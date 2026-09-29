"""Settings model — institution-level configuration."""

DEFAULT_SETTINGS = {
    "_id": "default",
    "peopleCount": 500,
    "dailyBudget": 18000,
    "kitchenCapacity": 500,
    "dietaryRequirements": ["vegetarian"],
    "nutritionTargets": {
        "energy": 1500,
        "protein": 45,
        "iron": 12,
        "calcium": 450,
        "fiber": 25,
    },
    "ai": {
        "provider": "groq",
        "model": "llama3-8b-8192"
    },
}


def serialize_settings(doc: dict) -> dict:
    """Convert a MongoDB settings document to a JSON-safe dict."""
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return doc
