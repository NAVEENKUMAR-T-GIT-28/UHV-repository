"""Deterministic cost and nutrition calculations.

CODE CALCULATES — these functions are the single source of truth for all
numeric values shown to the user. The LLM never performs these calculations.
"""

from models.food import NUTRITION_FIELDS


# ─────────────────────── Cost calculations ───────────────────────

def meal_cost(food_price: float, people_count: int, servings: int = 1) -> float:
    """Cost of one food item for all people in a single meal."""
    return food_price * people_count * servings


def daily_cost(foods: list[dict], people_count: int) -> float:
    """Total daily cost across all meals (morning + afternoon + evening)."""
    total = 0.0
    for food in foods:
        total += food["price"] * people_count
    return total


def weekly_cost(daily: float) -> float:
    """Weekly cost from a constant daily cost."""
    return daily * 7


def cost_per_person(total_cost: float, people_count: int) -> float:
    """Per-person share of a given total cost."""
    if people_count == 0:
        return 0.0
    return round(total_cost / people_count, 2)


def remaining_budget(budget: float, actual_cost: float) -> float:
    """How much budget remains (can be negative if over-budget)."""
    return budget - actual_cost


# ─────────────────────── Nutrition calculations ───────────────────────

def food_nutrition_contribution(food: dict, people_count: int) -> dict:
    """Total nutrition from one food item across all people."""
    nutrition = food.get("nutrition", {})
    return {
        field: nutrition.get(field, 0) * people_count
        for field in NUTRITION_FIELDS
    }


def aggregate_nutrition(foods: list[dict]) -> dict:
    """Sum nutrition per-person across a list of food items (one serving each).

    Returns per-person totals (not multiplied by people count).
    """
    totals = {field: 0.0 for field in NUTRITION_FIELDS}
    for food in foods:
        nutrition = food.get("nutrition", {})
        for field in NUTRITION_FIELDS:
            totals[field] += nutrition.get(field, 0)
    return totals


def daily_nutrition_per_person(day_foods: list[dict]) -> dict:
    """Per-person nutrition for all meals in one day."""
    return aggregate_nutrition(day_foods)


def weekly_avg_nutrition_per_person(daily_totals: list[dict]) -> dict:
    """Average per-person per-day nutrition over the week."""
    if not daily_totals:
        return {field: 0.0 for field in NUTRITION_FIELDS}

    sums = {field: 0.0 for field in NUTRITION_FIELDS}
    for day in daily_totals:
        for field in NUTRITION_FIELDS:
            sums[field] += day.get(field, 0)

    n_days = len(daily_totals)
    return {field: round(sums[field] / n_days, 2) for field in NUTRITION_FIELDS}


# ─────────────────────── Coverage calculations ───────────────────────

# Maps nutrition field names → settings target names
NUTRITION_TO_TARGET = {
    "calories": "energy",
    "protein": "protein",
    "iron": "iron",
    "calcium": "calcium",
    "fiber": "fiber",
}


def coverage_percentage(actual: float, target: float) -> float:
    """Coverage as a percentage (0-based). Returns 0 if target is 0."""
    if target <= 0:
        return 100.0  # no target means satisfied
    return round((actual / target) * 100, 1)


def nutrition_coverage(per_person_nutrition: dict, targets: dict) -> dict:
    """Compute coverage % for each nutrient against the configured targets."""
    coverage = {}
    for food_field, target_key in NUTRITION_TO_TARGET.items():
        actual = per_person_nutrition.get(food_field, 0)
        target = targets.get(target_key, 0)
        coverage[target_key] = coverage_percentage(actual, target)
    return coverage


def identify_gaps(coverage: dict, threshold: float = 100.0) -> list[dict]:
    """Return nutrients below the given coverage threshold."""
    gaps = []
    for nutrient, pct in coverage.items():
        if pct < threshold:
            gaps.append({
                "nutrient": nutrient,
                "coverage": pct,
                "shortfall": round(threshold - pct, 1),
            })
    # Sort by worst gap first
    gaps.sort(key=lambda g: g["coverage"])
    return gaps


# ─────────────────────── Budget checking ───────────────────────

def check_budget(actual_daily_cost: float, daily_budget: float) -> dict:
    """Check whether the daily cost fits the budget."""
    within = actual_daily_cost <= daily_budget
    return {
        "withinBudget": within,
        "dailyCost": round(actual_daily_cost, 2),
        "dailyBudget": daily_budget,
        "remaining": round(daily_budget - actual_daily_cost, 2),
        "overBy": round(actual_daily_cost - daily_budget, 2) if not within else 0,
    }


# ─────────────────────── Full menu summary ───────────────────────

def calculate_menu_summary(
    menu_days: list[dict],
    foods_by_id: dict,
    people_count: int,
    daily_budget: float,
    nutrition_targets: dict,
) -> dict:
    """Compute the complete cost + nutrition summary for a weekly menu.

    Args:
        menu_days: list of 7 day dicts with morning/afternoon/evening food IDs
        foods_by_id: {str_id: food_doc} lookup
        people_count: number of people to feed
        daily_budget: daily budget in ₹
        nutrition_targets: target nutrients per person per day

    Returns:
        Full summary dict with cost, nutrition, coverage, and gaps.
    """
    daily_costs = []
    daily_nutritions = []
    per_day_details = []

    for day_entry in menu_days:
        day_name = day_entry.get("day", "Unknown")
        day_foods = []

        for slot in ["morning", "afternoon", "evening"]:
            food_ids = day_entry.get(slot, [])
            for fid in food_ids:
                food = foods_by_id.get(str(fid))
                if food:
                    day_foods.append(food)

        # Cost for this day
        d_cost = daily_cost(day_foods, people_count)
        daily_costs.append(d_cost)

        # Nutrition per person for this day
        d_nutrition = daily_nutrition_per_person(day_foods)
        daily_nutritions.append(d_nutrition)

        # Coverage for this day
        d_coverage = nutrition_coverage(d_nutrition, nutrition_targets)

        per_day_details.append({
            "day": day_name,
            "cost": round(d_cost, 2),
            "costPerPerson": cost_per_person(d_cost, people_count),
            "nutrition": d_nutrition,
            "coverage": d_coverage,
        })

    # Weekly aggregates
    avg_daily_cost = sum(daily_costs) / 7 if daily_costs else 0
    total_weekly_cost = sum(daily_costs)
    avg_nutrition = weekly_avg_nutrition_per_person(daily_nutritions)
    overall_coverage = nutrition_coverage(avg_nutrition, nutrition_targets)
    gaps = identify_gaps(overall_coverage)

    budget_check = check_budget(avg_daily_cost, daily_budget)

    status = "all_met" if not gaps else "gaps_found"

    return {
        "status": status,
        "cost": {
            "daily": round(avg_daily_cost, 2),
            "weekly": round(total_weekly_cost, 2),
            "dailyBudget": daily_budget,
            "remaining": budget_check["remaining"],
            "perPerson": cost_per_person(avg_daily_cost, people_count),
            "withinBudget": budget_check["withinBudget"],
        },
        "nutrition": avg_nutrition,
        "coverage": overall_coverage,
        "gaps": gaps,
        "perDay": per_day_details,
    }
