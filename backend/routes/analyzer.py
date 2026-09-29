"""Analyzer routes — evaluate a menu's nutrition and cost."""

from flask import Blueprint, request, jsonify
from services import analyzer_service

analyzer_bp = Blueprint("analyzer", __name__)


@analyzer_bp.route("/api/analyze", methods=["POST"])
def analyze():
    """Analyze a menu: compute cost, nutrition, coverage, gaps.

    Body: { "menuId": "...", "explain": true/false }

    All numeric values come from Python calculations.
    If explain=true, an AI explanation is appended (or a template fallback).
    """
    data = request.get_json() or {}
    menu_id = data.get("menuId")
    explain = data.get("explain", False)

    if not menu_id:
        return jsonify({"success": False, "error": {"message": "menuId is required."}}), 400

    result = analyzer_service.analyze_menu(menu_id, explain=explain)

    if "error" in result:
        return jsonify({"success": False, "error": {"message": result["error"]}}), 404

    return jsonify({"success": True, "data": result})
