"""Balancer routes — generate and apply budget-aware meal suggestions."""

from flask import Blueprint, request, jsonify
from services import balancer_service
from services import ai_service

balancer_bp = Blueprint("balancer", __name__)


@balancer_bp.route("/api/balance", methods=["POST"])
def balance():
    """Generate meal-swap suggestions for a menu.

    Body: { "menuId": "...", "priority": "iron" (optional) }

    All ranking is deterministic Python. AI only explains the suggestions.
    """
    data = request.get_json() or {}
    menu_id = data.get("menuId")
    priority = data.get("priority")

    if not menu_id:
        return jsonify({"success": False, "error": {"message": "menuId is required."}}), 400

    result = balancer_service.generate_suggestions(menu_id, priority_nutrient=priority)

    if "error" in result:
        return jsonify({"success": False, "error": {"message": result["error"]}}), 404

    # Optionally add AI explanations for top suggestions
    if data.get("explain", False) and result.get("suggestions"):
        for s in result["suggestions"][:3]:
            s["aiExplanation"] = ai_service.explain_balancer_suggestion(s)

    return jsonify({"success": True, "data": result})


@balancer_bp.route("/api/balance/apply", methods=["POST"])
def apply_balance():
    """Apply a single balancer suggestion to the menu.

    Body: { "menuId": "...", "suggestion": { day, meal, currentFoodId, suggestedFoodId, ... } }

    The backend re-validates everything from the database before applying.
    """
    data = request.get_json() or {}
    menu_id = data.get("menuId")
    suggestion = data.get("suggestion")

    if not menu_id:
        return jsonify({"success": False, "error": {"message": "menuId is required."}}), 400
    if not suggestion:
        return jsonify({"success": False, "error": {"message": "suggestion is required."}}), 400

    result = balancer_service.apply_suggestion(menu_id, suggestion)

    if "error" in result:
        status_code = 400 if "not found" not in result["error"].lower() else 404
        return jsonify({"success": False, "error": {"message": result["error"]}}), status_code

    return jsonify({"success": True, "data": result})
