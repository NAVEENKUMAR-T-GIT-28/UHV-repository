"""AI service — unified abstraction over Groq and Ollama.

Architecture:
    AIService
       ├── GroqProvider   (primary)
       └── OllamaProvider (fallback)

The rest of the backend calls ai_service functions and never cares
which provider actually generated the response.
"""

import json
import logging
import re

from config import Config

logger = logging.getLogger(__name__)

# ──────────────── Centralized prompts ────────────────

NUTRITION_SYSTEM_PROMPT = (
    "You are NutriPlan's nutrition estimation assistant.\n\n"
    "Estimate nutritional composition for the supplied food and serving size.\n\n"
    "Return ONLY valid JSON using the requested schema.\n"
    "Do not include explanations outside the JSON.\n"
    "Do not invent the serving size.\n\n"
    "The result is an estimate and must not be presented as a medical or clinical "
    "nutrition assessment."
)

EXPLANATION_SYSTEM_PROMPT = (
    "You are NutriPlan's meal-plan explanation assistant for an institutional "
    "mess manager.\n\n"
    "Explain the supplied analysis result in simple, plain language, in at most "
    "120 words.\n\n"
    "Use ONLY the numbers and food names present in the supplied JSON.\n"
    "Do NOT create, modify, validate or recommend meals.\n"
    "Do NOT calculate or invent nutrition values, prices, ingredients or constraints.\n"
    "You may only mention suggestions that appear in the input.\n\n"
    "If a nutrient is below 100%, state it clearly. Never describe such a plan as "
    "fully meeting targets.\n"
    "Do not use markdown formatting."
)

BALANCER_EXPLANATION_PROMPT = (
    "You are NutriPlan's meal-plan explanation assistant.\n\n"
    "Explain WHY the suggested food swap makes sense, in at most 80 words.\n"
    "Use ONLY the numbers provided. Do not invent data.\n"
    "Do not use markdown formatting."
)


# ──────────────── Provider implementations ────────────────

def _call_groq(messages: list[dict], temperature: float = 0.3, timeout: int = 8) -> str | None:
    """Call the Groq API. Returns the response text or None on failure."""
    if not Config.GROQ_API_KEY:
        logger.warning("Groq API key not configured — skipping Groq.")
        return None
    try:
        from groq import Groq
        client = Groq(api_key=Config.GROQ_API_KEY)
        response = client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=512,
            timeout=timeout,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq call failed: {e}")
        return None


def _call_ollama(messages: list[dict], temperature: float = 0.3, timeout: int = 15) -> str | None:
    """Call the Ollama HTTP API. Returns the response text or None on failure."""
    try:
        import requests
        url = f"{Config.OLLAMA_BASE_URL}/api/chat"
        payload = {
            "model": Config.OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "")
    except Exception as e:
        logger.error(f"Ollama call failed: {e}")
        return None


def _call_ai(messages: list[dict], temperature: float = 0.3) -> str | None:
    """Try primary provider, then fallback. Returns response text or None."""
    providers = {
        "groq": _call_groq,
        "ollama": _call_ollama,
    }

    # Try primary
    primary = providers.get(Config.AI_PRIMARY_PROVIDER)
    if primary:
        result = primary(messages, temperature)
        if result:
            return result

    # Try fallback
    fallback = providers.get(Config.AI_FALLBACK_PROVIDER)
    if fallback and fallback != primary:
        result = fallback(messages, temperature)
        if result:
            return result

    return None


def _extract_json(text: str) -> dict | None:
    """Extract and parse a JSON object from AI response text."""
    if not text:
        return None
    # Try parsing directly first
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try extracting from ```json ... ``` code block
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    # Try finding the first { ... }
    match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


# ──────────────── Public API ────────────────

def estimate_nutrition(food_name: str, serving_size: float, unit: str) -> dict | None:
    """Ask AI to estimate nutrition for a food item.

    Returns a dict with nutrition fields, or None if AI is unavailable.
    The caller MUST validate the returned dict before trusting it.
    """
    user_prompt = (
        f"Estimate the nutritional composition of \"{food_name}\" "
        f"for a serving size of {serving_size} {unit}.\n\n"
        "Return ONLY a JSON object with these exact keys:\n"
        "{\n"
        '  "calories": <number>,\n'
        '  "protein": <number in grams>,\n'
        '  "carbohydrates": <number in grams>,\n'
        '  "fat": <number in grams>,\n'
        '  "fiber": <number in grams>,\n'
        '  "iron": <number in mg>,\n'
        '  "calcium": <number in mg>\n'
        "}\n\n"
        "Return ONLY the JSON. No explanations."
    )

    messages = [
        {"role": "system", "content": NUTRITION_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    response_text = _call_ai(messages, temperature=0.2)
    return _extract_json(response_text)


def explain_analysis(analysis_data: dict) -> dict:
    """Ask AI to explain a nutrition analysis result.

    Returns {text: str, source: "ai" | "fallback"}.
    """
    user_prompt = (
        "Explain this nutrition analysis result in simple language:\n\n"
        f"{json.dumps(analysis_data, indent=2)}"
    )

    messages = [
        {"role": "system", "content": EXPLANATION_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    response_text = _call_ai(messages, temperature=0.3)

    if response_text:
        return {"text": response_text.strip(), "source": "ai"}

    # Deterministic fallback
    return _template_explanation(analysis_data)


def explain_balancer_suggestion(suggestion_data: dict) -> dict:
    """Ask AI to explain a balancer suggestion.

    Returns {text: str, source: "ai" | "fallback"}.
    """
    user_prompt = (
        "Explain this food swap suggestion in simple language:\n\n"
        f"{json.dumps(suggestion_data, indent=2)}"
    )

    messages = [
        {"role": "system", "content": BALANCER_EXPLANATION_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    response_text = _call_ai(messages, temperature=0.3)

    if response_text:
        return {"text": response_text.strip(), "source": "ai"}

    # Deterministic fallback
    return _template_balancer_explanation(suggestion_data)


# ──────────────── Template fallbacks ────────────────

def _template_explanation(analysis: dict) -> dict:
    """Generate a deterministic explanation when AI is unavailable."""
    gaps = analysis.get("gaps", [])
    coverage = analysis.get("coverage", {})
    cost = analysis.get("cost", {})

    parts = []

    if cost.get("withinBudget") is False:
        parts.append(
            f"The current menu costs ₹{cost.get('daily', 0):,.0f}/day, "
            f"which is ₹{cost.get('overBy', 0):,.0f} over the daily budget of "
            f"₹{cost.get('dailyBudget', 0):,.0f}."
        )

    if gaps:
        gap_strs = [
            f"{g['nutrient']} at {g['coverage']}%"
            for g in gaps
        ]
        parts.append(
            f"Your current menu is below target for: {', '.join(gap_strs)}. "
            "Consider available nutrient-rich food options while keeping the "
            "current budget in mind."
        )
    else:
        parts.append("All tracked nutrition targets are currently met.")

    return {"text": " ".join(parts), "source": "fallback"}


def _template_balancer_explanation(suggestion: dict) -> dict:
    """Generate a deterministic balancer explanation when AI is unavailable."""
    current = suggestion.get("currentFood", "the current food")
    suggested = suggestion.get("suggestedFood", "the suggested food")
    improvement = suggestion.get("nutritionImprovement", {})
    nutrient = improvement.get("nutrient", "the target nutrient")
    pct = improvement.get("percentage", 0)
    cost = suggestion.get("additionalCost", 0)

    text = (
        f"Replacing {current} with {suggested} improves {nutrient} coverage "
        f"by {pct}%"
    )
    if cost > 0:
        text += f" for an additional ₹{cost:,.0f}"
    elif cost < 0:
        text += f" while saving ₹{abs(cost):,.0f}"
    text += "."

    return {"text": text, "source": "fallback"}
