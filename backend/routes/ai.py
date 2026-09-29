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
    except Exception as e:
        return jsonify({"success": False, "error": {"message": str(e)}}), 500


@ai_bp.route("/api/health", methods=["GET"])
def health():
    """Liveness check."""
    return jsonify({"success": True, "data": {"status": "healthy", "service": "NutriPlan API"}})
