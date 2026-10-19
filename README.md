# ZeroBite AI – AI-Powered Smart Food Donation Management System

This is the upgraded B.Tech final-year project built on the supplied React + Django REST + scikit-learn architecture.

## Implemented workflow

1. **Create an account** – Donor, NGO and Volunteer roles have separate dashboards and backend permissions.
2. **Post surplus food** – Donors enter only:
   - Food name (required)
   - Food type (required)
   - Quantity in meals (required)
   - Prepared Date & Time (required)
   - Pickup location (required)
   - Notes (optional)
3. **AI calculates expiry** – The donor does not enter expiry time. The expiry model estimates a shelf-life window from food type and prepared time, then creates `expiry_at` automatically.
4. **ML prioritizes rescue** – The existing Random Forest priority model uses the AI-estimated rescue window plus quantity, demand, reliability and distance feature(s) to produce a 0–100 rescue score and LOW/MEDIUM/HIGH/CRITICAL label.
5. **Request pickup** – NGOs and volunteers can request available food.
6. **Track status** – Donor accepts a pending request; the requesting NGO/volunteer marks it collected and then delivered. Expiry is automatically enforced.
7. **Secure access** – JWT authentication plus backend role checks protect actions.
8. **Measure impact** – Dashboard metrics show donations, active food, rescued meals and AI priority counts.
9. **Location-aware handoff** – The system stores a human-readable pickup location. Latitude and longitude are intentionally not collected in the donor form, per the project requirement.
10. **Live refresh** – Food listings and dashboards refresh every 10 seconds for demonstration.

## AI / ML architecture

```text
Donor input
  ↓
Food type + Prepared Date & Time
  ↓
AI expiry model (scikit-learn Random Forest)
  ↓
AI-estimated expiry_at / rescue window
  ↓
ML rescue-priority model (scikit-learn Random Forest)
  ↓
0–100 score + LOW / MEDIUM / HIGH / CRITICAL
  ↓
Donation saved → NGO/Volunteer pickup workflow
```

The project includes two models:
- `backend/ml/models/food_expiry.joblib` – generated from `backend/ml/data/expiry_training_data.csv`.
- `backend/ml/models/rescue_priority.joblib` – generated from `backend/ml/data/training_data.csv`.

Both models are automatically trained if the `.joblib` file is missing.

### Academic note
The included datasets are synthetic starter/demo datasets. The models are genuine scikit-learn pipelines, but their outputs should not be presented as validated real-world food-safety predictions. For a dissertation evaluation, replace the starter data with a larger historical/validated dataset and report appropriate model metrics.

## Windows quick start

1. Install Python 3.11/3.12 and Node.js 20+.
2. Run `setup_windows.bat`.
3. Open `http://localhost:5173`.

If PowerShell blocks `npm.ps1`, use `npm.cmd install` and `npm.cmd run dev` from the frontend folder.

### Demo accounts
- `donor_demo` / `ZeroBite@123`
- `ngo_demo` / `ZeroBite@123`
- `volunteer_demo` / `ZeroBite@123`

### Demo flow

Open two browser sessions:

**Donor:**
1. Log in.
2. Open **Donate**.
3. Enter food name, type, quantity, prepared time and pickup location.
4. Leave Notes empty or add optional notes.
5. Click **Publish & run AI**.
6. The result shows AI-estimated expiry and rescue priority.

**NGO/Volunteer:**
1. Log in in the second session.
2. Open **Find food**.
3. Choose an available donation and click **Request pickup**.
4. Open Dashboard and see the request.

**Donor:**
1. Return to the donor dashboard.
2. Accept the pending request.

**NGO/Volunteer:**
1. Mark the accepted request **collected**.
2. Mark it **delivered**.
3. Dashboard impact metrics update automatically.

## MySQL mode

Create a database named `zerobite_db`, set `DB_ENGINE=mysql` and the MySQL credentials in `backend/.env`, then run:

```text
cd backend
python manage.py migrate
python ml/train_model.py
python ml/expiry_model.py
python manage.py seed_demo
python manage.py runserver
```

In another terminal:

```text
cd frontend
npm install
npm run dev
```

SQLite remains the default for the easiest Windows demo.

## Main endpoints

- `GET /health/`
- `POST /api/auth/register/`
- `POST /api/auth/token/`
- `POST /api/auth/token/refresh/`
- `GET /api/auth/me/`
- `GET/POST /api/donations/donations/`
- `GET /api/donations/donations/recommended/`
- `GET /api/donations/donations/my/`
- `GET /api/donations/donations/stats/`
- `POST /api/donations/donations/<id>/request_pickup/`
- `GET /api/donations/pickup-requests/`
- `POST /api/donations/pickup-requests/<id>/accept/`
- `POST /api/donations/pickup-requests/<id>/status/`


### Dynamic AI rescue score
The rescue-priority model is recalculated for active donations when dashboards/recommendations are loaded. The live score uses the remaining AI-estimated rescue window, quantity, food type, donor rescue history, and a current food-type scarcity/demand proxy. Latitude/longitude are not required.

The starter training data is synthetic for demonstration; real deployment should retrain with validated historical rescue data.
