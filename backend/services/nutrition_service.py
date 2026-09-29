"""Nutrition service — bridges menu data with calculation utilities."""

from services.food_service import get_foods_by_ids
from services.menu_service import get_menu, collect_food_ids
from utils.calculations import calculate_menu_summary


def get_settings() -> dict:
    """Load the current settings from the database."""
    from database.mongodb import settings_collection
    doc = settings_collection().find_one({"_id": "default"})
    if doc is None:
        from models.settings import DEFAULT_SETTINGS
        settings_collection().insert_one(DEFAULT_SETTINGS.copy())
        doc = settings_collection().find_one({"_id": "default"})
    doc["_id"] = str(doc["_id"])
    if "ai" not in doc:
        from models.settings import DEFAULT_SETTINGS
        doc["ai"] = DEFAULT_SETTINGS["ai"]
    return doc


def update_settings(data: dict) -> dict:
    """Update institution settings."""
    from database.mongodb import settings_collection
    update_fields = {}
    for field in ["peopleCount", "dailyBudget", "kitchenCapacity",
                   "dietaryRequirements", "nutritionTargets", "ai"]:
        if field in data:
            if field == "ai":
                ai_data = data["ai"]
                provider = ai_data.get("provider")
                model = ai_data.get("model")
                if provider not in ["groq", "ollama"]:
                    raise ValueError(f"Invalid AI provider: {provider}")
                if not model:
                    raise ValueError("AI model is required.")
            update_fields[field] = data[field]
    if update_fields:
        settings_collection().update_one(
            {"_id": "default"}, {"$set": update_fields}, upsert=True
        )
    return get_settings()


def compute_menu_summary(menu: dict) -> dict:
    """Compute the full cost + nutrition summary for a given menu document."""
    settings = get_settings()

    food_ids = collect_food_ids(menu)
    foods_by_id = get_foods_by_ids(food_ids)

    return calculate_menu_summary(
        menu_days=menu.get("days", []),
        foods_by_id=foods_by_id,
        people_count=menu.get("peopleCount", settings.get("peopleCount", 500)),
        daily_budget=menu.get("dailyBudget", settings.get("dailyBudget", 18000)),
        nutrition_targets=settings.get("nutritionTargets", {}),
    )
