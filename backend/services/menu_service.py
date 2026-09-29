"""Menu service — CRUD and food-ID collection for weekly menus."""

from bson import ObjectId
from database.mongodb import menus_collection
from models.menu import new_menu, serialize_menu, MEAL_SLOTS


def get_current_menu() -> dict | None:
    """Return the most recently created menu."""
    doc = menus_collection().find_one(sort=[("_id", -1)])
    return serialize_menu(doc)


def get_menu(menu_id: str) -> dict | None:
    """Return a menu by ID."""
    try:
        doc = menus_collection().find_one({"_id": ObjectId(menu_id)})
    except Exception:
        return None
    return serialize_menu(doc)


def create_menu(data: dict) -> dict:
    """Insert a new weekly menu."""
    doc = new_menu(data)
    result = menus_collection().insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc


def update_menu(menu_id: str, data: dict) -> dict | None:
    """Update an existing menu. Returns the updated document or None."""
    try:
        oid = ObjectId(menu_id)
    except Exception:
        return None

    update_fields = {}
    for field in ["weekStart", "peopleCount", "dailyBudget", "days"]:
        if field in data:
            update_fields[field] = data[field]

    if not update_fields:
        return get_menu(menu_id)

    menus_collection().update_one({"_id": oid}, {"$set": update_fields})
    return get_menu(menu_id)


def collect_food_ids(menu: dict) -> list[str]:
    """Extract all unique food IDs referenced by a menu."""
    ids = set()
    for day_entry in menu.get("days", []):
        for slot in MEAL_SLOTS:
            for fid in day_entry.get(slot, []):
                ids.add(str(fid))
    return list(ids)
