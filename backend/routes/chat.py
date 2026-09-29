"""Chat routes — NutriPlan AI assistant chatbot.

Completely separate from the existing AI service / nutrition estimation.
Uses Ollama directly for general-purpose chat with a NutriPlan system prompt.
"""

from flask import Blueprint, request, jsonify, Response, stream_with_context
import json
import logging

from config import Config

logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__)

NUTRIPLAN_SYSTEM_PROMPT = (
    "You are NutriPlan AI, a friendly and knowledgeable assistant for NutriPlan — "
    "an institutional meal planning application used by college hostel mess managers.\n\n"
    "Your expertise includes:\n"
    "- Indian mess/hostel food planning and nutrition\n"
    "- Dietary guidelines for institutional feeding (500+ students)\n"
    "- Budget-aware meal planning for hostels\n"
    "- Nutrition information for common Indian foods\n"
    "- Food safety and storage best practices\n"
    "- Balancing cost, nutrition, and variety in weekly menus\n\n"
    "Guidelines:\n"
    "- Be concise and practical. Mess managers are busy.\n"
    "- Use Indian food names and ₹ for currency.\n"
    "- If asked about NutriPlan features, explain that the app handles: "
    "food inventory, weekly menu building, cost tracking, nutrition analysis, "
    "gap detection, and menu balancing.\n"
    "- Never make up specific prices or exact nutrition numbers unless you are "
    "reasonably confident. Say 'approximately' when estimating.\n"
    "- You are an assistant, not a medical professional. Recommend consulting "
    "a dietitian for clinical nutrition needs.\n"
    "- Keep responses under 150 words unless the user asks for detail."
)


@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    """Send a message to the NutriPlan AI assistant.

    Body: { "messages": [ { "role": "user", "content": "..." }, ... ] }

    Uses Ollama directly. Does not affect the existing AI service.
    """
    data = request.get_json() or {}
    messages = data.get("messages", [])

    if not messages:
        return jsonify({
            "success": False,
            "error": {"message": "messages array is required."}
        }), 400

    # Prepend the system prompt
    full_messages = [
        {"role": "system", "content": NUTRIPLAN_SYSTEM_PROMPT},
        *messages,
    ]

    # Read model from settings if available, otherwise use config default
    try:
        from services.nutrition_service import get_settings
        settings = get_settings()
        ai_config = settings.get("ai", {})
        provider = ai_config.get("provider", "ollama")
        model = ai_config.get("model", Config.OLLAMA_MODEL)

        # For chat, prefer Ollama. If user has Groq selected, still use Ollama for chat
        # since chat is meant to be local/free
        if provider == "groq":
            # Use Groq for chat too if that's what's configured
            return _chat_groq(full_messages, model)
        else:
            return _chat_ollama(full_messages, model)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({
            "success": False,
            "error": {"message": f"Chat is currently unavailable: {str(e)}"}
        }), 503


def _chat_ollama(messages: list, model: str):
    """Send chat to Ollama and stream the response."""
    try:
        import requests as req
        url = f"{Config.OLLAMA_BASE_URL}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.7},
        }
        resp = req.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        content = resp.json().get("message", {}).get("content", "")

        return jsonify({
            "success": True,
            "data": {
                "role": "assistant",
                "content": content,
                "provider": "ollama",
                "model": model,
            }
        })
    except Exception as e:
        logger.error(f"Ollama chat failed: {e}")
        return jsonify({
            "success": False,
            "error": {
                "message": f"Ollama is not reachable. Make sure Ollama is running. ({str(e)})"
            }
        }), 503


def _chat_groq(messages: list, model: str):
    """Send chat to Groq API."""
    if not Config.GROQ_API_KEY:
        return jsonify({
            "success": False,
            "error": {"message": "Groq API key not configured."}
        }), 503

    try:
        from groq import Groq
        client = Groq(api_key=Config.GROQ_API_KEY)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=512,
            timeout=10,
        )
        content = response.choices[0].message.content

        return jsonify({
            "success": True,
            "data": {
                "role": "assistant",
                "content": content,
                "provider": "groq",
                "model": model,
            }
        })
    except Exception as e:
        logger.error(f"Groq chat failed: {e}")
        return jsonify({
            "success": False,
            "error": {"message": f"Groq chat failed: {str(e)}"}
        }), 503
