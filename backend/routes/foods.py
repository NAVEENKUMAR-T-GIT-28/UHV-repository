"""Food items CRUD routes."""

from flask import Blueprint, request, jsonify
from services import food_service
from utils.validation import validate_food

foods_bp = Blueprint("foods", __name__)


@foods_bp.route("/api/foods", methods=["GET"])
def list_foods():
    """List all food items."""
    try:
        foods = food_service.list_foods()
        return jsonify({"success": True, "data": foods})
    except Exception as e:
        return jsonify({"success": False, "error": {"message": str(e)}}), 500


@foods_bp.route("/api/foods", methods=["POST"])
def create_food():
    """Create a new food item."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": {"message": "Request body is required."}}), 400

    errors = validate_food(data)
    if errors:
        return jsonify({"success": False, "error": {"message": "Validation failed.", "details": errors}}), 400

    try:
        food = food_service.create_food(data)
        return jsonify({"success": True, "data": food}), 201
    except Exception as e:
        return jsonify({"success": False, "error": {"message": str(e)}}), 500


@foods_bp.route("/api/foods/<food_id>", methods=["GET"])
def get_food(food_id):
    """Get a single food item by ID."""
    food = food_service.get_food(food_id)
    if food is None:
        return jsonify({"success": False, "error": {"message": "Food not found."}}), 404
    return jsonify({"success": True, "data": food})


@foods_bp.route("/api/foods/<food_id>", methods=["PUT"])
def update_food(food_id):
    """Update a food item."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": {"message": "Request body is required."}}), 400

    # Partial validation — only check provided fields
    existing = food_service.get_food(food_id)
    if existing is None:
        return jsonify({"success": False, "error": {"message": "Food not found."}}), 404

    # Merge for validation purposes
    merged = {**existing, **data}
    if "nutrition" in data:
        merged["nutrition"] = {**existing.get("nutrition", {}), **data["nutrition"]}

    errors = validate_food(merged)
    if errors:
        return jsonify({"success": False, "error": {"message": "Validation failed.", "details": errors}}), 400

    try:
        updated = food_service.update_food(food_id, data)
        if updated is None:
            return jsonify({"success": False, "error": {"message": "Food not found."}}), 404
        return jsonify({"success": True, "data": updated})
    except Exception as e:
        return jsonify({"success": False, "error": {"message": str(e)}}), 500


@foods_bp.route("/api/foods/<food_id>", methods=["DELETE"])
def delete_food(food_id):
    """Delete a food item."""
    deleted = food_service.delete_food(food_id)
    if not deleted:
        return jsonify({"success": False, "error": {"message": "Food not found."}}), 404
    return jsonify({"success": True, "data": {"message": "Food deleted."}})
