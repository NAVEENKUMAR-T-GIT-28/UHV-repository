"""Food service — CRUD operations for food items."""

from bson import ObjectId
from database.mongodb import foods_collection
from models.food import new_food, serialize_food


def list_foods(filters: dict | None = None) -> list[dict]:
    """Return all food items, optionally filtered."""
    query = filters or {}
    docs = foods_collection().find(query)
    return [serialize_food(doc) for doc in docs]


def get_food(food_id: str) -> dict | None:
    """Return a single food item by ID."""
    try:
        doc = foods_collection().find_one({"_id": ObjectId(food_id)})
    except Exception:
        return None
    return serialize_food(doc)


def create_food(data: dict) -> dict:
    """Insert a new food item and return it."""
    doc = new_food(data)
    result = foods_collection().insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc


def update_food(food_id: str, data: dict) -> dict | None:
    """Update an existing food item. Returns the updated document or None."""
    try:
        oid = ObjectId(food_id)
    except Exception:
        return None

    # Build update fields (only provided fields)
    update_fields = {}
    direct_fields = [
        "name", "category", "servingSize", "unit", "price",
        "availableQuantity", "dietaryTags", "nutritionSource",
    ]
    for field in direct_fields:
        if field in data:
            update_fields[field] = data[field]

    if "nutrition" in data:
        from models.food import NUTRITION_FIELDS
        for nf in NUTRITION_FIELDS:
            if nf in data["nutrition"]:
                update_fields[f"nutrition.{nf}"] = data["nutrition"][nf]

    if not update_fields:
        return get_food(food_id)

    foods_collection().update_one({"_id": oid}, {"$set": update_fields})
    return get_food(food_id)


def delete_food(food_id: str) -> bool:
    """Delete a food item. Returns True if deleted."""
    try:
        result = foods_collection().delete_one({"_id": ObjectId(food_id)})
        return result.deleted_count > 0
    except Exception:
        return False


def get_foods_by_ids(food_ids: list[str]) -> dict:
    """Return a dict of {str_id: food_doc} for a list of food IDs."""
    oids = []
    for fid in food_ids:
        try:
            oids.append(ObjectId(fid))
        except Exception:
            continue

    docs = foods_collection().find({"_id": {"$in": oids}})
    return {str(doc["_id"]): serialize_food(doc) for doc in docs}
