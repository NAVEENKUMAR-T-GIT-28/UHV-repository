"""MongoDB connection and collection accessors."""

from pymongo import MongoClient
from config import Config

_client = None
_db = None


def get_client():
    """Return (and cache) the MongoClient singleton."""
    global _client
    if _client is None:
        _client = MongoClient(Config.MONGO_URI)
    return _client


def get_db():
    """Return the nutriplan database handle."""
    global _db
    if _db is None:
        client = get_client()
        # Extract DB name from URI, default to 'nutriplan'
        db_name = Config.MONGO_URI.rsplit("/", 1)[-1].split("?")[0] or "nutriplan"
        _db = client[db_name]
    return _db


# --------------- collection shortcuts ---------------

def foods_collection():
    return get_db()["foods"]


def menus_collection():
    return get_db()["menus"]


def settings_collection():
    return get_db()["settings"]
