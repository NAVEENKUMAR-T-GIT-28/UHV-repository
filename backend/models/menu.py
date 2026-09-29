"""Menu model — schema definition and serialization helpers."""

VALID_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MEAL_SLOTS = ["morning", "afternoon", "evening"]


def new_menu(data: dict) -> dict:
    """Build a clean menu document from validated input data."""
    return {
        "weekStart": data["weekStart"],
        "peopleCount": data.get("peopleCount", 500),
        "dailyBudget": data.get("dailyBudget", 18000),
        "days": data["days"],  # validated before calling this
    }


def serialize_menu(doc: dict) -> dict:
    """Convert a MongoDB menu document to a JSON-safe dict."""
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return doc
