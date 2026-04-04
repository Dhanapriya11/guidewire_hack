"""
GigShield — ML Risk Model Trainer
===================================
Run this ONCE to train the model and save it.

    pip install scikit-learn pandas numpy joblib
    python train_model.py

This generates:
  - district_risk_profile.csv   (training data)
  - gigshield_model.pkl         (trained RandomForest)
  - label_encoder.pkl           (district name encoder)
"""

import pandas as pd
import numpy as np
import joblib
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score

np.random.seed(42)

# ── 1. Synthetic historical weather data (mimics Kaggle Indian Rainfall dataset) ──
# Real columns: district, state, rainfall_mm, avg_temp, max_temp, wind_speed
DISTRICT_PROFILES = {
    # (state, base_rainfall, base_temp, base_wind, true_risk)
    "Mumbai Suburban":    ("Maharashtra",  320, 29, 22, 128),
    "Mumbai City":        ("Maharashtra",  310, 30, 20, 125),
    "Ratnagiri":          ("Maharashtra",  290, 28, 18, 118),
    "Dhubri":             ("Assam",        270, 27, 16, 115),
    "Chennai":            ("Tamil Nadu",   260, 32, 19, 110),
    "Kolkata":            ("West Bengal",  250, 30, 15, 105),
    "West Tripura":       ("Tripura",      245, 28, 14, 103),
    "Goalpara":           ("Assam",        240, 27, 13, 101),
    "Puri":               ("Odisha",       230, 31, 17, 100),
    "Nagapattinam":       ("Tamil Nadu",   225, 31, 18,  95),
    "Nagpur":             ("Maharashtra",  210, 33, 15,  98),
    "Nainital":           ("Uttarakhand",  220, 22, 16,  97),
    "Rajkot":             ("Gujarat",      215, 34, 20,  96),
    "Bhopal":             ("Madhya Pradesh",200, 30, 12, 94),
    "Tirunelveli":        ("Tamil Nadu",   195, 32, 17,  92),
    "Thiruvananthapuram": ("Kerala",       190, 30, 14,  91),
    "Madurai":            ("Tamil Nadu",   185, 33, 15,  89),
    "Bangalore":          ("Karnataka",    180, 26, 13,  88),
    "Vizag":              ("Andhra Pradesh",175, 30, 16, 88),
    "Pune":               ("Maharashtra",  170, 28, 12,  85),
    "Surat":              ("Gujarat",      165, 32, 18,  80),
    "Delhi":              ("Delhi",        145, 29, 14,  72),
    "Ahmedabad":          ("Gujarat",      140, 34, 16,  75),
    "Coimbatore":         ("Tamil Nadu",   155, 29, 13,  78),
    "Hyderabad":          ("Telangana",    160, 31, 14,  82),
}

MONTHS = list(range(1, 13))
YEARS = list(range(2013, 2024))  # 10+ years

rows = []
for district, (state, base_rain, base_temp, base_wind, true_risk) in DISTRICT_PROFILES.items():
    for year in YEARS:
        for month in MONTHS:
            # Seasonal modifiers
            if month in [6, 7, 8, 9]:   season_rain = 2.5; season_temp = 1.05
            elif month in [3, 4, 5]:     season_rain = 0.8; season_temp = 1.15
            elif month in [10, 11]:      season_rain = 1.2; season_temp = 0.95
            else:                        season_rain = 0.4; season_temp = 0.85

            rainfall    = max(0, base_rain * season_rain + np.random.normal(0, 30))
            avg_temp    = base_temp * season_temp + np.random.normal(0, 1.5)
            max_temp    = avg_temp + np.random.uniform(3, 8)
            wind_speed  = base_wind + np.random.normal(0, 3)

            # Risk score derived from features (what the model will learn to predict)
            # Formula matches GigShield's domain logic:
            #   rain heavily weighted, then max_temp extremes, then wind
            risk = (
                0.40 * min(rainfall / 3.5, 60) +
                0.25 * min(max(max_temp - 38, 0) * 8, 30) +
                0.20 * min(wind_speed / 1.2, 25) +
                0.15 * np.random.uniform(0, 15)  # disruption-rate noise
            )
            risk = max(0, min(130, risk + np.random.normal(0, 4)))

            rows.append({
                "district":    district,
                "state":       state,
                "year":        year,
                "month":       month,
                "rainfall_mm": round(rainfall, 1),
                "avg_temp":    round(avg_temp, 1),
                "max_temp":    round(max_temp, 1),
                "wind_speed":  round(wind_speed, 1),
                "risk_score":  round(risk, 2),
            })

df = pd.DataFrame(rows)
df.to_csv("district_risk_profile.csv", index=False)
print(f"✓ Saved district_risk_profile.csv — {len(df)} rows, {df['district'].nunique()} districts")

# ── 2. Feature engineering ──
le = LabelEncoder()
df["district_enc"] = le.fit_transform(df["district"])

FEATURES = ["district_enc", "month", "rainfall_mm", "avg_temp", "max_temp", "wind_speed"]
X = df[FEATURES]
y = df["risk_score"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ── 3. Train RandomForest ──
model = RandomForestRegressor(
    n_estimators=150,
    max_depth=12,
    min_samples_leaf=4,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mae   = mean_absolute_error(y_test, y_pred)
r2    = r2_score(y_test, y_pred)
print(f"✓ Model trained — MAE: {mae:.2f} risk pts | R²: {r2:.4f}")

# ── 4. Compute per-district annual risk score (average monsoon months) ──
monsoon = df[df["month"].isin([6, 7, 8, 9])].copy()
district_risk = (
    monsoon.groupby("district")["risk_score"]
    .mean()
    .round(1)
    .to_dict()
)
print("\n📊 District Risk Scores (monsoon avg):")
for d, s in sorted(district_risk.items(), key=lambda x: -x[1]):
    print(f"   {d:<28} {s:>6.1f}/130")

# ── 5. Save model artifacts ──
joblib.dump(model, "gigshield_model.pkl")
joblib.dump(le,    "label_encoder.pkl")
with open("district_risk_scores.json", "w") as f:
    json.dump(district_risk, f, indent=2)

print("\n✓ Saved: gigshield_model.pkl, label_encoder.pkl, district_risk_scores.json")
print("→ Now run: python app.py")
