// GigShield — data.js (Phase 2)
// Calls Flask ML backend. Falls back to static if backend is offline.

const API = "http://localhost:5000/api";

export const DISTRICTS = {
  "Chennai": 110, "Mumbai Suburban": 128, "Mumbai City": 125, "Nagpur": 98,
  "Bangalore": 88, "Hyderabad": 82, "Kolkata": 105, "Delhi": 72, "Pune": 85,
  "Tirunelveli": 92, "Madurai": 89, "Coimbatore": 78, "Nagapattinam": 95,
  "Ratnagiri": 118, "Dhubri": 115, "Rajkot": 96, "Bhopal": 94, "Puri": 100,
  "Nainital": 97, "West Tripura": 103, "Goalpara": 101, "Ahmedabad": 75,
  "Surat": 80, "Vizag": 88, "Thiruvananthapuram": 91
};

export const PLATFORMS = {
  zomato: 1.1, swiggy: 1.1, zepto: 1.0,
  blinkit: 1.0, amazon: 0.9, flipkart: 0.9, dunzo: 1.05
};

export const SEASONS = {
  monsoon: 1.5, summer: 1.2, autumn: 0.9, winter: 0.8
};

export const TRIGGERS = [
  { id: "rain",   label: "Heavy Rainfall",    threshold: ">50mm/24h",              severity: "HIGH",   pct: 0.75, icon: "🌧", source: "OpenMeteo API" },
  { id: "heat",   label: "Extreme Heat",      threshold: ">42°C",                  severity: "MEDIUM", pct: 0.50, icon: "🌡", source: "IMD API" },
  { id: "wind",   label: "High Wind Speed",   threshold: ">35 km/h",               severity: "MEDIUM", pct: 0.50, icon: "💨", source: "OpenMeteo API" },
  { id: "flood",  label: "Flood Warning",     threshold: "Official IMD alert",     severity: "HIGH",   pct: 0.75, icon: "🌊", source: "IMD Alerts API" },
  { id: "curfew", label: "Govt Curfew",       threshold: "Movement restricted",    severity: "HIGH",   pct: 0.75, icon: "🚫", source: "GDELT News API" },
  { id: "strike", label: "Transport Strike",  threshold: "Delivery zones blocked", severity: "MEDIUM", pct: 0.50, icon: "🛑", source: "Local Auth API" }
];

export function getSeason() {
  const m = new Date().getMonth() + 1;
  if (m >= 6 && m <= 9)   return "monsoon";
  if (m >= 3 && m <= 5)   return "summer";
  if (m >= 10 && m <= 11) return "autumn";
  return "winter";
}

export function calcPremium(weeklyEarnings, district, platform, season) {
  const riskScore = DISTRICTS[district] || 70;
  const riskRate  = riskScore >= 100 ? 0.05 : riskScore >= 70 ? 0.035 : 0.02;
  const pMul      = PLATFORMS[platform] || 1.0;
  const sMul      = SEASONS[season] || 1.0;
  return Math.min(60, Math.max(20, Math.round(weeklyEarnings * riskRate * pMul * sMul)));
}

export function getRiskTier(score) {
  return score >= 100 ? "HIGH" : score >= 70 ? "MEDIUM" : "LOW";
}

export function runFraudCheck(worker, claimType, gpsMatch, wasActive, existingClaims) {
  const checks = {
    duplicate: !existingClaims.find(c => {
      const h24 = Date.now() - 24 * 60 * 60 * 1000;
      return c.workerId === worker.id &&
        ["pending", "approved"].includes(c.status) &&
        new Date(c.rawDate).getTime() > h24;
    }),
    gpsZone:        gpsMatch === "yes",
    platformActive: wasActive === "yes"
  };
  const passed = checks.duplicate && checks.gpsZone && checks.platformActive;
  let reason = "";
  if (!checks.duplicate)      reason = "Duplicate claim within 24h window";
  else if (!checks.gpsZone)   reason = "GPS zone mismatch — not in registered district";
  else if (!checks.platformActive) reason = "Worker not active on platform before disruption";
  return { passed, checks, reason };
}

// ── ML API ────────────────────────────────────────────────────────────────────
export async function fetchMLRiskScore({ district, weeklyEarnings, platform }) {
  try {
    const res = await fetch(`${API}/ml/risk-score`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        district,
        month:               new Date().getMonth() + 1,
        rainfall_mm:         50,
        avg_temp:            30,
        max_temp:            36,
        wind_speed:          15,
        weekly_earnings:     weeklyEarnings,
        platform_multiplier: PLATFORMS[platform] || 1.0,
      }),
    });
    if (!res.ok) throw new Error("API error");
    return await res.json();
  } catch {
    const riskScore = DISTRICTS[district] || 80;
    const tier      = getRiskTier(riskScore);
    const riskRate  = riskScore >= 100 ? 0.05 : riskScore >= 70 ? 0.035 : 0.02;
    const sMul      = SEASONS[getSeason()] || 1.0;
    const pMul      = PLATFORMS[platform] || 1.0;
    return {
      district, risk_score: riskScore, risk_tier: tier,
      risk_rate_pct:   riskRate * 100,
      weekly_premium:  Math.min(60, Math.max(20, Math.round(weeklyEarnings * riskRate * pMul * sMul))),
      season:          getSeason(),
      season_multiplier: sMul,
      feature_importance: [],
      model_type: "Static fallback (start backend: python backend/app.py)",
      predicted_at: new Date().toISOString(),
    };
  }
}

export async function checkTriggers(district) {
  try {
    const res = await fetch(`${API}/triggers/check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ district }),
    });
    if (!res.ok) throw new Error();
    return await res.json();
  } catch {
    return { any_active: false, triggered: [], safe: TRIGGERS.map(t => ({ ...t, confidence: 0, current_value: "—" })) };
  }
}

export async function simulateTrigger(type, district, intensity = 100) {
  try {
    const res = await fetch(`${API}/triggers/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type, district, intensity }),
    });
    return await res.json();
  } catch {
    return { error: "Backend offline — run: python backend/app.py" };
  }
}

export async function fireAutoClaim(district) {
  try {
    const res = await fetch(`${API}/triggers/auto-claim`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ district }),
    });
    return await res.json();
  } catch {
    return { error: "Backend offline" };
  }
}

export async function resetTriggers() {
  try {
    const res = await fetch(`${API}/triggers/reset`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    return await res.json();
  } catch {
    return { error: "Backend offline" };
  }
}
