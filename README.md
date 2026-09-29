NutriPlan — Final Idea & System Architecture
1. Project Overview

NutriPlan is a web-based institutional meal optimization system designed for colleges, hostels, schools, shelters, and other mass-meal institutions.

The system helps a non-technical meal planner create a balanced 7-day meal plan while simultaneously considering:

👥 Number of people
💰 Daily meal budget
🥗 Nutritional requirements
📦 Available ingredients
🍳 Kitchen capacity
🌱 Dietary requirements
🔄 Meal variety

The core principle is:

Do not hide the trade-off between nutrition, cost, and operational constraints. Make it visible and help the planner find the best feasible plan.

2. Problem We Are Solving

Institutional kitchens have to prepare food for hundreds of people every day.

The planner must answer several questions simultaneously:

Can we afford the menu?
        +
Does it provide adequate nutrition?
        +
Do we have the required ingredients?
        +
Can our kitchen prepare it?
        +
Does it respect dietary requirements?
        +
Is the menu sufficiently varied?

A low-cost menu may satisfy the budget but create nutritional gaps.

A highly nutritious menu may exceed the available budget.

A theoretically good menu may require ingredients that are unavailable.

Therefore, NutriPlan treats meal planning as a constraint-driven decision problem rather than simply generating recipes.

3. Target User
Primary User

Institutional Meal Planner / Mess Manager

The user does not need to understand:

optimization algorithms
mathematical programming
nutrition equations
AI models
database systems

Instead, they interact with simple questions:

How many people are you serving?

What is your daily budget?

What ingredients are available?

What dietary requirements should we respect?

What can your kitchen handle?

The system handles the technical complexity behind the interface.

4. Core Product Flow
CONFIGURE
    ↓
ADD AVAILABLE INGREDIENTS
    ↓
DEFINE CONSTRAINTS
    ↓
OPTIMIZE
    ↓
VERIFY
    ↓
VIEW 7-DAY PLAN
    ↓
UNDERSTAND WHY
    ↓
WHAT-IF / RE-OPTIMIZE
5. Main Features
5.1 Institution Setup

The planner enters:

Institution Type
        ↓
Number of People
        ↓
Daily Budget
        ↓
Kitchen Capacity
        ↓
Dietary Requirements

Example:

Institution: College Hostel
People: 500
Daily Budget: ₹18,000
Kitchen Capacity: 500 meals/day

Dietary:
✓ Vegetarian
✓ No specific allergens
6. Ingredient Management

The system provides a simple ingredient inventory.

Example:

Ingredient	Available	Price	Nutritional Data
Rice	100 kg	₹45/kg	Yes
Dal	30 kg	₹110/kg	Yes
Vegetables	50 kg	₹60/kg	Yes
Milk	50 L	₹55/L	Yes
Banana	200	₹6/unit	Yes
Groundnut	15 kg	₹140/kg	Yes

For the hackathon MVP, the dataset can be preloaded.

The user can modify availability when demonstrating the What-if feature.

7. Meal Dataset

Each meal combination contains structured information.

Example:

{
  name: "Rice + Dal + Vegetable Curry",

  costPerPerson: 32,

  nutrition: {
    energy: 620,
    protein: 18,
    iron: 5,
    calcium: 120
  },

  ingredients: [
    "rice",
    "dal",
    "vegetables"
  ],

  dietaryTags: [
    "vegetarian"
  ],

  kitchenLoad: 1
}

The optimizer works with this structured data.

8. Optimization Logic

The most important technical decision:

Deterministic Optimization Core

The system does not use an LLM to decide what people should eat.

Instead:

Meal Dataset
     ↓
Hard Constraint Filtering
     ↓
Feasible Meals
     ↓
Objective Scoring
     ↓
Best Feasible Combination
     ↓
7-Day Meal Plan
9. Hard Constraints

These are requirements that the optimizer should not silently violate.

Budget
Total Cost ≤ Available Budget
Ingredient Availability
Required Quantity ≤ Available Quantity
Kitchen Capacity
Required Kitchen Capacity ≤ Available Capacity
Dietary Requirements

Example:

Vegetarian requirement
        ↓
Non-vegetarian meals excluded

These constraints determine whether a plan is feasible.

10. Optimization Objectives

After removing infeasible options, the system scores the remaining possibilities.

Conceptually:

              FEASIBLE MEALS
                    ↓
       ┌────────────┼────────────┐
       ↓            ↓            ↓
   Nutrition       Cost        Variety
       ↓            ↓            ↓
       └────────────┼────────────┘
                    ↓
              Final Score
                    ↓
             Best Feasible Plan

Example scoring model:

Final Score =

40% Nutrition Coverage
25% Cost Efficiency
20% Meal Variety
15% Ingredient Utilization

These weights are configurable implementation parameters rather than claims that this is a universal nutritional standard.

11. Nutrition Coverage

The dashboard should make nutrition understandable.

Instead of showing only raw numbers:

Protein: 18g
Iron: 5mg
Calcium: 120mg

show:

Nutrition Coverage

Energy       █████████░  92%
Protein      ██████████  98%
Iron         ████████░░  84%
Calcium      █████████░  91%

This makes the hidden nutrition gap visible.

12. Constraint Status

The final plan should clearly communicate whether it satisfies the important constraints.

PLAN FEASIBILITY

✓ Budget
  ₹17,420 / ₹18,000

✓ Ingredients
  Available inventory sufficient

✓ Kitchen Capacity
  500 / 500 meals

✓ Dietary Requirements
  Vegetarian requirement satisfied

✓ Nutrition
  Target coverage achieved

The user should never have to guess whether the generated plan is actually feasible.

13. Hidden Nutrition Gap

This is one of the most important parts of the concept.

Instead of simply saying:

"Here is your menu."

NutriPlan shows:

"Here is your menu, and here is what it achieves."

Example:

Current Plan

Calories       ✓
Protein        ✓
Iron           ⚠ 84%
Calcium        ✓

The planner can immediately see that the menu may look acceptable while a specific nutrient remains below the selected target.

14. What-If / Re-Optimization

This is a major demo feature.

The planner can change a real-world constraint.

Example 1 — Budget Reduction

Current:

Budget: ₹18,000/day

Change:

Budget: ₹15,000/day

Click:

RE-OPTIMIZE

The system recalculates the plan.

Then show:

BEFORE                     AFTER

₹17,420                    ₹14,860

Paneer Curry       →       Chana Curry
Milk               →       Curd

And explain the resulting nutrition/cost changes.

15. Ingredient Availability Scenario

Example:

Remove Rice from available inventory

Then:

RE-OPTIMIZE

The system finds another feasible combination if one exists.

This demonstrates that the system responds to real operational constraints, rather than displaying a static meal plan.

16. Infeasibility Handling

This is important for credibility.

Suppose the budget becomes unrealistically low.

Instead of generating a bad menu and pretending it is valid:

No Feasible Plan

Show:

Why?

Available budget: ₹8,000/day

Minimum feasible cost: ₹13,650/day

Nutrition target cannot be satisfied
within the current budget.

Then provide possible adjustments:

Possible adjustments:

→ Increase budget
→ Modify ingredient availability
→ Relax selected nutrition target
→ Increase available kitchen capacity

The system should surface the conflict rather than hide it.

17. Optional AI Explanation Layer

AI is used only after optimization.

              OPTIMIZER
                  ↓
           Verified Result
                  ↓
             Optional AI
                  ↓
       Human-Friendly Explanation
AI should NOT:
generate the meal plan
calculate nutrition
invent food prices
validate nutritional adequacy
override constraints
AI CAN:

Explain the already-computed result.

Example:

"The plan stayed within the daily budget by replacing the higher-cost paneer dish with a legume-based meal. The change maintains the selected protein target while reducing the estimated daily cost."

If the AI API fails, the application still works using deterministic explanations.

18. AI System Prompt
You are a meal-plan explanation assistant.

Explain the optimization result to a non-technical institutional meal planner using only the supplied data.

Do not create, modify, validate, or recommend meals.

Do not invent nutritional values, costs, ingredients, or constraints.

Explain:
- why the selected plan was chosen,
- how it satisfies the supplied constraints,
- what changed after re-optimization,
- and which constraints could not be satisfied if the plan is infeasible.

Keep the explanation simple and factual.
19. Final System Architecture
                         ┌─────────────────────────┐
                         │     MEAL PLANNER        │
                         │   Non-technical User    │
                         └────────────┬────────────┘
                                      │
                                      ▼
                    ┌──────────────────────────────┐
                    │       REACT FRONTEND         │
                    │                              │
                    │  Setup                       │
                    │  Ingredients                 │
                    │  Constraints                 │
                    │  Meal Plan                   │
                    │  Nutrition Dashboard         │
                    │  What-if                     │
                    └──────────────┬───────────────┘
                                   │
                              API Request
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │       NODE.JS + EXPRESS      │
                    │                              │
                    │     Optimization API        │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
             ┌─────────────────────────────────────────────┐
             │          DETERMINISTIC OPTIMIZER            │
             │                                             │
             │  ┌───────────────────────────────────────┐  │
             │  │ Meal Dataset                          │  │
             │  └──────────────────┬────────────────────┘  │
             │                     ↓                       │
             │  ┌───────────────────────────────────────┐  │
             │  │ Hard Constraint Filtering             │  │
             │  │                                       │  │
             │  │ • Budget                              │  │
             │  │ • Ingredient Availability              │  │
             │  │ • Kitchen Capacity                    │  │
             │  │ • Dietary Requirements                │  │
             │  └──────────────────┬────────────────────┘  │
             │                     ↓                       │
             │  ┌───────────────────────────────────────┐  │
             │  │ Objective Scoring                      │  │
             │  │                                       │  │
             │  │ • Nutrition Coverage                  │  │
             │  │ • Cost Efficiency                     │  │
             │  │ • Variety                             │  │
             │  │ • Ingredient Utilization              │  │
             │  └──────────────────┬────────────────────┘  │
             │                     ↓                       │
             │             Best Feasible Plan              │
             └─────────────────────┬───────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │       PLAN VERIFICATION      │
                    │                              │
                    │  Cost                        │
                    │  Nutrition                   │
                    │  Ingredients                 │
                    │  Kitchen Capacity            │
                    │  Dietary Requirements        │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │       OPTIONAL AI LAYER      │
                    │                              │
                    │  Human-friendly explanation  │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │       REACT DASHBOARD        │
                    │                              │
                    │  7-Day Meal Plan             │
                    │  Nutrition Coverage          │
                    │  Cost & Budget               │
                    │  Constraint Status           │
                    │  Why This Plan?              │
                    │  What-If Comparison          │
                    └──────────────────────────────┘
20. Technology Stack
Frontend
├── React
├── Vite
├── Tailwind CSS
├── Lucide React
└── Recharts

Backend
├── Node.js
└── Express

Optimization
└── Deterministic JavaScript Optimization Engine

Data
└── JSON / JavaScript Dataset

AI
└── Optional LLM API
   └── Explanation only

Database
└── None for MVP

Deployment
├── Vercel
└── Render / Railway
21. Frontend Architecture
src/
│
├── components/
│   ├── Navbar
│   ├── SetupForm
│   ├── ConstraintCard
│   ├── IngredientTable
│   ├── MealPlanTable
│   ├── NutritionCard
│   ├── BudgetCard
│   ├── ConstraintStatus
│   ├── WhyThisPlan
│   ├── WhatIfPanel
│   └── InfeasibleState
│
├── pages/
│   ├── Setup
│   └── Dashboard
│
├── data/
│   ├── meals.js
│   └── ingredients.js
│
├── services/
│   └── api.js
│
├── utils/
│   └── formatting.js
│
└── App.jsx
22. Backend Architecture
server/
│
├── data/
│   ├── meals.js
│   └── ingredients.js
│
├── services/
│   ├── optimizer.js
│   ├── nutrition.js
│   └── explanation.js
│
├── routes/
│   └── optimize.js
│
└── server.js
API
POST /api/optimize

Input:

{
  "people": 500,
  "budget": 18000,
  "kitchenCapacity": 500,
  "dietaryRequirements": [
    "vegetarian"
  ],
  "availableIngredients": [
    "rice",
    "dal",
    "vegetables",
    "milk",
    "banana"
  ]
}

Output:

{
  "feasible": true,

  "plan": [],

  "totalCost": 17420,

  "nutrition": {
    "energy": 92,
    "protein": 98,
    "iron": 84,
    "calcium": 91
  },

  "constraints": {
    "budget": true,
    "ingredients": true,
    "kitchenCapacity": true,
    "dietaryRequirements": true
  },

  "changes": []
}
23. UI Structure
Screen 1 — Setup
┌──────────────────────────────────────────────┐
│ NutriPlan                         Step 1/3   │
│ Institutional Meal Optimizer                │
├──────────────────────────────────────────────┤
│                                              │
│ Institution                                  │
│ [ College Hostel ▼ ]                         │
│                                              │
│ People Served                                │
│ [ 500 ]                                      │
│                                              │
│ Daily Budget                                 │
│ [ ₹18,000 ]                                  │
│                                              │
│ Kitchen Capacity                             │
│ [ 500 meals/day ]                            │
│                                              │
│ Dietary Requirements                         │
│ [✓] Vegetarian                               │
│                                              │
│             [ Continue → ]                   │
└──────────────────────────────────────────────┘
24. Screen 2 — Ingredients
Available Ingredients

Rice          100 kg       ✓
Dal            30 kg       ✓
Vegetables     50 kg       ✓
Milk           50 L        ✓
Banana        200 units    ✓
Groundnut      15 kg       ✓

                    [ Generate Plan ]
25. Screen 3 — Optimization Dashboard

Top-level cards:

₹17,420
Daily Cost

92%
Nutrition

500
People Served

✓
All Constraints

Then:

7-DAY MEAL PLAN
─────────────────────────────────────────────

       Breakfast       Lunch          Dinner

Mon    Idli + Milk     Rice + Dal     Chapati + Curry
Tue    Upma + Banana   Rice + Sambar  Rice + Vegetables
Wed    Dosa + Milk     Rice + Dal     Chapati + Dal
...
26. Nutrition Dashboard
NUTRITION COVERAGE

Energy       █████████░ 92%
Protein      ██████████ 98%
Iron         ████████░░ 84%
Calcium      █████████░ 91%

Highlight gaps instead of hiding them.

27. Why This Plan?
WHY THIS PLAN?

✓ Fits within your daily budget
✓ Uses currently available ingredients
✓ Meets the selected dietary requirement
✓ Fits your kitchen capacity
✓ Maintains the selected nutrition targets

The optimizer selected lower-cost protein sources
where possible to preserve nutrition while keeping
the total meal cost within the budget.
28. What-If Mode
WHAT IF?

Daily Budget

₹18,000
───────────────●────
₹15,000

                 [ Re-optimize ]

────────────────────────────────────

BEFORE                 AFTER

₹17,420                ₹14,860

Paneer Curry     →     Chana Curry
Milk             →     Curd

Nutrition: 92%         Nutrition: 89%

This gives judges an immediate demonstration of the optimization engine.

29. Infeasible State
             ⚠ NO FEASIBLE PLAN

The current constraints cannot be satisfied.

Budget available       ₹8,000
Minimum feasible cost   ₹13,650

Nutrition target cannot be achieved
within the current budget.

Possible changes:

[ Increase Budget ]

[ Adjust Ingredient Availability ]

[ Review Selected Targets ]

This is much stronger than silently producing an invalid plan.

30. Hackathon Demo Flow

The entire demo should take approximately 3–5 minutes.

Step 1

Start with:

College Hostel
500 students
₹18,000/day
Vegetarian
500 meal kitchen capacity
Step 2

Generate the plan.

Show:

7-day menu
₹17,420 cost
Nutrition coverage
Constraint status
Step 3

Say:

"Now let's see what happens when the real-world constraint changes."

Reduce:

₹18,000 → ₹15,000

Click:

Re-optimize

Show the changed meals and nutrition/cost impact.

Step 4

Remove an ingredient.

Milk → unavailable

Re-optimize.

Show how the plan adapts.

Step 5

Create an extreme constraint.

₹8,000

Show:

No feasible plan

and explain the conflict.

31. UHV Connection

NutriPlan is not simply a food calculator.

The underlying value proposition is:

Justice

People dependent on institutional meals should not silently receive nutritionally inadequate food because of hidden planning trade-offs.

Trust

The system shows why a plan was selected instead of presenting an unexplained AI-generated menu.

Right Understanding
Full stomach ≠ Balanced nutrition

The dashboard makes the difference visible.

Respect

Dietary requirements are treated as first-class constraints rather than optional preferences.

Transparency

When constraints conflict, the system communicates the conflict instead of hiding it.

32. What We Are NOT Building

To protect the 2-hour MVP scope:

❌ Authentication
❌ Complex role management
❌ IoT
❌ Sensors
❌ Hardware
❌ Blockchain
❌ Real-time supplier marketplace
❌ Mobile application
❌ Complex ML model
❌ LLM-generated meal plans
❌ Production database
❌ Payment system
❌ Notification system
❌ Huge food database

The product should demonstrate the core problem-solving capability, not unnecessary technology.

33. Final Product Positioning
One-line pitch

NutriPlan is a transparent institutional meal optimization system that helps meal planners balance nutrition, budget, ingredient availability, kitchen capacity, and dietary needs—while making every trade-off visible.

Demo pitch

"Institutions don't struggle because they don't know what healthy food is. They struggle because they have to make nutrition decisions under real-world constraints. NutriPlan turns those constraints into a transparent optimization problem, generates a feasible 7-day meal plan, shows the nutritional and financial impact, and lets planners see exactly what changes when their constraints change."

34. Final MVP Architecture in One Diagram
                         NUTRIPLAN
                            │
                ┌───────────┴───────────┐
                │                       │
             INPUTS                   USER
                │                       │
     ┌──────────┼──────────┐            │
     │          │          │            │
  Budget    Ingredients  Kitchen      Dietary
     │          │          │          Needs
     └──────────┼──────────┼───────────┘
                │
                ▼
       ┌───────────────────┐
       │  HARD CONSTRAINTS  │
       │                   │
       │ Budget            │
       │ Ingredients       │
       │ Kitchen           │
       │ Dietary           │
       └─────────┬─────────┘
                 │
                 ▼
          FEASIBLE OPTIONS
                 │
                 ▼
       ┌───────────────────┐
       │ OPTIMIZATION CORE │
       │                   │
       │ Nutrition         │
       │ Cost              │
       │ Variety           │
       │ Utilization       │
       └─────────┬─────────┘
                 │
                 ▼
          BEST FEASIBLE PLAN
                 │
        ┌────────┴────────┐
        ▼                 ▼
   VERIFICATION      AI EXPLANATION
        │                 │
        └────────┬────────┘
                 ▼
       ┌───────────────────┐
       │   USER DASHBOARD  │
       │                   │
       │ 7-Day Plan        │
       │ Cost              │
       │ Nutrition         │
       │ Constraints       │
       │ Why?              │
       │ What-if           │
       └─────────┬─────────┘
                 │
                 ▼
           RE-OPTIMIZE
                 │
                 └──────────→ Optimization Core
Final technical principle

The frontend is the product experience.
The deterministic optimizer is the product intelligence.
The optional LLM is only the product explainer.