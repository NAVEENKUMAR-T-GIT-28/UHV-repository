# NutriPlan — Institutional Meal Optimization System

> Hack4Values · Track 4 · PS 4.2 "The Hidden Nutrition Gap in Institutional Meals"
> Stack: **React (Vite) + Python + Flask + MongoDB**, with an optional LLM (Groq) that only *explains*.

This file is the build spec. Build exactly this. Anything marked **(stretch)** is only done if the core is finished.

---

## 1. What we are building

A web tool for a **college hostel mess in-charge** to answer one question:

> "Given my budget, my stock and my kitchen, can I feed 500 students properly for a week, and if not, what exactly is missing?"

The in-charge can:

1. **See** the week's cost and nutrition at a glance (Dashboard).
2. **Manage** food items and their per-serving cost and nutrients (Food Items).
3. **Plan** a 7-day × 3-meal menu by hand (Mess Menu).
4. **Analyse** any menu and expose hidden nutrient gaps (Analyser).
5. **Balance**: auto-generate a menu that meets nutrition within budget, run what-ifs, and get honest alternatives when it is impossible (Balancer).

### The three demo moments (everything is built to make these work)

| Moment | What the judge sees |
|---|---|
| **Hidden gap** | A menu that looks fine (cost within budget, stomachs full) shows **iron 56%, protein 84%** in the Analyser. |
| **Optimize + what-if** | At ₹18,000/day the Balancer builds a plan meeting all targets. Moving the budget slider re-solves and shows before/after. |
| **Honest infeasibility** | At ₹15,000/day, full targets are impossible. The app says **why**, shows the **exact funding gap**, and offers computed alternatives. It never fakes a plan. |

---

## 2. Non-negotiable principles

1. **Numbers come from code, never from the LLM.** Cost, nutrient totals, coverage %, feasibility and the menu itself are computed deterministically in Python. Every number on screen must be reproducible.
2. **The LLM only explains.** It receives already-computed JSON and writes plain-language text. It never generates menus, calculates nutrition, invents prices, or validates anything.
3. **Nutrition is a hard constraint, not a score.** A plan below target is never shown as "success". A nutrient below 100% is always shown in amber/red, including in the constraint checklist.
4. **Trade-offs are surfaced.** When constraints conflict, say which one, by how much, and what could change.
5. **App works without the LLM.** If Groq fails or times out, template explanations are returned instead.
6. **Sample data is labeled as sample data.** Nutrient values are demo values, not authoritative IFCT values.

---

## 3. System architecture

```
┌──────────────────────────────────────────────────────────────┐
│                 REACT (Vite) FRONTEND                        │
│  Dashboard | Food Items | Mess Menu | Analyser | Balancer    │
└───────────────────────────┬──────────────────────────────────┘
                            │  JSON over HTTP  (/api/*)
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                       FLASK API                              │
│  routes/   food_items · stock · settings · menu · dashboard  │
│            analyze · balance · whatif · explain              │
│                                                              │
│  services/ ┌────────────────────────────────────────────┐    │
│            │ nutrition.py   evaluate any menu (pure math)│   │
│            │ optimizer.py   MILP via scipy.optimize.milp │   │
│            │ assign.py      order chosen meals into days │    │
│            │ diagnose.py    infeasibility + alternatives │    │
│            │ swaps.py       ranked meal-swap suggestions │    │
│            │ explain.py     Groq call + template fallback│    │
│            └────────────────────────────────────────────┘    │
└──────────────┬───────────────────────────────┬───────────────┘
               │ PyMongo                       │ HTTPS (optional)
               ▼                               ▼
      ┌─────────────────┐              ┌─────────────────┐
      │    MongoDB      │              │   Groq LLM API  │
      │ food_items      │              │  EXPLAIN ONLY   │
      │ stock           │              └─────────────────┘
      │ settings        │
      │ menus           │
      │ plan_runs       │
      └─────────────────┘
```

**Data flow rule:** `DB → services (deterministic) → JSON result → (optional) LLM explanation → UI`. The LLM is a leaf at the end. Nothing ever flows from the LLM back into calculations.

---

## 4. Tech stack

| Layer | Choice | Notes |
|---|---|---|
| Frontend | React 19, Vite, React Router, Tailwind CSS, lucide-react | Recharts optional for the coverage chart |
| Backend | Python 3.11+, Flask, flask-cors | App factory + blueprints |
| Validation | Pydantic v2 | Request/response models |
| Optimization | `numpy`, `scipy>=1.9` (`scipy.optimize.milp`, HiGHS) | No extra solver install needed |
| Database | MongoDB (Atlas free tier or local), PyMongo | No auth/users |
| LLM (optional) | Groq API via `groq` SDK | Model name from env, never hardcoded |
| Tests | pytest | Solver + evaluator tests are required |
| Deploy | Vercel/Netlify (frontend), Render (Flask + gunicorn), Atlas | Localhost is fine for the demo |

---

## 5. Repository structure

```
nutriplan/
├── README.md
├── backend/
│   ├── app.py                    # create_app(), blueprint registration, CORS
│   ├── config.py                 # env loading
│   ├── db.py                     # Mongo client + collection getters
│   ├── schemas.py                # Pydantic models (FoodItem, Settings, PlanResult, ...)
│   ├── routes/
│   │   ├── food_items.py
│   │   ├── stock.py
│   │   ├── settings.py
│   │   ├── menu.py
│   │   ├── dashboard.py
│   │   ├── analyze.py
│   │   ├── balance.py            # /balance and /whatif
│   │   └── explain.py
│   ├── services/
│   │   ├── nutrition.py
│   │   ├── optimizer.py
│   │   ├── assign.py
│   │   ├── diagnose.py
│   │   ├── swaps.py
│   │   └── explain.py
│   ├── seed/
│   │   ├── food_items.json       # built from the table in Appendix A
│   │   └── seed.py               # idempotent; also used by POST /api/seed/reset
│   ├── tests/
│   │   ├── test_nutrition.py
│   │   └── test_optimizer.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── pages/  (Dashboard, FoodItems, MessMenu, Analyser, Balancer)
    │   ├── components/  (SummaryCard, CoverageBars, ConstraintChecklist, MenuGrid,
    │   │                 FoodItemForm, WhatIfPanel, InfeasibleState, AlternativeCard, ...)
    │   ├── api/client.js         # fetch wrapper, base URL from VITE_API_URL
    │   ├── lib/format.js         # ₹ and % formatting
    │   └── App.jsx
    ├── vite.config.js            # dev proxy /api -> http://localhost:5000
    └── .env.example
```

**UI reference:** the visual language (sidebar layout, summary cards, coverage bars, amber gap callouts, before/after comparison) should follow the existing `nutriplan-frontend` repo. Reuse its styling. Replace every hardcoded value with API data.

---

## 6. Data model (MongoDB)

### `food_items` — a servable dish, priced and measured **per serving (1 person)**

```json
{
  "_id": "ObjectId",
  "name": "Rice + Chana Masala",
  "slot": "lunch",                       // breakfast | lunch | dinner
  "unit": "serving",
  "cost_per_unit": 12,                   // ₹ per serving
  "nutrients_per_unit": { "energy_kcal": 620, "protein_g": 19, "iron_mg": 5.8, "calcium_mg": 110 },
  "diet": "vegetarian",                  // vegetarian | non_vegetarian
  "ingredients": [ { "name": "rice", "qty_per_unit": 0.10, "unit": "kg" },
                   { "name": "chana", "qty_per_unit": 0.05, "unit": "kg" } ],
  "kitchen_load": 1,
  "active": true,
  "source": "seed",                      // seed | user | ai_estimate
  "created_at": "...", "updated_at": "..."
}
```

### `stock` — weekly ingredient availability

```json
{ "ingredient": "milk", "available_qty": 2000, "unit": "L" }
```

### `settings` — single document `_id: "default"`

```json
{
  "institution_type": "College Hostel",
  "people": 500,
  "daily_budget": 18000,
  "kitchen_capacity": 500,                // max meals served per meal-time
  "diet": "vegetarian",                   // vegetarian | any
  "targets_per_person_day": { "energy_kcal": 1500, "protein_g": 45, "iron_mg": 12, "calcium_mg": 450 },
  "max_repeats_per_week": 2,              // same dish at most N times a week in its slot
  "coverage_cap": 1.25                    // optimizer will not chase coverage above this
}
```

Targets are the **share of daily needs the mess supplies** across three meals. They are demo values; verify against ICMR-NIN before presenting them as official.

### `menus` — the current saved week, `_id: "current"`

```json
{
  "days": [ { "day": "MON", "breakfast": "<food_item_id>", "lunch": "<id>", "dinner": "<id>" }, "... 7 entries" ],
  "source": "manual",                     // manual | balancer
  "updated_at": "..."
}
```

### `plan_runs` — history of balancer runs (used for what-if "before")

```json
{ "settings_snapshot": {}, "result": {}, "created_at": "..." }
```

---

## 7. Core algorithms

### 7.1 Evaluator (`nutrition.py`) — used by Dashboard, Menu, Analyser, and to verify every optimizer output

For a menu (7 days × 3 slots) and settings, compute:

- `cost_per_person_day` = mean over 7 days of the sum of the three items' `cost_per_unit`; `daily_total` = that × people.
- Weekly nutrient average per person per day, and `coverage[k] = average_k / target_k` (1.0 = 100%).
- Per-day coverage (so a bad single day is visible).
- Constraint statuses (see 8.1): budget, ingredients/stock, kitchen capacity, diet, **each nutrient**, variety.
- Contributors: which items supply each nutrient.

**Every plan returned by the optimizer is passed through the evaluator before being sent to the UI.** If the two ever disagree, return a 500 with a clear error. Never show unverified numbers.

### 7.2 Optimizer (`optimizer.py`) — one MILP formulation, three modes

Pre-filter items by `active`, `diet`, and slot. If any slot has no eligible item, report infeasible with that reason. If `people > kitchen_capacity`, report infeasible with that reason.

**Variables**
- `x_m ∈ {0, …, max_repeats}` integer: number of days item `m` is served in its slot.
- `t` continuous: the weakest nutrient's coverage ratio.

**Constraints**
- For each slot `s`: `Σ_{m∈s} x_m = 7`
- Nutrient `k`: `Σ_m x_m · n_{m,k} ≥ 7 · T_k · t`
- Budget (modes B and C): `Σ_m x_m · c_m ≤ 7 · (daily_budget / people)`
- Stock, per ingredient `i`: `people · Σ_m x_m · q_{m,i} ≤ stock_i`

**Modes**

| Mode | `t` bounds | Objective | Purpose |
|---|---|---|---|
| **A `min_cost`** | `t = 1` | minimize `Σ x_m c_m`, **no budget constraint** | True minimum feasible cost (for the funding gap) |
| **B `balanced`** | `1 ≤ t ≤ coverage_cap` | maximize `t − 0.01 · (Σ x_m c_m / 7)` | The plan shown when feasible |
| **C `best_effort`** | `0 ≤ t ≤ coverage_cap` | maximize `t` | Best plan within budget when full targets are impossible |

Use `scipy.optimize.milp` (integrality on `x`, continuous `t`). Do not hardcode any "minimum feasible cost", it must come from mode A.

### 7.3 Day assignment (`assign.py`)

The MILP decides *how many days* each dish is served. Then assign dishes to days: within each slot, spread repeats (no same dish on consecutive days) and pair breakfast/lunch/dinner so the **worst single day's coverage is as high as possible**. A simple randomized swap search (about 2,000 iterations, fixed seed) is sufficient. Weekly totals do not change, so this step cannot break feasibility. Report per-day coverage in the result.

### 7.4 Infeasibility diagnosis and alternatives (`diagnose.py`)

Only runs when mode B is infeasible.

1. **Binding constraints:** relax each hard constraint group one at a time (budget, stock, nutrition targets) and re-solve. Any group whose relaxation alone makes it feasible is listed as binding. If none works alone, report "combination".
2. **Minimum feasible cost** = mode A result (with stock enforced). `funding_gap_daily = min_cost_daily − daily_budget`. Also return `funding_gap_per_person`.
3. **Cheapest possible day** = sum of the cheapest eligible item per slot × people. If `daily_budget` is below this, no complete menu fits at all. Say so, and skip best-effort.
4. **Alternatives** (each carries a full evaluated plan the UI can preview):
   - **A `fund_gap`:** re-solve mode B with `daily_budget = min_cost_daily`.
   - **B `best_effort`:** mode C at the current budget. Label `meets_targets: false` and list `shortfalls` per nutrient.
   - **C `stock_change`** **(stretch)**: for each out-of-stock or low-stock ingredient, try restocking it and record the drop in minimum cost. Return the top one.
   - **D `combined`** **(stretch)**.
5. Order alternatives by smallest change first; return at most 4.

### 7.5 Swap suggestions (`swaps.py`) — deterministic, feeds the Analyser

For the weakest nutrient in an analysed menu, try replacing each of the 21 slots' items with every other eligible item in the same slot (respecting repeats, stock and diet). Rank by *coverage gain per extra rupee*. Return the top 3 as `{day, slot, from, to, delta_coverage, delta_cost_per_person}`. The LLM may only narrate these. It must never invent its own swaps.

---

## 8. API contract

Base path `/api`. All responses are JSON. Errors: `{ "error": "message", "details": {} }` with a proper status code.

| Method | Path | Purpose |
|---|---|---|
| GET/POST | `/food-items` | List (filter by `slot`, `active`) / create |
| PUT/DELETE | `/food-items/<id>` | Update / delete |
| GET/PUT | `/stock` | Read / update ingredient stock |
| GET/PUT | `/settings` | Read / update institution settings and targets |
| GET/PUT | `/menu` | Read / save the current week (manual edit) |
| GET | `/dashboard` | Summary of the current menu (evaluator output plus last run info and stock warnings) |
| POST | `/analyze` | Evaluate a menu (body `menu` optional, defaults to current). Add `?explain=true` for an LLM narrative |
| POST | `/balance` | Body: optional `overrides` (e.g. `{ "daily_budget": 15000 }`) and `apply` (bool, saves menu). Returns `PlanResult` |
| POST | `/whatif` | Body: `overrides`. Solves with overrides and returns `PlanResult` plus `diff` versus the current saved menu |
| POST | `/explain` | Body: a `PlanResult` or `AnalysisResult`. Returns `{ text, source: "llm" \| "template" }` |
| POST | `/food-items/estimate` **(stretch)** | LLM nutrient estimate for a new dish. Response is flagged `ai_estimate`, and the user must confirm before saving |
| POST | `/seed/reset` | Restore seed data (demo safety net) |
| GET | `/health` | Liveness check |

### 8.1 `PlanResult` (also the shape of `/analyze` output, minus `infeasibility`)

```json
{
  "feasible": true,
  "mode": "balanced",
  "inputs": { "people": 500, "daily_budget": 18000, "diet": "vegetarian", "kitchen_capacity": 500 },
  "menu": { "days": [ { "day": "MON",
      "breakfast": { "id": "…", "name": "Ragi Dosa + Chutney" },
      "lunch":     { "id": "…", "name": "Rice + Palak Dal" },
      "dinner":    { "id": "…", "name": "Chapati + Chana Curry" } } ] },
  "cost": { "per_person_day": 33.0, "daily_total": 16500, "budget": 18000, "remaining": 1500 },
  "nutrition": {
    "coverage": { "energy_kcal": 1.02, "protein_g": 1.05, "iron_mg": 1.00, "calcium_mg": 1.10 },
    "targets_met": true,
    "gaps": []
  },
  "per_day": [ { "day": "MON", "coverage": { "energy_kcal": 1.0, "protein_g": 1.1, "iron_mg": 1.0, "calcium_mg": 1.2 }, "cost_per_person": 31 } ],
  "constraints": [
    { "key": "budget",    "label": "Budget",            "status": "ok",   "detail": "₹16,500 of ₹18,000" },
    { "key": "stock",     "label": "Ingredients",       "status": "ok",   "detail": "All within stock" },
    { "key": "kitchen",   "label": "Kitchen capacity",  "status": "ok",   "detail": "500 of 500 meals" },
    { "key": "diet",      "label": "Dietary requirement","status": "ok",  "detail": "Vegetarian" },
    { "key": "nutrition", "label": "Nutrition targets", "status": "ok",   "detail": "All 4 nutrients at or above 100%" },
    { "key": "variety",   "label": "Variety",           "status": "ok",   "detail": "≥ 4 distinct dishes per meal slot" }
  ],
  "diff": null,
  "infeasibility": null,
  "explanation": { "text": "…", "source": "llm" }
}
```

Constraint `status` is `ok | warn | fail`. **`nutrition` must be `warn` or `fail` whenever any nutrient is below 100%**, and the page-level header state must reflect it (e.g. "Feasible · 1 nutrition gap"). Never show an all-green state with a gap.

`diff` (what-if): `{ "cost_daily": {"before": 16500, "after": 14900}, "coverage": {…before/after per nutrient…}, "changed_meals": [ { "day": "TUE", "slot": "lunch", "from": "…", "to": "…" } ] }`

### 8.2 `infeasibility` object

```json
{
  "feasible": false,
  "binding": ["budget"],
  "min_feasible_cost_daily": 16500,
  "funding_gap_daily": 1500,
  "funding_gap_per_person": 3.0,
  "cheapest_possible_day_daily": 13000,
  "alternatives": [
    { "id": "A", "type": "fund_gap",    "change": { "daily_budget": 16500 }, "plan": { } },
    { "id": "B", "type": "best_effort", "meets_targets": false,
      "shortfalls": { "iron_mg": 0.11, "protein_g": 0.05 }, "plan": { } }
  ]
}
```

When infeasible, the top-level `PlanResult` has `feasible: false`, `menu: null`, and `infeasibility` populated.

---

## 9. LLM layer (Groq, explain-only)

**Env:** `GROQ_API_KEY`, `GROQ_MODEL`. Choose a current model from Groq's console. Do not hardcode a model name. The key stays server-side, never in the frontend.

**Calls:** only from `services/explain.py`, with a hard timeout of about 8 seconds, `temperature ≤ 0.3`, and input limited to the computed result JSON (menu, cost, coverage, constraints, swap suggestions, infeasibility). Strip anything else.

**System prompt:**

```
You are a meal-plan explanation assistant for an institutional mess manager.
Explain the supplied result in simple, plain language, in at most 120 words.
Use ONLY the numbers and dish names present in the supplied JSON.
Do NOT create, modify, validate or recommend meals. Do NOT calculate or invent
nutrition values, prices, ingredients or constraints. You may only mention swap
suggestions that appear in the input's "swap_suggestions" list.
Cover, when present in the input: why this plan was chosen; which nutrients are
below target and by how much; what changed after a what-if; and, if infeasible,
which constraint is binding and the funding gap.
If a nutrient is below 100%, state it clearly. Never describe such a plan as fully
meeting targets. Do not use markdown.
```

**Fallback:** if the call fails, times out, or returns empty text, generate a template string from the same JSON (e.g. "Iron is at 56% of target. Swapping X for Y on TUE lunch raises it to 71% for ₹2 more per person.") and return `source: "template"`. The UI shows a small "AI" or "auto-generated" tag accordingly.

---

## 10. Pages (what each must do)

1. **Dashboard:** weekly cost vs budget, per-nutrient coverage bars (amber under 100%), constraint checklist including nutrition, stock warnings, and a link to Balancer.
2. **Food Items:** table with search and slot filter. Add, edit and delete dish (name, slot, ₹ per serving, four nutrients, diet, ingredients). Inline stock editor. "Reset demo data" button.
3. **Mess Menu:** 7-day × 3-slot grid. Each cell is a dropdown of eligible items for that slot. Live totals (cost and coverage) update via `/analyze` on every change. Save button.
4. **Analyser:** run analysis on the current or edited menu. Show coverage bars, per-day coverage, contributors, gaps, ranked swap suggestions, and an AI explanation. A "Preview swap" action applies a suggestion to a draft menu and shows the change in coverage and cost.
5. **Balancer:** the settings panel (people, budget, diet, kitchen capacity, stock toggles), a **Generate plan** button, and the resulting plan with the constraint checklist. A budget slider drives the **what-if** with before/after comparison. When infeasible, show the **InfeasibleState**: why it fails, funding gap in ₹/day and ₹/person, and one `AlternativeCard` per alternative with a **Preview** button. An **Apply to menu** button saves the plan.

---

## 11. Seed data

Seed `food_items` from Appendix A and `stock` with **2,000 units of every ingredient** (generous so stock does not bind by default). Set Milk stock to 0 during the demo to show the ingredient constraint. Seed `settings` with the values in section 6. Seed a "habitual" starter menu (see acceptance test 1) into `menus`. `seed.py` must be idempotent and callable from `POST /seed/reset`.

---

## 12. Acceptance tests (with seed data; must pass before demo)

| # | Scenario | Expected |
|---|---|---|
| 1 | Analyse the habitual menu: Idli + Milk / Curd Rice + Veg / Veg Pulao + Raita, all 7 days | ₹32/person, ₹16,000/day. Coverage: energy 98%, **protein 84%, iron 56%**, calcium 138%. Nutrition constraint is not green. |
| 2 | Mode A minimum cost (seed, full stock, max 2 repeats) | ₹33.00/person/day, i.e. **₹16,500/day** |
| 3 | Balance at ₹18,000/day | Feasible, all four coverages ≥ 100%, cost ≤ ₹18,000, ≥ 4 distinct dishes per slot. Evaluator agrees with optimizer. |
| 4 | What-if ₹15,000/day | Infeasible. Gap **₹1,500/day (₹3/person)**. Alternative B best-effort at about 89% minimum coverage, labeled "does not meet targets". Alternative A at ₹16,500 feasible. |
| 5 | Balance at ₹8,000/day | Infeasible. Cheapest possible day is **₹13,000**, so no complete menu fits. Message says so. Alternative A is offered. |
| 6 | Milk stock set to 0, balance at ₹18,000 | Plan contains no Idli + Milk. Either a valid plan or a clear infeasibility explanation. |
| 7 | `kitchen_capacity` set below `people` | Infeasible with an explicit kitchen reason. |
| 8 | Groq key removed or invalid | Everything works. Explanations come from templates with `source: "template"`. |
| 9 | Edit a dish's price in Food Items, then re-analyse | Costs and results change accordingly. |

Automate tests 1 to 5 and 7 in `pytest`.

---

## 13. Environment variables

```
# backend/.env
MONGO_URI=mongodb://localhost:27017
DB_NAME=nutriplan
GROQ_API_KEY=
GROQ_MODEL=
FRONTEND_ORIGIN=http://localhost:5173
PORT=5000

# frontend/.env
VITE_API_URL=http://localhost:5000/api
```

`backend/requirements.txt`: `flask`, `flask-cors`, `pymongo`, `pydantic`, `numpy`, `scipy`, `python-dotenv`, `groq`, `gunicorn`, `pytest`

**Run:**

```
cd backend && pip install -r requirements.txt && python seed/seed.py && flask --app app run --port 5000
cd frontend && npm install && npm run dev
```

---

## 14. Build order (about 2 hours)

1. **(15 min)** Flask skeleton, Mongo connection, seed script, `/food-items`, `/stock`, `/settings`, `/menu` CRUD. Frontend scaffold with routing and layout.
2. **(20 min)** `nutrition.py` evaluator and `/analyze`, with tests 1 and 9. Mess Menu page and Analyser page wired to it.
3. **(30 min)** `optimizer.py` (modes A, B, C), `assign.py`, `/balance`. Tests 2 to 3.
4. **(20 min)** `diagnose.py` (binding constraints, funding gap, alternatives A and B), `/whatif`. Tests 4, 5, 7. Balancer page with InfeasibleState.
5. **(15 min)** `swaps.py`, `explain.py` with template fallback first, then Groq. Dashboard page.
6. **(20 min)** Integrate, run all acceptance tests, fix, deploy or rehearse.

**Cut in this order if late:** Dashboard polish, alternatives C and D, `/food-items/estimate`, deployment (run locally).

---

## 15. Non-goals

Authentication and roles, a custom ML model, LLM-generated menus, IoT/hardware/blockchain, supplier marketplace, mobile app, payments, notifications, a production-grade nutrient database.

---

## Appendix A — Seed dishes (sample data, per 1 person serving)

All `diet: vegetarian`. Quantities in `ingredients` are per serving (kg, L or unit). Label the whole set "sample data" in the UI.

| Name | Slot | ₹ | kcal | Protein g | Iron mg | Calcium mg | Ingredients (per serving) |
|---|---|---|---|---|---|---|---|
| Idli + Sambar | breakfast | 8 | 330 | 10 | 2.2 | 70 | rice 0.05 kg, dal 0.02 kg |
| Upma + Banana | breakfast | 7 | 340 | 7 | 1.8 | 30 | semolina 0.06 kg, banana 1 unit |
| Poha + Peanuts | breakfast | 8 | 360 | 10 | 3.6 | 40 | poha 0.06 kg, groundnut 0.02 kg |
| Ragi Dosa + Chutney | breakfast | 8 | 340 | 9 | 4.0 | 200 | ragi 0.06 kg |
| Pongal | breakfast | 9 | 380 | 12 | 2.6 | 55 | rice 0.05 kg, dal 0.02 kg |
| Idli + Milk | breakfast | 11 | 380 | 14 | 1.9 | 250 | rice 0.05 kg, milk 0.2 L |
| Rice + Dal + Veg Curry | lunch | 13 | 620 | 19 | 4.8 | 110 | rice 0.10 kg, dal 0.04 kg, vegetables 0.10 kg |
| Rice + Sambar + Poriyal | lunch | 11 | 570 | 15 | 4.2 | 95 | rice 0.10 kg, dal 0.03 kg, vegetables 0.12 kg |
| Rice + Chana Masala | lunch | 12 | 620 | 19 | 5.8 | 110 | rice 0.10 kg, chana 0.05 kg |
| Rice + Rajma | lunch | 14 | 640 | 21 | 6.0 | 130 | rice 0.10 kg, rajma 0.05 kg |
| Rice + Palak Dal | lunch | 13 | 600 | 19 | 7.0 | 160 | rice 0.10 kg, dal 0.04 kg, spinach 0.08 kg |
| Curd Rice + Veg | lunch | 10 | 520 | 12 | 2.0 | 210 | rice 0.10 kg, curd 0.15 kg, vegetables 0.08 kg |
| Rice + Paneer Curry | lunch | 21 | 650 | 21 | 2.6 | 290 | rice 0.10 kg, paneer 0.06 kg |
| Chapati + Dal | dinner | 11 | 570 | 17 | 4.5 | 85 | wheat 0.10 kg, dal 0.04 kg |
| Chapati + Chana Curry | dinner | 12 | 600 | 19 | 5.5 | 95 | wheat 0.10 kg, chana 0.05 kg |
| Chapati + Mixed Veg | dinner | 9 | 490 | 11 | 3.6 | 70 | wheat 0.10 kg, vegetables 0.15 kg |
| Chapati + Soya Curry | dinner | 12 | 600 | 23 | 5.2 | 90 | wheat 0.10 kg, soya 0.04 kg |
| Veg Pulao + Raita | dinner | 11 | 570 | 12 | 2.8 | 160 | rice 0.10 kg, vegetables 0.08 kg, curd 0.10 kg |
| Chapati + Paneer Curry | dinner | 21 | 620 | 21 | 2.7 | 280 | wheat 0.10 kg, paneer 0.06 kg |
| Khichdi + Curd | dinner | 10 | 550 | 16 | 3.8 | 170 | rice 0.07 kg, dal 0.04 kg, curd 0.10 kg |

Note: the nutrient values are illustrative demo values, not IFCT measurements. Acceptance tests 1 to 5 depend on these exact numbers.