You are working on the NutriPlan hackathon project.

IMPORTANT:
Do NOT build new UI features yet.
Do NOT redesign the existing frontend.
Do NOT replace the existing product architecture.
The immediate priority is to establish and verify a complete working React/Vite → Flask API → MongoDB connection.

==================================================
CURRENT GOAL
==================================================

Connect the existing React + Vite frontend to the existing Flask backend.

The backend is already implemented and should be treated as the source of truth for:
- nutrition calculations
- cost calculations
- menu calculations
- constraint validation
- analyzer results
- balancer suggestions
- applying menu changes

The frontend should only consume and display backend results.

Do NOT duplicate backend calculations in React.

==================================================
BACKEND API CONTRACT
==================================================

Backend runs locally at:

http://localhost:5000

API prefix:

/api

Existing endpoints:

HEALTH
GET /api/health

FOODS
GET /api/foods
POST /api/foods
GET /api/foods/<id>
PUT /api/foods/<id>
DELETE /api/foods/<id>

AI FOOD NUTRITION
POST /api/foods/analyze-nutrition

MENU
GET /api/menu
POST /api/menu
PUT /api/menu/<id>

ANALYZER
POST /api/analyze

BALANCER
POST /api/balance

APPLY BALANCE
POST /api/balance/apply

SETTINGS
GET /api/settings
PUT /api/settings

SEED RESET
POST /api/seed/reset

Do NOT invent additional endpoints.

Do NOT assume endpoints such as:
- /api/dashboard
- /api/whatif
- /api/explain
- /api/food-items
unless they actually exist in the backend code.

Inspect the actual backend source before implementing the frontend client.

==================================================
RESPONSE FORMAT
==================================================

Backend generally uses:

SUCCESS:

{
  "success": true,
  "data": {}
}

ERROR:

{
  "success": false,
  "error": {
    "message": "Human readable error message",
    "code": "OPTIONAL_ERROR_CODE"
  }
}

Handle this structure correctly.

IMPORTANT:

GET /api/foods returns:

{
  "success": true,
  "data": [
    {...},
    {...}
  ]
}

NOT:

{
  "data": {
    "foods": [...]
  }
}

Do not make incorrect assumptions about the response shape.

==================================================
FOOD OBJECT
==================================================

Food objects currently resemble:

{
  "_id": "...",
  "name": "Idli + Sambar",
  "category": "Breakfast",
  "servingSize": 100,
  "unit": "g",
  "price": 8,
  "availableQuantity": 50,
  "dietaryTags": ["vegetarian"],
  "nutrition": {
    "calories": 330,
    "protein": 10,
    "carbohydrates": 55,
    "fat": 5,
    "fiber": 4,
    "iron": 2.2,
    "calcium": 70
  },
  "nutritionSource": "sample"
}

Use the actual backend models as the authoritative structure.

==================================================
MENU API
==================================================

GET /api/menu returns something similar to:

{
  "success": true,
  "data": {
    "menu": {},
    "summary": {}
  }
}

The backend calculates the authoritative menu summary.

Do not recalculate:
- total cost
- nutrition coverage
- budget status
- nutrient gaps

in the frontend.

Display the backend values.

==================================================
ANALYZER
==================================================

POST:

/api/analyze

Request:

{
  "menuId": "..."
}

The backend performs the authoritative:
- nutrition analysis
- cost analysis
- coverage calculation
- gap detection

Frontend should display the returned result.

==================================================
BALANCER
==================================================

POST:

/api/balance

Minimum request:

{
  "menuId": "..."
}

The backend returns suggestions.

Suggestion objects may contain:

{
  "day": "Wednesday",
  "meal": "evening",
  "currentFood": "Veg Pulao + Raita",
  "currentFoodId": "...",
  "suggestedFood": "Chapati + Chana Curry",
  "suggestedFoodId": "...",
  "additionalCost": 500,
  "nutritionImprovement": {
    "nutrient": "iron",
    "percentage": 12
  },
  "budgetValid": true,
  "dietValid": true,
  "availabilityValid": true,
  "newCoverage": {}
}

Do not invent a suggestionId.

==================================================
APPLY BALANCE
==================================================

POST:

/api/balance/apply

Request structure is approximately:

{
  "menuId": "...",
  "suggestion": {
    "day": "Wednesday",
    "meal": "evening",
    "currentFoodId": "...",
    "suggestedFoodId": "..."
  }
}

Inspect the actual backend route/service before implementing this.

After applying a suggestion:

1. Re-fetch the menu.
2. Re-run analysis if necessary.
3. Update the frontend using the backend response.
4. Do not locally fake the result.

==================================================
AI NUTRITION ENDPOINT
==================================================

POST:

/api/foods/analyze-nutrition

Request:

{
  "name": "Chana Curry",
  "servingSize": 100,
  "unit": "g"
}

The backend may use:
- Groq
- Ollama
- deterministic fallback

The frontend must NOT directly call Groq or Ollama.

Frontend only calls the Flask endpoint.

The response may contain:

{
  "nutrition": {...},
  "source": "groq",
  "confidence": "medium",
  "warning": "AI estimated values should be verified before operational use."
}

Display source/warning appropriately.

==================================================
STEP 1 — INSPECT PROJECT
==================================================

Before changing anything:

1. Inspect the repository structure.
2. Locate the actual React/Vite frontend.
3. Locate the actual Flask backend.
4. Inspect:
   - backend/app.py
   - backend/routes/*
   - backend/models/*
   - backend/services/*
   - backend/config.py
5. Inspect the existing frontend architecture.
6. Determine whether an API client already exists.

Do NOT create duplicate API clients.

Do NOT migrate the project to Next.js.

The frontend MUST remain React + Vite.

==================================================
STEP 2 — CENTRALIZED API CLIENT
==================================================

Create or update a single centralized API client.

Preferred location:

frontend/src/api/client.js

or the existing equivalent location if the project already has one.

All frontend API calls must go through this client.

Expose functions similar to:

getHealth()
getFoods()
getFood(id)
createFood(food)
updateFood(id, food)
deleteFood(id)

analyzeFoodNutrition(payload)

getMenu()
createMenu(payload)
updateMenu(id, payload)

analyzeMenu(menuId)

balanceMenu(menuId)
applyBalance(menuId, suggestion)

getSettings()
updateSettings(settings)

Do not scatter fetch/axios calls throughout components.

==================================================
STEP 3 — ENVIRONMENT CONFIG
==================================================

Use:

VITE_API_URL

Example local value:

VITE_API_URL=http://localhost:5000/api

Do not hardcode the API URL throughout the application.

Create/update:

.env.example

if necessary.

Do not expose secrets in the frontend.

Especially:
- GROQ_API_KEY must NEVER be placed in Vite frontend code.
- Ollama configuration must remain backend-side.

==================================================
STEP 4 — VITE / CORS
==================================================

Make the minimum required changes so React/Vite can communicate with Flask locally.

If the backend already has CORS configured correctly, do not unnecessarily modify it.

If Vite proxy is useful, configure it cleanly.

Avoid creating multiple competing API base URL mechanisms.

==================================================
STEP 5 — CONNECT EXISTING PAGES
==================================================

Connect the existing frontend pages to real backend data.

Pages:

1. Dashboard
2. Food Items
3. Mess Menu
4. Nutrient Analyzer
5. Menu Balancer

Do not redesign these pages.

Only replace hardcoded/demo API-dependent values where necessary with real backend data.

The UI should preserve the existing NutriPlan visual style.

==================================================
STEP 6 — LOADING / ERROR STATES
==================================================

Every API-driven page must have basic:

- loading state
- error state
- empty state where applicable

Use simple existing UI patterns.

Do NOT introduce a large state-management library unless the project already uses one.

Do NOT over-engineer.

==================================================
STEP 7 — TEST THE CONNECTION
==================================================

After implementation, actually run the frontend and backend if possible.

Verify in this exact order:

TEST 1:

GET /api/health

Expected:
successful backend response.

TEST 2:

GET /api/foods

Expected:
seeded food data is returned.

There should currently be seeded food records.

TEST 3:

GET /api/menu

Expected:
current menu and summary are returned.

TEST 4:

POST /api/analyze

Use the actual menuId returned by the backend.

Expected:
nutrition/cost/gap analysis returned.

TEST 5:

POST /api/balance

Use the actual menuId.

Expected:
backend-generated balance suggestions or an honest no-suggestion/infeasible response.

TEST 6:

POST /api/balance/apply

Use an actual returned suggestion.

Expected:
backend updates MongoDB.

Then:

GET /api/menu

again.

Verify that the menu actually changed.

Then run:

POST /api/analyze

again.

Verify that the analysis reflects the updated menu.

==================================================
IMPORTANT ARCHITECTURE RULE
==================================================

The flow must be:

React UI
   ↓
centralized API client
   ↓
Flask REST API
   ↓
backend services
   ↓
MongoDB

NOT:

React
   ↓
local calculations
   ↓
fake result

The backend is authoritative.

==================================================
DO NOT DO THESE
==================================================

Do NOT:

- redesign the UI
- create a landing page
- add authentication
- add payments
- add notifications
- add chatbot UI
- add maps
- add hardware integrations
- add unnecessary animations
- add Redux/Zustand/etc. unless already required
- add a second backend
- migrate to Next.js
- rewrite Flask
- rewrite the database layer
- move Groq/Ollama calls into React
- hardcode nutrition totals
- hardcode cost totals
- hardcode coverage percentages
- fake optimizer/balancer results
- invent API endpoints
- invent API response fields
- use suggestionId unless the actual backend provides it

==================================================
CRITICAL DATA INTEGRITY RULE
==================================================

Never make the frontend authoritative for:

- cost
- nutrition
- nutrient coverage
- nutrient gaps
- budget validity
- dietary validity
- stock/availability validity
- kitchen constraints
- balance suggestions
- final menu validity

These come from the backend.

Frontend is responsible for:
- collecting input
- calling APIs
- displaying results
- showing loading/errors
- allowing the user to apply valid backend suggestions

==================================================
SUCCESS CRITERIA
==================================================

The task is complete ONLY when:

1. React/Vite starts successfully.
2. Flask backend starts successfully.
3. React can reach Flask.
4. Health check works.
5. Real MongoDB food data appears in the frontend.
6. Real MongoDB menu data appears in the frontend.
7. Analyzer uses the real backend endpoint.
8. Balancer uses the real backend endpoint.
9. Applying a balance suggestion updates MongoDB.
10. Re-fetching the menu shows the actual updated data.
11. No API-dependent hardcoded values remain where backend data exists.
12. No frontend-side duplicate nutrition/cost calculations were introduced.
13. No Groq/Ollama secrets are exposed to the browser.
14. Existing NutriPlan UI design remains intact.

==================================================
FINAL REPORT
==================================================

When finished, do NOT just say "done".

Report:

### FE ↔ BE Integration Status

- Frontend URL:
- Backend URL:
- API base URL:
- MongoDB connection:
- CORS/proxy:
- API client location:

### Endpoint Verification

| Endpoint | Method | Status | Notes |
|---|---|---|---|
| /api/health | GET | | |
| /api/foods | GET | | |
| /api/menu | GET | | |
| /api/analyze | POST | | |
| /api/balance | POST | | |
| /api/balance/apply | POST | | |
| /api/settings | GET | | |
| /api/foods/analyze-nutrition | POST | | |

### Files Changed

List every file changed.

### Remaining Issues

List only real remaining issues.

If an endpoint cannot be tested because of an external dependency such as MongoDB not running, clearly state that instead of claiming it works.

STOP after FE ↔ BE integration is working.

Do NOT continue into additional UI feature development.