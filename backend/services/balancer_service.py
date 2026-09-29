"""Balancer service — deterministic budget-aware meal replacement suggestions.

For every candidate swap the balancer:
1. Creates a temporary menu copy.
2. Calculates new cost (Python).
3. Calculates new nutrition (Python).
4. Checks budget, dietary requirements, availability.
5. Ranks by improvement.

The AI never selects the replacement — it only explains the suggestion afterward.
"""

import copy
from services.menu_service import get_menu, collect_food_ids, update_menu
from services.food_service import get_foods_by_ids, list_foods
from services.nutrition_service import compute_menu_summary, get_settings
from services import ai_service
from models.menu import MEAL_SLOTS
from utils.calculations import (
    nutrition_coverage,
    identify_gaps,
    daily_nutrition_per_person,
    NUTRITION_TO_TARGET,
)


def generate_suggestions(menu_id: str, priority_nutrient: str | None = None) -> dict:
    """Generate ranked meal-swap suggestions for the given menu.

    Args:
        menu_id: the menu to improve
        priority_nutrient: which nutrient to optimize (e.g. "iron")
                           If None, targets the worst gap automatically.

    Returns:
        dict with status and ranked suggestions.
    """
    menu = get_menu(menu_id)
    if menu is None:
        return {"error": "Menu not found"}

    settings = get_settings()
    people_count = menu.get("peopleCount", settings.get("peopleCount", 500))
    daily_budget = menu.get("dailyBudget", settings.get("dailyBudget", 18000))
    targets = settings.get("nutritionTargets", {})
    dietary_reqs = set(settings.get("dietaryRequirements", []))

    # Current summary
    current_summary = compute_menu_summary(menu)
    current_gaps = current_summary.get("gaps", [])

    if not current_gaps and priority_nutrient is None:
        return {
            "status": "no_gaps",
            "message": "All nutrition targets are currently met.",
            "suggestions": [],
        }

    # Determine which nutrient to improve
    if priority_nutrient:
        target_nutrient = priority_nutrient
    else:
        target_nutrient = current_gaps[0]["nutrient"]  # worst gap

    # All available foods
    all_foods = list_foods({"availableQuantity": {"$gt": 0}})
    food_ids = collect_food_ids(menu)
    foods_by_id = get_foods_by_ids(food_ids)

    # Build a lookup for all foods
    all_foods_by_id = {f["_id"]: f for f in all_foods}

    suggestions = []

    # Try swapping each food in each slot of each day
    for day_idx, day_entry in enumerate(menu.get("days", [])):
        day_name = day_entry.get("day", f"Day {day_idx + 1}")

        for slot in MEAL_SLOTS:
            current_food_ids = day_entry.get(slot, [])

            for food_idx, current_fid in enumerate(current_food_ids):
                current_food = foods_by_id.get(str(current_fid))
                if not current_food:
                    continue

                # Try every available replacement food
                for candidate in all_foods:
                    candidate_id = candidate["_id"]

                    # Skip self
                    if candidate_id == str(current_fid):
                        continue

                    # Check dietary compatibility
                    candidate_tags = set(candidate.get("dietaryTags", []))
                    if dietary_reqs and not dietary_reqs.issubset(candidate_tags):
                        continue

                    # Check availability
                    if candidate.get("availableQuantity", 0) <= 0:
                        continue

                    # Create temporary menu with the swap
                    temp_menu = copy.deepcopy(menu)
                    temp_day = temp_menu["days"][day_idx]
                    temp_slot_foods = list(temp_day.get(slot, []))
                    temp_slot_foods[food_idx] = candidate_id
                    temp_day[slot] = temp_slot_foods

                    # Calculate new summary
                    # We need foods_by_id to include the candidate
                    temp_food_ids = collect_food_ids(temp_menu)
                    temp_foods_by_id = get_foods_by_ids(temp_food_ids)

                    temp_summary = _quick_summary(
                        temp_menu, temp_foods_by_id, people_count, daily_budget, targets
                    )

                    # Check budget
                    temp_cost = temp_summary["cost"]
                    budget_valid = temp_cost["withinBudget"]

                    # Calculate improvement for the target nutrient
                    old_coverage = current_summary.get("coverage", {}).get(target_nutrient, 0)
                    new_coverage = temp_summary.get("coverage", {}).get(target_nutrient, 0)
                    improvement = round(new_coverage - old_coverage, 1)

                    if improvement <= 0:
                        continue  # no improvement — skip

                    # Cost difference per person per day
                    old_cost_pp = current_summary["cost"].get("perPerson", 0)
                    new_cost_pp = temp_cost.get("perPerson", 0)
                    additional_cost = round(
                        (new_cost_pp - old_cost_pp) * people_count, 2
                    )

                    suggestions.append({
                        "day": day_name,
                        "meal": slot,
                        "currentFood": current_food.get("name", "Unknown"),
                        "currentFoodId": str(current_fid),
                        "suggestedFood": candidate.get("name", "Unknown"),
                        "suggestedFoodId": candidate_id,
                        "additionalCost": additional_cost,
                        "nutritionImprovement": {
                            "nutrient": target_nutrient,
                            "percentage": improvement,
                        },
                        "budgetValid": budget_valid,
                        "dietValid": True,
                        "availabilityValid": True,
                        "newCoverage": temp_summary.get("coverage", {}),
                    })

    # Rank: best improvement per ₹ first, then by raw improvement
    suggestions.sort(
        key=lambda s: (
            -s["nutritionImprovement"]["percentage"],
            s["additionalCost"],
        )
    )

    # Take top 10
    top_suggestions = suggestions[:10]

    return {
        "status": "suggestions_available" if top_suggestions else "no_improvements",
        "targetNutrient": target_nutrient,
        "currentCoverage": current_summary.get("coverage", {}),
        "suggestions": top_suggestions,
    }


def apply_suggestion(menu_id: str, suggestion: dict) -> dict:
    """Apply a single swap suggestion to a menu.

    Re-validates everything from the database before applying.
    Never blindly trusts the frontend payload.
    """
    menu = get_menu(menu_id)
    if menu is None:
        return {"error": "Menu not found"}

    settings = get_settings()
    people_count = menu.get("peopleCount", settings.get("peopleCount", 500))
    daily_budget = menu.get("dailyBudget", settings.get("dailyBudget", 18000))
    targets = settings.get("nutritionTargets", {})
    dietary_reqs = set(settings.get("dietaryRequirements", []))

    day_name = suggestion.get("day")
    slot = suggestion.get("meal")
    current_food_id = suggestion.get("currentFoodId")
    suggested_food_id = suggestion.get("suggestedFoodId")

    if not all([day_name, slot, current_food_id, suggested_food_id]):
        return {"error": "Missing required suggestion fields (day, meal, currentFoodId, suggestedFoodId)."}

    if slot not in MEAL_SLOTS:
        return {"error": f"Invalid meal slot: {slot}"}

    # Re-load suggested food from DB to verify it exists and is available
    from services.food_service import get_food
    suggested_food = get_food(suggested_food_id)
    if not suggested_food:
        return {"error": f"Suggested food not found: {suggested_food_id}"}

    if suggested_food.get("availableQuantity", 0) <= 0:
        return {"error": f"Suggested food is not available: {suggested_food['name']}"}

    # Check dietary compatibility
    candidate_tags = set(suggested_food.get("dietaryTags", []))
    if dietary_reqs and not dietary_reqs.issubset(candidate_tags):
        return {"error": f"Suggested food does not meet dietary requirements."}

    # Find the day and slot in the menu, apply the swap
    updated_days = copy.deepcopy(menu["days"])
    found = False
    for day_entry in updated_days:
        if day_entry.get("day") == day_name:
            slot_foods = day_entry.get(slot, [])
            for i, fid in enumerate(slot_foods):
                if str(fid) == str(current_food_id):
                    slot_foods[i] = suggested_food_id
                    found = True
                    break
            day_entry[slot] = slot_foods
            break

    if not found:
        return {"error": f"Current food {current_food_id} not found in {day_name} {slot}."}

    # Verify budget with the new menu before saving
    temp_menu = copy.deepcopy(menu)
    temp_menu["days"] = updated_days
    temp_food_ids = collect_food_ids(temp_menu)
    temp_foods_by_id = get_foods_by_ids(temp_food_ids)

    temp_summary = _quick_summary(
        temp_menu, temp_foods_by_id, people_count, daily_budget, targets
    )

    if not temp_summary["cost"]["withinBudget"]:
        return {
            "error": "Applying this suggestion would exceed the daily budget.",
            "newCost": temp_summary["cost"],
        }

    # All checks passed — save
    updated_menu = update_menu(menu_id, {"days": updated_days})

    # Return the newly calculated summary
    new_summary = compute_menu_summary(updated_menu)
    new_summary["appliedSwap"] = {
        "day": day_name,
        "meal": slot,
        "from": suggestion.get("currentFood"),
        "to": suggested_food.get("name"),
    }

    return new_summary


def _quick_summary(menu, foods_by_id, people_count, daily_budget, targets):
    """Compute a cost/nutrition summary using the calculation utilities directly."""
    from utils.calculations import calculate_menu_summary
    return calculate_menu_summary(
        menu_days=menu.get("days", []),
        foods_by_id=foods_by_id,
        people_count=people_count,
        daily_budget=daily_budget,
        nutrition_targets=targets,
    )
