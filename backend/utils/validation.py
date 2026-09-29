"""Input validation helpers for food and menu data."""

from models.food import NUTRITION_FIELDS, VALID_NUTRITION_SOURCES
from models.menu import VALID_DAYS, MEAL_SLOTS


def validate_food(data: dict) -> list[str]:
    """Validate food item input. Returns a list of error messages (empty = valid)."""
    errors = []

    if not data.get("name") or not str(data["name"]).strip():
        errors.append("name is required.")

    if "servingSize" not in data or not isinstance(data["servingSize"], (int, float)):
        errors.append("servingSize must be a positive number.")
    elif data["servingSize"] <= 0:
        errors.append("servingSize must be a positive number.")

    if not data.get("unit") or not str(data["unit"]).strip():
        errors.append("unit is required.")

    if "price" not in data or not isinstance(data["price"], (int, float)):
        errors.append("price must be a non-negative number.")
    elif data["price"] < 0:
        errors.append("price must not be negative.")

    if "availableQuantity" in data:
        qty = data["availableQuantity"]
        if not isinstance(qty, (int, float)) or qty < 0:
            errors.append("availableQuantity must be a non-negative number.")

    # Nutrition validation
    nutrition = data.get("nutrition", {})
    if nutrition:
        for field in NUTRITION_FIELDS:
            val = nutrition.get(field)
            if val is not None:
                if not isinstance(val, (int, float)):
                    errors.append(f"nutrition.{field} must be a number.")
                elif val < 0:
                    errors.append(f"nutrition.{field} must not be negative.")

    # Nutrition source
    src = data.get("nutritionSource")
    if src and src not in VALID_NUTRITION_SOURCES:
        errors.append(f"nutritionSource must be one of: {VALID_NUTRITION_SOURCES}")

    return errors


def validate_menu(data: dict) -> list[str]:
    """Validate menu input. Returns a list of error messages (empty = valid)."""
    errors = []

    if not data.get("weekStart"):
        errors.append("weekStart is required.")

    if "peopleCount" in data:
        pc = data["peopleCount"]
        if not isinstance(pc, (int, float)) or pc <= 0:
            errors.append("peopleCount must be a positive number.")

    if "dailyBudget" in data:
        db = data["dailyBudget"]
        if not isinstance(db, (int, float)) or db <= 0:
            errors.append("dailyBudget must be a positive number.")

    days = data.get("days", [])
    if not days:
        errors.append("days is required and must contain at least one day.")
    else:
        if len(days) != 7:
            errors.append("A weekly menu must have exactly 7 days.")

        seen_days = set()
        for i, day_entry in enumerate(days):
            day_name = day_entry.get("day")
            if not day_name or day_name not in VALID_DAYS:
                errors.append(
                    f"days[{i}].day must be one of: {VALID_DAYS}"
                )
            elif day_name in seen_days:
                errors.append(f"Duplicate day: {day_name}")
            else:
                seen_days.add(day_name)

            for slot in MEAL_SLOTS:
                food_ids = day_entry.get(slot, [])
                if not isinstance(food_ids, list):
                    errors.append(f"days[{i}].{slot} must be a list of food IDs.")

    return errors


def validate_nutrition_response(data: dict) -> list[str]:
    """Validate an AI-returned nutrition estimate."""
    errors = []

    if not isinstance(data, dict):
        errors.append("AI response must be a JSON object.")
        return errors

    for field in NUTRITION_FIELDS:
        val = data.get(field)
        if val is None:
            errors.append(f"Missing nutrition field: {field}")
        elif not isinstance(val, (int, float)):
            errors.append(f"nutrition.{field} must be a number, got {type(val).__name__}")
        elif val < 0:
            errors.append(f"nutrition.{field} must not be negative.")

    return errors
