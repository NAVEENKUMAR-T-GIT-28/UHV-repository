"""Menu routes — CRUD for weekly meal plans."""

from flask import Blueprint, request, jsonify
from services import menu_service
from services.nutrition_service import compute_menu_summary
from utils.validation import validate_menu

menu_bp = Blueprint("menu", __name__)


@menu_bp.route("/api/menu", methods=["GET"])
def get_menu():
    """Get the current (latest) weekly menu with its computed summary."""
    menu = menu_service.get_current_menu()
    if menu is None:
        return jsonify({"success": True, "data": None, "message": "No menu found."})

    try:
        summary = compute_menu_summary(menu)
        return jsonify({"success": True, "data": {"menu": menu, "summary": summary}})
    except Exception as e:
        return jsonify({"success": True, "data": {"menu": menu, "summary": None, "error": str(e)}})


@menu_bp.route("/api/menu", methods=["POST"])
def create_menu():
    """Create a new weekly menu."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": {"message": "Request body is required."}}), 400

    errors = validate_menu(data)
    if errors:
        return jsonify({"success": False, "error": {"message": "Validation failed.", "details": errors}}), 400

    try:
        menu = menu_service.create_menu(data)
        summary = compute_menu_summary(menu)
        return jsonify({"success": True, "data": {"menu": menu, "summary": summary}}), 201
    except Exception as e:
        return jsonify({"success": False, "error": {"message": str(e)}}), 500


@menu_bp.route("/api/menu/<menu_id>", methods=["GET"])
def get_menu_by_id(menu_id):
    """Get a specific menu by ID with its computed summary."""
    menu = menu_service.get_menu(menu_id)
    if menu is None:
        return jsonify({"success": False, "error": {"message": "Menu not found."}}), 404

    try:
        summary = compute_menu_summary(menu)
        return jsonify({"success": True, "data": {"menu": menu, "summary": summary}})
    except Exception as e:
        return jsonify({"success": True, "data": {"menu": menu, "summary": None, "error": str(e)}})


@menu_bp.route("/api/menu/<menu_id>", methods=["PUT"])
def update_menu(menu_id):
    """Update a menu. Cost and nutrition are recalculated in Python."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": {"message": "Request body is required."}}), 400

    existing = menu_service.get_menu(menu_id)
    if existing is None:
        return jsonify({"success": False, "error": {"message": "Menu not found."}}), 404

    # If days are being updated, validate them
    if "days" in data:
        merged = {**existing, **data}
        errors = validate_menu(merged)
        if errors:
            return jsonify({"success": False, "error": {"message": "Validation failed.", "details": errors}}), 400

    try:
        updated = menu_service.update_menu(menu_id, data)
        if updated is None:
            return jsonify({"success": False, "error": {"message": "Menu not found."}}), 404
        summary = compute_menu_summary(updated)
        return jsonify({"success": True, "data": {"menu": updated, "summary": summary}})
    except Exception as e:
        return jsonify({"success": False, "error": {"message": str(e)}}), 500
