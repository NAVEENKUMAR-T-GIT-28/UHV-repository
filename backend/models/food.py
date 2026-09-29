"""Food model — schema definition and serialization helpers."""

NUTRITION_FIELDS = [
    "calories", "protein", "carbohydrates", "fat", "fiber", "iron", "calcium"
]

VALID_NUTRITION_SOURCES = ["ai_estimate", "manual", "sample"]


def new_food(data: dict) -> dict:
    """Build a clean food document from validated input data."""
    nutrition = data.get("nutrition", {})
    return {
        "name": data["name"],
        "category": data.get("category", "General"),
        "servingSize": data["servingSize"],
        "unit": data["unit"],
        "price": data["price"],
        "availableQuantity": data.get("availableQuantity", 0),
        "dietaryTags": data.get("dietaryTags", ["vegetarian"]),
        "nutrition": {field: nutrition.get(field, 0) for field in NUTRITION_FIELDS},
        "nutritionSource": data.get("nutritionSource", "manual"),
    }


def serialize_food(doc: dict) -> dict:
    """Convert a MongoDB food document to a JSON-safe dict."""
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return doc
