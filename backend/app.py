"""
GigShield — Flask Backend API
===============================
Run after training the model:

    pip install flask flask-cors scikit-learn pandas numpy joblib requests
    python train_model.py   (first time only)
    python app.py

API runs at http://localhost:5000
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import joblib
import json
import math
import random
import threading
import time
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # Allow React (localhost:3000) to call this API

# ── Load ML model ──────────────────────────────────────────────────────────────
try:
    model         = joblib.load("gigshield_model.pkl")
    label_encoder = joblib.load("label_encoder.pkl")
    with open("district_risk_scores.json") as f:
        DISTRICT_RISK_SCORES = json.load(f)
    print("✓ ML model loaded successfully")
except FileNotFoundError:
    print("⚠ Model not found — run train_model.py first")
    model = label_encoder = None
    DISTRICT_RISK_SCORES = {}

# ── In-memory state (replace with DB in production) ───────────────────────────
workers  = []
policies = []
claims   = []
pool     = {"balance": 50000.0, "total_premiums": 50000.0, "total_payouts": 0.0}

# ── Mock environment state for auto-triggers ──────────────────────────────────
env_state = {
    "weather": {
        "Chennai":    {"rainfall_mm": 12, "temp": 31, "wind": 18},
        "Mumbai":     {"rainfall_mm": 8,  "temp": 30, "wind": 20},
        "Bangalore":  {"rainfall_mm": 5,  "temp": 26, "wind": 13},
        "Hyderabad":  {"rainfall_mm": 3,  "temp": 32, "wind": 14},
        "Kolkata":    {"rainfall_mm": 9,  "temp": 29, "wind": 15},
    },
    "alerts": {
        "curfew":  False,
        "strike":  False,
        "flood":   False,
    },
    "last_updated": datetime.now().isoformat()
}

active_disruptions = []   # fired triggers waiting for payout
trigger_log        = []   # history of all triggers


# ══════════════════════════════════════════════════════════════════════════════
# ML ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/ml/risk-score", methods=["POST"])
def predict_risk():
    """
    Predict risk score for a district using the trained RandomForest model.

    Body: { district, month (1-12), rainfall_mm, avg_temp, max_temp, wind_speed }
    Returns: { risk_score, risk_tier, confidence, feature_importance }
    """
    if model is None:
        return jsonify({"error": "Model not loaded. Run train_model.py first."}), 503

    data = request.json
    district     = data.get("district", "Chennai")
    month        = int(data.get("month", datetime.now().month))
    rainfall_mm  = float(data.get("rainfall_mm", 50))
    avg_temp     = float(data.get("avg_temp", 30))
    max_temp     = float(data.get("max_temp", 36))
    wind_speed   = float(data.get("wind_speed", 15))

    # Encode district
    try:
        district_enc = label_encoder.transform([district])[0]
    except ValueError:
        district_enc = 0   # default if unknown district

    features = [[district_enc, month, rainfall_mm, avg_temp, max_temp, wind_speed]]
    raw_score = float(model.predict(features)[0])
    risk_score = round(max(0, min(130, raw_score)), 1)

    # Feature importance for this prediction (from the forest)
    feature_names = ["District", "Month", "Rainfall", "Avg Temp", "Max Temp", "Wind Speed"]
    importances   = model.feature_importances_
    fi = [
        {"feature": name, "importance": round(float(imp) * 100, 1)}
        for name, imp in zip(feature_names, importances)
    ]
    fi.sort(key=lambda x: -x["importance"])

    # Risk tier
    tier = "HIGH" if risk_score >= 100 else "MEDIUM" if risk_score >= 70 else "LOW"

    # Premium calculation
    risk_rate     = 0.05 if risk_score >= 100 else 0.035 if risk_score >= 70 else 0.02
    weekly_earn   = float(data.get("weekly_earnings", 3500))
    platform_mul  = float(data.get("platform_multiplier", 1.0))
    season_mul    = _get_season_multiplier(month)
    raw_premium   = weekly_earn * risk_rate * platform_mul * season_mul
    premium       = round(min(60, max(20, raw_premium)))

    return jsonify({
        "district":            district,
        "risk_score":          risk_score,
        "risk_tier":           tier,
        "risk_rate_pct":       round(risk_rate * 100, 1),
        "weekly_premium":      premium,
        "monthly_premium":     round(premium * 4.33),
        "season_multiplier":   season_mul,
        "season":              _get_season_name(month),
        "feature_importance":  fi,
        "model_type":          "RandomForestRegressor",
        "predicted_at":        datetime.now().isoformat(),
    })


@app.route("/api/ml/district-scores", methods=["GET"])
def district_scores():
    """Return all pre-computed district risk scores from training."""
    scored = []
    for district, score in sorted(DISTRICT_RISK_SCORES.items(), key=lambda x: -x[1]):
        tier = "HIGH" if score >= 100 else "MEDIUM" if score >= 70 else "LOW"
        scored.append({"district": district, "risk_score": score, "tier": tier})
    return jsonify({"districts": scored, "count": len(scored)})


@app.route("/api/ml/batch-premium", methods=["POST"])
def batch_premium():
    """Recalculate premiums for all workers using the ML model (called every Monday)."""
    if not workers:
        return jsonify({"updated": 0, "message": "No workers registered"})

    results = []
    month = datetime.now().month
    for w in workers:
        district_enc = _encode_district(w["district"])
        weather      = _get_mock_weather(w["district"])
        features     = [[district_enc, month,
                         weather["rainfall_mm"], weather["temp"],
                         weather["temp"] + 5, weather["wind"]]]

        if model:
            score = float(model.predict(features)[0])
            score = round(max(0, min(130, score)), 1)
        else:
            score = DISTRICT_RISK_SCORES.get(w["district"], 80)

        tier      = "HIGH" if score >= 100 else "MEDIUM" if score >= 70 else "LOW"
        risk_rate = 0.05 if score >= 100 else 0.035 if score >= 70 else 0.02
        plat_mul  = _platform_multiplier(w.get("platform", "zomato"))
        sea_mul   = _get_season_multiplier(month)
        premium   = round(min(60, max(20, float(w.get("weeklyEarnings", 3500)) * risk_rate * plat_mul * sea_mul)))

        w["riskScore"] = score
        w["tier"]      = tier
        w["premium"]   = premium
        results.append({"worker_id": w["id"], "name": w["name"],
                         "risk_score": score, "premium": premium})

    return jsonify({"updated": len(results), "workers": results,
                    "recalibrated_at": datetime.now().isoformat()})


# ══════════════════════════════════════════════════════════════════════════════
# AUTO-TRIGGER ENGINE (3-5 mock API triggers)
# ══════════════════════════════════════════════════════════════════════════════

TRIGGERS = {
    "rain":   {"label": "Heavy Rainfall",   "threshold": 50,   "unit": "mm/24h", "severity": "HIGH",   "pct": 0.75, "source": "OpenMeteo API"},
    "heat":   {"label": "Extreme Heat",     "threshold": 42,   "unit": "°C",     "severity": "MEDIUM", "pct": 0.50, "source": "IMD API"},
    "wind":   {"label": "High Wind Speed",  "threshold": 35,   "unit": "km/h",   "severity": "MEDIUM", "pct": 0.50, "source": "OpenMeteo API"},
    "flood":  {"label": "Flood Warning",    "threshold": None, "unit": "alert",  "severity": "HIGH",   "pct": 0.75, "source": "IMD Alerts API"},
    "curfew": {"label": "Govt Curfew",      "threshold": None, "unit": "alert",  "severity": "HIGH",   "pct": 0.75, "source": "GDELT News API"},
    "strike": {"label": "Transport Strike", "threshold": None, "unit": "alert",  "severity": "MEDIUM", "pct": 0.50, "source": "Local Auth API"},
}

@app.route("/api/triggers/check", methods=["POST"])
def check_triggers():
    """
    Mock API: Simulate checking all 5 external data sources for disruptions.
    Called by the frontend every 30 seconds (or on-demand).

    Body: { district }
    Returns: { triggered: [], safe: [], confidence }
    """
    district = request.json.get("district", "Chennai")
    weather  = _get_mock_weather(district)
    alerts   = env_state["alerts"]
    fired    = []
    safe     = []

    # Trigger 1 — Heavy Rainfall (OpenMeteo)
    rain_confidence = min(100, int((weather["rainfall_mm"] / TRIGGERS["rain"]["threshold"]) * 100))
    if weather["rainfall_mm"] > TRIGGERS["rain"]["threshold"]:
        fired.append({
            "id": "rain", **TRIGGERS["rain"],
            "current_value": f'{weather["rainfall_mm"]} mm',
            "confidence": rain_confidence,
            "source_status": "✓ Confirmed by OpenMeteo + IMD"
        })
    else:
        safe.append({"id": "rain", **TRIGGERS["rain"],
                     "current_value": f'{weather["rainfall_mm"]} mm', "confidence": rain_confidence})

    # Trigger 2 — Extreme Heat (IMD)
    heat_confidence = min(100, int((weather["temp"] / TRIGGERS["heat"]["threshold"]) * 100))
    if weather["temp"] > TRIGGERS["heat"]["threshold"]:
        fired.append({
            "id": "heat", **TRIGGERS["heat"],
            "current_value": f'{weather["temp"]} °C',
            "confidence": heat_confidence,
            "source_status": "✓ Confirmed by IMD API"
        })
    else:
        safe.append({"id": "heat", **TRIGGERS["heat"],
                     "current_value": f'{weather["temp"]} °C', "confidence": heat_confidence})

    # Trigger 3 — High Wind (OpenMeteo)
    wind_confidence = min(100, int((weather["wind"] / TRIGGERS["wind"]["threshold"]) * 100))
    if weather["wind"] > TRIGGERS["wind"]["threshold"]:
        fired.append({
            "id": "wind", **TRIGGERS["wind"],
            "current_value": f'{weather["wind"]} km/h',
            "confidence": wind_confidence,
            "source_status": "✓ Confirmed by OpenMeteo"
        })
    else:
        safe.append({"id": "wind", **TRIGGERS["wind"],
                     "current_value": f'{weather["wind"]} km/h', "confidence": wind_confidence})

    # Trigger 4 — Flood Warning (IMD Alerts)
    if alerts["flood"]:
        fired.append({
            "id": "flood", **TRIGGERS["flood"],
            "current_value": "Active IMD Alert",
            "confidence": 97,
            "source_status": "✓ Official IMD Flood Alert issued"
        })
    else:
        safe.append({"id": "flood", **TRIGGERS["flood"],
                     "current_value": "No active alert", "confidence": 0})

    # Trigger 5 — Govt Curfew (GDELT)
    if alerts["curfew"]:
        fired.append({
            "id": "curfew", **TRIGGERS["curfew"],
            "current_value": "Movement restricted",
            "confidence": 99,
            "source_status": "✓ Confirmed by GDELT + local authority"
        })
    else:
        safe.append({"id": "curfew", **TRIGGERS["curfew"],
                     "current_value": "No curfew", "confidence": 0})

    # Transport Strike (Local Authority API)
    if alerts["strike"]:
        fired.append({
            "id": "strike", **TRIGGERS["strike"],
            "current_value": "Delivery zones blocked",
            "confidence": 92,
            "source_status": "✓ Confirmed by Local Auth API"
        })
    else:
        safe.append({"id": "strike", **TRIGGERS["strike"],
                     "current_value": "No strike", "confidence": 0})

    # Log the check
    trigger_log.append({
        "checked_at":   datetime.now().isoformat(),
        "district":     district,
        "fired_count":  len(fired),
        "fired_ids":    [t["id"] for t in fired],
        "weather_snap": weather,
    })

    return jsonify({
        "district":    district,
        "checked_at":  datetime.now().isoformat(),
        "triggered":   fired,
        "safe":        safe,
        "any_active":  len(fired) > 0,
        "weather":     weather,
        "alerts":      alerts,
    })


@app.route("/api/triggers/simulate", methods=["POST"])
def simulate_trigger():
    """
    Simulate a disruption event for demo purposes.
    Body: { type: 'rain'|'heat'|'wind'|'flood'|'curfew'|'strike', district, intensity: 0-100 }
    """
    ttype    = request.json.get("type", "rain")
    district = request.json.get("district", "Chennai")
    intensity = int(request.json.get("intensity", 100))

    if ttype == "rain":
        env_state["weather"].setdefault(district, {})["rainfall_mm"] = round(50 + intensity * 1.5, 1)
    elif ttype == "heat":
        env_state["weather"].setdefault(district, {})["temp"] = round(42 + intensity * 0.1, 1)
    elif ttype == "wind":
        env_state["weather"].setdefault(district, {})["wind"] = round(35 + intensity * 0.5, 1)
    elif ttype in ["flood", "curfew", "strike"]:
        env_state["alerts"][ttype] = True

    env_state["last_updated"] = datetime.now().isoformat()
    event = {
        "id":          f"EVT{int(time.time())}",
        "type":        ttype,
        "district":    district,
        "intensity":   intensity,
        "triggered_at": datetime.now().isoformat(),
        "trigger_meta": TRIGGERS[ttype],
    }
    active_disruptions.append(event)

    return jsonify({"status": "simulated", "event": event,
                    "message": f"Disruption '{ttype}' active in {district}"})


@app.route("/api/triggers/reset", methods=["POST"])
def reset_triggers():
    """Reset all disruptions to normal conditions."""
    district = request.json.get("district", None)
    for d in env_state["weather"]:
        env_state["weather"][d] = {"rainfall_mm": random.randint(2, 15),
                                    "temp": random.randint(28, 34),
                                    "wind": random.randint(10, 20)}
    env_state["alerts"] = {"curfew": False, "strike": False, "flood": False}
    active_disruptions.clear()
    return jsonify({"status": "reset", "message": "All disruptions cleared"})


@app.route("/api/triggers/auto-claim", methods=["POST"])
def auto_claim():
    """
    Zero-touch auto-claim: check triggers, run fraud engine, fire payouts.
    Body: { district }
    Called automatically when a trigger fires.
    """
    district = request.json.get("district", "Chennai")
    resp     = check_triggers()
    result   = resp.get_json()

    if not result["any_active"]:
        return jsonify({"message": "No active disruptions", "claims_filed": 0})

    # Find all active policies in this district
    affected_policies = [p for p in policies
                         if p["status"] == "active" and p.get("district") == district]
    filed = []

    for pol in affected_policies:
        worker = next((w for w in workers if w["id"] == pol["workerId"]), None)
        if not worker:
            continue

        for trigger in result["triggered"]:
            # Fraud check
            fraud = _run_fraud_check(worker, trigger["id"])
            amount = round(pol["dailyPayout"] * trigger["pct"])
            status = "pending" if fraud["passed"] else "rejected"

            claim = {
                "id":          f"AUTO{int(time.time())}{random.randint(10,99)}",
                "workerId":    worker["id"],
                "workerName":  worker["name"],
                "policyId":    pol["id"],
                "trigger":     trigger["label"],
                "triggerId":   trigger["id"],
                "amount":      amount,
                "fraudPass":   fraud["passed"],
                "fraudReason": fraud.get("reason", ""),
                "status":      status,
                "auto":        True,
                "confidence":  trigger["confidence"],
                "date":        datetime.now().strftime("%d/%m/%Y"),
                "rawDate":     datetime.now().isoformat(),
            }
            claims.append(claim)
            if fraud["passed"]:
                pool["balance"]      -= amount
                pool["total_payouts"] += amount
            filed.append(claim)

    return jsonify({
        "district":     district,
        "triggers_fired": [t["label"] for t in result["triggered"]],
        "workers_affected": len(affected_policies),
        "claims_filed": len(filed),
        "claims":       filed,
    })


# ══════════════════════════════════════════════════════════════════════════════
# WORKER / POLICY / CLAIMS CRUD
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/workers", methods=["GET"])
def get_workers():
    return jsonify(workers)

@app.route("/api/workers", methods=["POST"])
def register_worker():
    data     = request.json
    district = data.get("district", "Chennai")
    score    = DISTRICT_RISK_SCORES.get(district, 80)
    tier     = "HIGH" if score >= 100 else "MEDIUM" if score >= 70 else "LOW"
    worker   = {
        "id":            f"W{int(time.time())}",
        "name":          data["name"],
        "phone":         data["phone"],
        "district":      district,
        "platform":      data.get("platform", "zomato"),
        "weeklyEarnings": float(data.get("weeklyEarnings", 3500)),
        "upi":           data.get("upi", ""),
        "riskScore":     score,
        "tier":          tier,
        "joined":        datetime.now().strftime("%d/%m/%Y"),
    }
    workers.append(worker)
    return jsonify(worker), 201

@app.route("/api/policies", methods=["GET"])
def get_policies():
    return jsonify(policies)

@app.route("/api/policies", methods=["POST"])
def create_policy():
    data   = request.json
    worker = next((w for w in workers if w["id"] == data["workerId"]), None)
    if not worker:
        return jsonify({"error": "Worker not found"}), 404
    policy = {
        "id":          f"POL{int(time.time())}",
        "workerId":    worker["id"],
        "workerName":  worker["name"],
        "district":    worker["district"],
        "platform":    worker.get("platform"),
        "weeklyPremium": data.get("weeklyPremium", 40),
        "dailyPayout": round(float(worker["weeklyEarnings"]) * 0.7 / 7),
        "status":      "active",
        "startDate":   datetime.now().strftime("%d/%m/%Y"),
    }
    pool["balance"]          += policy["weeklyPremium"]
    pool["total_premiums"]   += policy["weeklyPremium"]
    policies.append(policy)
    return jsonify(policy), 201

@app.route("/api/claims", methods=["GET"])
def get_claims():
    return jsonify(claims)

@app.route("/api/claims/<claim_id>/approve", methods=["POST"])
def approve_claim(claim_id):
    claim = next((c for c in claims if c["id"] == claim_id), None)
    if not claim:
        return jsonify({"error": "Claim not found"}), 404
    claim["status"] = "approved"
    pool["balance"]       -= claim["amount"]
    pool["total_payouts"] += claim["amount"]
    return jsonify({"claim": claim, "pool": pool})

@app.route("/api/pool", methods=["GET"])
def get_pool():
    return jsonify({**pool, "worker_count": len(workers), "policy_count": len(policies),
                    "claim_count": len(claims)})

@app.route("/api/triggers/log", methods=["GET"])
def get_trigger_log():
    return jsonify(trigger_log[-50:])

@app.route("/api/env-state", methods=["GET"])
def get_env_state():
    return jsonify(env_state)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok", "model_loaded": model is not None,
        "workers": len(workers), "policies": len(policies), "claims": len(claims),
        "pool_balance": pool["balance"]
    })


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _get_mock_weather(district):
    """Return current mock weather for a district."""
    city_key = district.split()[0]
    return env_state["weather"].get(
        city_key,
        env_state["weather"].get(district, {"rainfall_mm": 10, "temp": 30, "wind": 15})
    )

def _encode_district(district):
    try:
        return int(label_encoder.transform([district])[0])
    except (ValueError, AttributeError):
        return 0

def _platform_multiplier(platform):
    return {"zomato": 1.1, "swiggy": 1.1, "zepto": 1.0, "blinkit": 1.0,
            "amazon": 0.9, "flipkart": 0.9, "dunzo": 1.05}.get(platform, 1.0)

def _get_season_multiplier(month):
    if month in [6, 7, 8, 9]:   return 1.5
    if month in [3, 4, 5]:      return 1.2
    if month in [10, 11]:       return 0.9
    return 0.8

def _get_season_name(month):
    if month in [6, 7, 8, 9]:   return "monsoon"
    if month in [3, 4, 5]:      return "summer"
    if month in [10, 11]:       return "autumn"
    return "winter"

def _run_fraud_check(worker, trigger_id):
    """Simplified fraud engine matching data.js logic."""
    # Duplicate check (24h window)
    cutoff = datetime.now() - timedelta(hours=24)
    duplicate = any(
        c["workerId"] == worker["id"] and
        c["status"] in ["pending", "approved"] and
        datetime.fromisoformat(c["rawDate"]) > cutoff
        for c in claims
    )
    if duplicate:
        return {"passed": False, "reason": "Duplicate claim within 24h window"}

    # GPS zone — mock: 95% of claims pass
    gps_ok = random.random() > 0.05
    if not gps_ok:
        return {"passed": False, "reason": "GPS zone mismatch"}

    # Platform activity — mock: 90% pass
    active_ok = random.random() > 0.10
    if not active_ok:
        return {"passed": False, "reason": "Worker not active on platform before disruption"}

    return {"passed": True, "reason": ""}


if __name__ == "__main__":
    print("🚀 GigShield API starting on http://localhost:5000")
    print("   Endpoints:")
    print("   POST /api/ml/risk-score          — ML risk prediction")
    print("   GET  /api/ml/district-scores     — All district scores")
    print("   POST /api/ml/batch-premium       — Recalibrate all workers")
    print("   POST /api/triggers/check         — Check all 5 triggers")
    print("   POST /api/triggers/simulate      — Simulate a disruption")
    print("   POST /api/triggers/auto-claim    — Fire auto-claims")
    print("   POST /api/triggers/reset         — Reset to normal")
    print("   GET  /api/health                 — Health check")
    app.run(debug=True, port=5000)
