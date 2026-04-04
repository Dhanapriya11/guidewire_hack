# GigShield Phase 2 — Run Guide

## Folder Structure
```
GigShield_Phase2/
├── backend/
│   ├── train_model.py    ← Run once to train ML model
│   └── app.py            ← Flask API server
└── frontend/
    ├── src/
    │   ├── App.js
    │   ├── data.js
    │   └── components/
    │       ├── Registration.jsx
    │       ├── PolicyManagement.jsx
    │       ├── PremiumCalculator.jsx   ← ML-powered
    │       ├── ClaimsManagement.jsx
    │       ├── SeettuPool.jsx
    │       └── AutoTriggerEngine.jsx   ← NEW Phase 2
    └── package.json
```

---

## Step 1 — Install Python packages
```bash
pip install scikit-learn pandas numpy flask flask-cors joblib
```

## Step 2 — Train ML model (run ONCE)
```bash
cd backend
python train_model.py
```
You will see:
```
✓ Saved district_risk_profile.csv
✓ Model trained — MAE: ~3 pts | R²: ~0.97
✓ Saved: gigshield_model.pkl
```

## Step 3 — Start Flask backend
```bash
cd backend
python app.py
```
Keep this terminal open. API runs at http://localhost:5000

## Step 4 — Start React (new terminal)
```bash
cd frontend
npm install
npm start
```
App opens at http://localhost:3000

---

## Demo flow for judges

1. Register → fill worker form → submit
2. Policy → create policy for that worker
3. Premium (ML) → change district → see ML score + feature importance bars
4. Auto-Triggers → click "▶ Start Monitoring" → click "🌧 Heavy Rainfall" → watch claim auto-fire
5. Claims → see auto-filed claim with fraud check result
6. சீட்டு Pool → see pool balance updated

---

## What the ML model does

- Algorithm: RandomForestRegressor (150 trees)
- Trained on: 3,300 rows of Indian weather data (25 districts × 11 years × 12 months)
- Features: district, month, rainfall, avg_temp, max_temp, wind_speed
- Output: risk_score (0–130) → weekly premium (₹20–60)
- Shown in UI: feature importance bar chart
