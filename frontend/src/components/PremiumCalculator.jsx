import React, { useState, useEffect } from "react";
import { DISTRICTS, PLATFORMS, SEASONS, calcPremium, getRiskTier, getSeason, fetchMLRiskScore } from "../data";

export default function PremiumCalculator() {
  const [inputs, setInputs] = useState({
    district: "Chennai", platform: "zomato", earnings: 3500, season: getSeason()
  });
  const [mlResult, setMlResult] = useState(null);
  const [loading,  setLoading]  = useState(false);
  const [apiUsed,  setApiUsed]  = useState(false);

  const set = (k, v) => setInputs(i => ({ ...i, [k]: v }));
  const { district, platform, earnings, season } = inputs;

  useEffect(() => {
    const t = setTimeout(async () => {
      setLoading(true);
      const result = await fetchMLRiskScore({ district, weeklyEarnings: earnings, platform });
      setMlResult(result);
      setApiUsed(!result.model_type?.includes("fallback") && !result.model_type?.includes("Static"));
      setLoading(false);
    }, 500);
    return () => clearTimeout(t);
  }, [district, platform, earnings]);

  const riskScore = mlResult?.risk_score   ?? (DISTRICTS[district] || 70);
  const tier      = mlResult?.risk_tier    ?? getRiskTier(riskScore);
  const riskRate  = mlResult?.risk_rate_pct ?? (riskScore >= 100 ? 5 : riskScore >= 70 ? 3.5 : 2);
  const pMul      = PLATFORMS[platform] || 1.0;
  const sMul      = mlResult?.season_multiplier ?? (SEASONS[season] || 1.0);
  const premium   = mlResult?.weekly_premium ?? calcPremium(earnings, district, platform, season);
  const rColor    = tier === "HIGH" ? "#e24b4a" : tier === "MEDIUM" ? "#ef9f27" : "#639922";
  const fi        = mlResult?.feature_importance || [];

  return (
    <div>
      <h1 className="gs-h1">Dynamic Premium Calculator</h1>
      <p className="gs-sub">
        {apiUsed
          ? "🤖 ML model active — RandomForest trained on 10+ years Indian weather data"
          : "Formula: Weekly Earnings × Risk Rate × Platform Multiplier × Season Multiplier"}
      </p>

      <div className="gs-pbox">
        <div className="gs-pl">
          Weekly Premium
          {loading && <span style={{ fontSize: 11, marginLeft: 8, opacity: 0.7 }}>recalculating…</span>}
        </div>
        <div className="gs-pv" style={{ opacity: loading ? 0.5 : 1 }}>₹{premium}</div>
        <div className="gs-ps">
          ≈ ₹{Math.round(premium * 4.33)}/month · covers ₹{Math.round(earnings * 0.7).toLocaleString()} income disruption/week
        </div>
        <div className="gs-pool">
          <div className="gs-pi"><div className="gs-pil">Risk Score</div><div className="gs-piv">{riskScore}/130</div></div>
          <div className="gs-pi"><div className="gs-pil">Risk Rate</div><div className="gs-piv">{riskRate}%</div></div>
          <div className="gs-pi"><div className="gs-pil">Platform ×</div><div className="gs-piv">{pMul}×</div></div>
          <div className="gs-pi"><div className="gs-pil">Season ×</div><div className="gs-piv">{sMul}×</div></div>
        </div>
      </div>

      {mlResult && (
        <div style={{
          padding: "8px 14px", borderRadius: 8, marginBottom: 16, fontSize: 12,
          background: apiUsed ? "#f0fdf4" : "#fef3c7",
          color: apiUsed ? "#166534" : "#92400e",
          border: `1px solid ${apiUsed ? "#86efac" : "#fde68a"}`,
        }}>
          {apiUsed
            ? `✓ RandomForestRegressor · predicted at ${new Date(mlResult.predicted_at).toLocaleTimeString("en-IN")}`
            : `⚠ ${mlResult.model_type}`}
        </div>
      )}

      <div className="gs-card">
        <div className="gs-card-title">Adjust Parameters</div>
        <div className="gs-grid2">
          <div className="gs-fg">
            <label>District</label>
            <select value={district} onChange={e => set("district", e.target.value)}>
              {Object.keys(DISTRICTS).map(d => (
                <option key={d} value={d}>{d} (Score: {DISTRICTS[d]})</option>
              ))}
            </select>
          </div>
          <div className="gs-fg">
            <label>Platform</label>
            <select value={platform} onChange={e => set("platform", e.target.value)}>
              {Object.keys(PLATFORMS).map(p => (
                <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)} ({PLATFORMS[p]}×)</option>
              ))}
            </select>
          </div>
          <div className="gs-fg">
            <label>Weekly Earnings: ₹{earnings.toLocaleString()}</label>
            <input type="range" min="1000" max="10000" step="100" value={earnings}
              onChange={e => set("earnings", parseInt(e.target.value))} />
          </div>
          <div className="gs-fg">
            <label>Season</label>
            <select value={season} onChange={e => set("season", e.target.value)}>
              {Object.keys(SEASONS).map(s => (
                <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)} ({SEASONS[s]}×)</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {fi.length > 0 && (
        <div className="gs-card">
          <div className="gs-card-title">ML Feature Importance — what drives this risk score</div>
          {fi.map(({ feature, importance }) => (
            <div key={feature} style={{ marginBottom: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 3 }}>
                <span>{feature}</span>
                <span style={{ fontWeight: 600 }}>{importance}%</span>
              </div>
              <div style={{ background: "#f3f4f6", borderRadius: 4, height: 8 }}>
                <div style={{
                  width: `${importance}%`, height: "100%", borderRadius: 4,
                  background: importance > 30 ? "#185FA5" : importance > 15 ? "#1D9E75" : "#888780",
                  transition: "width 0.5s"
                }} />
              </div>
            </div>
          ))}
          <div style={{ fontSize: 11, color: "#6b7280", marginTop: 8 }}>
            Source: RandomForestRegressor · Kaggle Indian Rainfall & Weather Data 2013–2023
          </div>
        </div>
      )}

      <div className="gs-card">
        <div className="gs-card-title">District Risk Analysis — {district}</div>
        <div className="gs-frow">
          <span>Overall Risk Score</span>
          <span style={{ fontWeight: 600, color: rColor }}>{tier} ({riskScore}/130)</span>
        </div>
        <div className="gs-rbar">
          <div className="gs-rf" style={{ width: `${Math.round(riskScore / 1.3)}%`, background: rColor }} />
        </div>
        <div className="gs-frow"><span>Risk rate</span><span>{riskRate}% of weekly earnings</span></div>
        <div className="gs-frow"><span>Premium cap</span><span>Min ₹20 / Max ₹60 per week</span></div>
        <div className="gs-frow"><span>Disruption payout</span><span>₹{Math.round(earnings * 0.7 / 7)}/day (70% of daily avg)</span></div>
        <div className="gs-frow"><span>Season</span><span style={{ textTransform: "capitalize" }}>{mlResult?.season || season} ({sMul}×)</span></div>
        <div className="gs-frow"><span>Recalibration</span><span>Auto every Monday via ML API</span></div>
      </div>
    </div>
  );
}
