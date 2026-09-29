"""Analyzer service — evaluate a menu and optionally add AI explanation."""

from services.menu_service import get_menu, collect_food_ids
from services.food_service import get_foods_by_ids
from services.nutrition_service import compute_menu_summary, get_settings
from services import ai_service
from models.menu import MEAL_SLOTS


def analyze_menu(menu_id: str, explain: bool = False) -> dict:
    """Analyze a menu: compute cost, nutrition, coverage, gaps.

    All numbers are deterministic Python calculations.
    AI is only used for the optional explanation.
    """
    menu = get_menu(menu_id)
    if menu is None:
        return {"error": "Menu not found"}

    summary = compute_menu_summary(menu)

    # Identify top contributors per nutrient
    settings = get_settings()
    food_ids = collect_food_ids(menu)
    foods_by_id = get_foods_by_ids(food_ids)
    contributors = _find_contributors(menu, foods_by_id)
    summary["contributors"] = contributors

    # Optional AI explanation
    if explain:
        explanation_input = {
            "coverage": summary.get("coverage", {}),
            "gaps": summary.get("gaps", []),
            "cost": summary.get("cost", {}),
            "availableFoods": [f["name"] for f in foods_by_id.values()],
        }
        ai_resp = ai_service.explain_analysis(explanation_input)
        summary["aiExplanation"] = ai_resp.get("text") if ai_resp else None
    else:
        summary["aiExplanation"] = None

    return summary


def _find_contributors(menu: dict, foods_by_id: dict) -> dict:
    """Find which foods contribute most to each nutrient."""
    from models.food import NUTRITION_FIELDS
    from utils.calculations import NUTRITION_TO_TARGET

    # Accumulate per-food nutrition totals across the week
    food_totals = {}  # food_id -> {field: total}
    for day_entry in menu.get("days", []):
        for slot in MEAL_SLOTS:
            for fid in day_entry.get(slot, []):
                fid_str = str(fid)
                food = foods_by_id.get(fid_str)
                if not food:
                    continue
                if fid_str not in food_totals:
                    food_totals[fid_str] = {
                        "name": food["name"],
                        **{f: 0.0 for f in NUTRITION_FIELDS},
                    }
                for field in NUTRITION_FIELDS:
                    food_totals[fid_str][field] += food.get("nutrition", {}).get(field, 0)

    # For each nutrient, find top 3 contributing foods
    contributors = {}
    for food_field, target_key in NUTRITION_TO_TARGET.items():
        ranked = sorted(
            food_totals.values(),
            key=lambda ft: ft.get(food_field, 0),
            reverse=True,
        )
        contributors[target_key] = [
            {"name": ft["name"], "value": round(ft[food_field], 2)}
            for ft in ranked[:3]
        ]

    return contributors
