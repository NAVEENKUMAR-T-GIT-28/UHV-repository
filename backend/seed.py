"""Seed script — populate MongoDB with demo food items, a sample menu, and default settings.

Run: python seed.py
Idempotent: clears and re-inserts each time.

NOTE: All nutrition values are illustrative DEMO values, not official IFCT/ICMR data.
"""

import sys
import os

# Ensure the backend directory is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.mongodb import foods_collection, menus_collection, settings_collection
from models.settings import DEFAULT_SETTINGS

# ──────────────── Seed food items (sample data) ────────────────

SEED_FOODS = [
    # ── Breakfast items ──
    {
        "name": "Idli + Sambar",
        "category": "Breakfast",
        "servingSize": 100,
        "unit": "g",
        "price": 8,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 330, "protein": 10, "carbohydrates": 55, "fat": 5, "fiber": 4, "iron": 2.2, "calcium": 70},
        "nutritionSource": "sample",
    },
    {
        "name": "Upma + Banana",
        "category": "Breakfast",
        "servingSize": 100,
        "unit": "g",
        "price": 7,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 340, "protein": 7, "carbohydrates": 60, "fat": 6, "fiber": 3, "iron": 1.8, "calcium": 30},
        "nutritionSource": "sample",
    },
    {
        "name": "Poha + Peanuts",
        "category": "Breakfast",
        "servingSize": 100,
        "unit": "g",
        "price": 8,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 360, "protein": 10, "carbohydrates": 52, "fat": 10, "fiber": 3, "iron": 3.6, "calcium": 40},
        "nutritionSource": "sample",
    },
    {
        "name": "Ragi Dosa + Chutney",
        "category": "Breakfast",
        "servingSize": 100,
        "unit": "g",
        "price": 8,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 340, "protein": 9, "carbohydrates": 58, "fat": 7, "fiber": 5, "iron": 4.0, "calcium": 200},
        "nutritionSource": "sample",
    },
    {
        "name": "Pongal",
        "category": "Breakfast",
        "servingSize": 100,
        "unit": "g",
        "price": 9,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 380, "protein": 12, "carbohydrates": 60, "fat": 8, "fiber": 3, "iron": 2.6, "calcium": 55},
        "nutritionSource": "sample",
    },
    {
        "name": "Idli + Milk",
        "category": "Breakfast",
        "servingSize": 100,
        "unit": "g",
        "price": 11,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 380, "protein": 14, "carbohydrates": 50, "fat": 8, "fiber": 2, "iron": 1.9, "calcium": 250},
        "nutritionSource": "sample",
    },
    # ── Lunch items ──
    {
        "name": "Rice + Dal + Veg Curry",
        "category": "Lunch",
        "servingSize": 100,
        "unit": "g",
        "price": 13,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 620, "protein": 19, "carbohydrates": 95, "fat": 12, "fiber": 8, "iron": 4.8, "calcium": 110},
        "nutritionSource": "sample",
    },
    {
        "name": "Rice + Sambar + Poriyal",
        "category": "Lunch",
        "servingSize": 100,
        "unit": "g",
        "price": 11,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 570, "protein": 15, "carbohydrates": 90, "fat": 10, "fiber": 7, "iron": 4.2, "calcium": 95},
        "nutritionSource": "sample",
    },
    {
        "name": "Rice + Chana Masala",
        "category": "Lunch",
        "servingSize": 100,
        "unit": "g",
        "price": 12,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 620, "protein": 19, "carbohydrates": 92, "fat": 11, "fiber": 9, "iron": 5.8, "calcium": 110},
        "nutritionSource": "sample",
    },
    {
        "name": "Rice + Rajma",
        "category": "Lunch",
        "servingSize": 100,
        "unit": "g",
        "price": 14,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 640, "protein": 21, "carbohydrates": 98, "fat": 10, "fiber": 10, "iron": 6.0, "calcium": 130},
        "nutritionSource": "sample",
    },
    {
        "name": "Rice + Palak Dal",
        "category": "Lunch",
        "servingSize": 100,
        "unit": "g",
        "price": 13,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 600, "protein": 19, "carbohydrates": 88, "fat": 11, "fiber": 9, "iron": 7.0, "calcium": 160},
        "nutritionSource": "sample",
    },
    {
        "name": "Curd Rice + Veg",
        "category": "Lunch",
        "servingSize": 100,
        "unit": "g",
        "price": 10,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 520, "protein": 12, "carbohydrates": 85, "fat": 10, "fiber": 5, "iron": 2.0, "calcium": 210},
        "nutritionSource": "sample",
    },
    {
        "name": "Rice + Paneer Curry",
        "category": "Lunch",
        "servingSize": 100,
        "unit": "g",
        "price": 21,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 650, "protein": 21, "carbohydrates": 80, "fat": 22, "fiber": 4, "iron": 2.6, "calcium": 290},
        "nutritionSource": "sample",
    },
    # ── Dinner items ──
    {
        "name": "Chapati + Dal",
        "category": "Dinner",
        "servingSize": 100,
        "unit": "g",
        "price": 11,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 570, "protein": 17, "carbohydrates": 85, "fat": 10, "fiber": 8, "iron": 4.5, "calcium": 85},
        "nutritionSource": "sample",
    },
    {
        "name": "Chapati + Chana Curry",
        "category": "Dinner",
        "servingSize": 100,
        "unit": "g",
        "price": 12,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 600, "protein": 19, "carbohydrates": 88, "fat": 12, "fiber": 9, "iron": 5.5, "calcium": 95},
        "nutritionSource": "sample",
    },
    {
        "name": "Chapati + Mixed Veg",
        "category": "Dinner",
        "servingSize": 100,
        "unit": "g",
        "price": 9,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 490, "protein": 11, "carbohydrates": 72, "fat": 12, "fiber": 7, "iron": 3.6, "calcium": 70},
        "nutritionSource": "sample",
    },
    {
        "name": "Chapati + Soya Curry",
        "category": "Dinner",
        "servingSize": 100,
        "unit": "g",
        "price": 12,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 600, "protein": 23, "carbohydrates": 78, "fat": 14, "fiber": 8, "iron": 5.2, "calcium": 90},
        "nutritionSource": "sample",
    },
    {
        "name": "Veg Pulao + Raita",
        "category": "Dinner",
        "servingSize": 100,
        "unit": "g",
        "price": 11,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 570, "protein": 12, "carbohydrates": 88, "fat": 14, "fiber": 5, "iron": 2.8, "calcium": 160},
        "nutritionSource": "sample",
    },
    {
        "name": "Chapati + Paneer Curry",
        "category": "Dinner",
        "servingSize": 100,
        "unit": "g",
        "price": 21,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 620, "protein": 21, "carbohydrates": 72, "fat": 22, "fiber": 5, "iron": 2.7, "calcium": 280},
        "nutritionSource": "sample",
    },
    {
        "name": "Khichdi + Curd",
        "category": "Dinner",
        "servingSize": 100,
        "unit": "g",
        "price": 10,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 550, "protein": 16, "carbohydrates": 82, "fat": 10, "fiber": 6, "iron": 3.8, "calcium": 170},
        "nutritionSource": "sample",
    },
    # ── Extra items ──
    {
        "name": "Groundnut Sundal",
        "category": "Snack",
        "servingSize": 100,
        "unit": "g",
        "price": 6,
        "availableQuantity": 50,
        "dietaryTags": ["vegetarian"],
        "nutrition": {"calories": 280, "protein": 12, "carbohydrates": 18, "fat": 18, "fiber": 5, "iron": 2.5, "calcium": 45},
        "nutritionSource": "sample",
    },
]


def seed():
    """Clear and re-seed all collections. Idempotent."""
    print("🌱 Seeding NutriPlan database...")

    # ── Foods ──
    foods_col = foods_collection()
    foods_col.delete_many({})
    result = foods_col.insert_many(SEED_FOODS)
    food_ids = result.inserted_ids
    print(f"   ✅ Inserted {len(food_ids)} food items")

    # Build a name → id lookup for the sample menu
    id_by_name = {}
    for i, food in enumerate(SEED_FOODS):
        id_by_name[food["name"]] = str(food_ids[i])

    # ── Sample weekly menu (habitual menu from the README) ──
    # Habitual: Idli + Milk / Curd Rice + Veg / Veg Pulao + Raita, all 7 days
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    sample_days = []
    for day_name in days_of_week:
        sample_days.append({
            "day": day_name,
            "morning": [id_by_name["Idli + Milk"]],
            "afternoon": [id_by_name["Curd Rice + Veg"]],
            "evening": [id_by_name["Veg Pulao + Raita"]],
        })

    menus_col = menus_collection()
    menus_col.delete_many({})
    menus_col.insert_one({
        "weekStart": "2026-09-28",
        "peopleCount": 500,
        "dailyBudget": 18000,
        "days": sample_days,
    })
    print("   ✅ Inserted sample weekly menu (habitual menu)")

    # ── Settings ──
    settings_col = settings_collection()
    settings_col.delete_many({})
    settings_col.insert_one(DEFAULT_SETTINGS.copy())
    print("   ✅ Inserted default settings")

    print("\n🎉 Seeding complete! The backend is ready to use.")
    print("   NOTE: All nutrition values are illustrative demo values.")


if __name__ == "__main__":
    seed()
