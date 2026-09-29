"""AI routes — nutrition estimation and settings endpoints."""

from flask import Blueprint, request, jsonify
from services import ai_service
from services.nutrition_service import get_settings, update_settings
from utils.validation import validate_nutrition_response

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/api/foods/analyze-nutrition", methods=["POST"])
def analyze_nutrition():
    """Ask AI to estimate nutrition for a food item.

    Body: { "name": "...", "servingSize": 100, "unit": "g" }

    The backend validates the AI response before returning it.
    """
    data = request.get_json() or {}
    name = data.get("name")
    serving_size = data.get("servingSize")
    unit = data.get("unit")

    if not name or not serving_size or not unit:
        return jsonify({
            "success": False,
            "error": {"message": "name, servingSize, and unit are required."}
        }), 400

    # Call AI service (Groq → Ollama → None)
    result = ai_service.estimate_nutrition(name, serving_size, unit)

    if result is None:
        return jsonify({
            "success": False,
            "error": {
                "message": "AI nutrition estimation is currently unavailable. "
                           "Please enter nutrition values manually."
            }
        }), 503

    # Validate the AI response
    errors = validate_nutrition_response(result)
    if errors:
        return jsonify({
            "success": False,
            "error": {
                "message": "AI returned invalid nutrition data.",
                "details": errors,
            }
        }), 502

    return jsonify({
        "success": True,
        "data": {
            "nutrition": result,
            "source": "ai_estimate",
            "disclaimer": "AI-estimated nutrition — verify before operational use.",
        }
    })


# ───── Settings routes (co-located since they're small) ─────

@ai_bp.route("/api/settings", methods=["GET"])
def get_settings_route():
    """Get current institution settings and nutrition targets."""
    try:
        settings = get_settings()
        return jsonify({"success": True, "data": settings})
    except Exception as e:
        return jsonify({"success": False, "error": {"message": str(e)}}), 500


@ai_bp.route("/api/settings", methods=["PUT"])
def update_settings_route():
    """Update institution settings."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": {"message": "Request body is required."}}), 400

    try:
        settings = update_settings(data)
        return jsonify({"success": True, "data": settings})
    except ValueError as e:
        return jsonify({"success": False, "error": {"message": str(e)}}), 400
    except Exception as e:
        return jsonify({"success": False, "error": {"message": str(e)}}), 500


@ai_bp.route("/api/ai/models", methods=["GET"])
def list_models():
    """List available models for a given AI provider.

    Query: ?provider=groq|ollama

    For Ollama, queries the local server's /api/tags endpoint.
    For Groq, returns a curated list of known-available models.
    """
    provider = request.args.get("provider", "groq")

    if provider == "ollama":
        try:
            import requests as req
            from config import Config
            resp = req.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            resp.raise_for_status()
            raw_models = resp.json().get("models", [])
            models = [m["name"] for m in raw_models]
            return jsonify({
                "success": True,
                "data": {
                    "provider": "ollama",
                    "models": models,
                    "source": "live",
                }
            })
        except Exception as e:
            return jsonify({
                "success": True,
                "data": {
                    "provider": "ollama",
                    "models": [],
                    "source": "error",
                    "error": f"Could not reach Ollama: {e}",
                }
            })

    elif provider == "groq":
        # Curated list of stable Groq-hosted models
        groq_models = [
            "llama3-8b-8192",
            "llama3-70b-8192",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ]
        return jsonify({
            "success": True,
            "data": {
                "provider": "groq",
                "models": groq_models,
                "source": "curated",
            }
        })

    else:
        return jsonify({
            "success": False,
            "error": {"message": f"Unknown provider: {provider}"}
        }), 400


@ai_bp.route("/api/health", methods=["GET"])
def health():
    """Liveness check."""
    return jsonify({"success": True, "data": {"status": "healthy", "service": "NutriPlan API"}})
