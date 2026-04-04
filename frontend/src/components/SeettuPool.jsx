import React from "react";
import { TRIGGERS, SEASONS, getRiskTier } from "../data";

// ── சீட்டு Community Pool ────────────────────────────────────────
export function SeettuPool({ policies, pool, totalPaid }) {
  const active = policies.filter(p => p.status === "active");
  const poolHealth = pool > 5000 ? "Healthy" : pool > 1000 ? "Low" : "Critical";
  const healthColor = pool > 5000 ? "#639922" : pool > 1000 ? "#ef9f27" : "#e24b4a";

  return (
    <div>
      <h1 className="gs-h1">சீட்டு Community Pool</h1>
      <p className="gs-sub">All premiums go into one community pool — payouts come from pool, not company funds</p>

      <div className="gs-card" style={{ background: "#0f2740", borderColor: "#1a3a5c" }}>
        <div style={{ display: "flex", justifyContent: "space-around", padding: "8px 0" }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ color: "#64748b", fontSize: 10, textTransform: "uppercase", letterSpacing: 0.5 }}>Pool Balance</div>
            <div style={{ color: "#f97316", fontSize: 28, fontWeight: 500 }}>₹{Math.round(pool).toLocaleString()}</div>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ color: "#64748b", fontSize: 10, textTransform: "uppercase", letterSpacing: 0.5 }}>Total Paid Out</div>
            <div style={{ color: "#f97316", fontSize: 28, fontWeight: 500 }}>₹{Math.round(totalPaid).toLocaleString()}</div>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ color: "#64748b", fontSize: 10, textTransform: "uppercase", letterSpacing: 0.5 }}>Health Status</div>
            <div style={{ color: healthColor, fontSize: 28, fontWeight: 500 }}>{poolHealth}</div>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ color: "#64748b", fontSize: 10, textTransform: "uppercase", letterSpacing: 0.5 }}>Active Members</div>
            <div style={{ color: "#f97316", fontSize: 28, fontWeight: 500 }}>{active.length}</div>
          </div>
        </div>
      </div>

      <div className="gs-card">
        <div className="gs-card-title">How the சீட்டு Pool works</div>
        {[
          ["Every Monday", "Premium auto-deducted from platform payout"],
          ["All premiums go to", "Community pool (not company funds)"],
          ["Disruption detected", "Payout from pool within 30 seconds"],
          ["Surplus balance", "Rolls to next week — workers never lose contribution"],
          ["Pool reserve rule", "Min 20% always kept as reserve"]
        ].map(([k, v]) => (
          <div key={k} className="gs-frow"><span>{k}</span><span style={{ color: "var(--color-text-secondary)" }}>{v}</span></div>
        ))}
      </div>

      {active.length > 0 && (
        <div className="gs-card" style={{ padding: 0, overflow: "hidden" }}>
          <div style={{ padding: "12px 14px", fontWeight: 500, fontSize: 13, borderBottom: "0.5px solid var(--color-border-tertiary)" }}>
            Active Contributors
          </div>
          <table className="gs-table">
            <thead>
              <tr><th>Worker</th><th>District</th><th>Weekly Premium</th><th>Monthly Contribution</th><th>Risk Tier</th></tr>
            </thead>
            <tbody>
              {active.map(p => {
                const tier = getRiskTier(p.riskScore || 70);
                return (
                  <tr key={p.id}>
                    <td>{p.workerName}</td>
                    <td>{p.district}</td>
                    <td>₹{p.weeklyPremium}/wk</td>
                    <td>₹{Math.round(p.weeklyPremium * 4.33)}</td>
                    <td><span className={`bdg ${tier === "HIGH" ? "bdg-r" : tier === "MEDIUM" ? "bdg-o" : "bdg-g"}`}>{tier}</span></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ── Auto-Triggers ─────────────────────────────────────────────────
export function AutoTriggers() {
  return (
    <div>
      <h1 className="gs-h1">Parametric Auto-Triggers</h1>
      <p className="gs-sub">Disruption detected = payout sent. Worker does nothing. All 6 triggers fully automated.</p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 14 }}>
        {TRIGGERS.map(t => (
          <div key={t.id} className={`gs-tcard ${t.severity === "HIGH" ? "high" : "med"}`}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <div style={{ fontSize: 14, fontWeight: 500 }}>{t.icon} {t.label}</div>
              <span className={`bdg ${t.severity === "HIGH" ? "bdg-r" : "bdg-o"}`}>{t.severity}</span>
            </div>
            <div className="gs-frow" style={{ padding: "4px 0" }}>
              <span style={{ color: "var(--color-text-secondary)", fontSize: 11 }}>Trigger</span>
              <span style={{ fontSize: 12, fontWeight: 500 }}>{t.threshold}</span>
            </div>
            <div className="gs-frow" style={{ padding: "4px 0" }}>
              <span style={{ color: "var(--color-text-secondary)", fontSize: 11 }}>Source</span>
              <span style={{ fontSize: 12 }}>{t.source}</span>
            </div>
            <div className="gs-frow" style={{ padding: "4px 0" }}>
              <span style={{ color: "var(--color-text-secondary)", fontSize: 11 }}>Payout</span>
              <span style={{ fontSize: 12, color: "#639922", fontWeight: 500 }}>{Math.round(t.pct * 100)}% of daily earnings</span>
            </div>
          </div>
        ))}
      </div>

      <div className="gs-card">
        <div className="gs-card-title"><span className="gs-pulse" /> Fraud Detection Engine — 3-Layer Check</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16 }}>
          <div>
            <div style={{ fontSize: 12, fontWeight: 500, color: "#e24b4a", marginBottom: 6 }}>Layer 1 — Detect the Faker</div>
            <div style={{ fontSize: 12, color: "var(--color-text-secondary)", lineHeight: 1.9 }}>
              ✓ GPS zone continuity check<br />
              ✓ Platform activity gap analysis<br />
              ✓ Duplicate claim 24h window
            </div>
          </div>
          <div>
            <div style={{ fontSize: 12, fontWeight: 500, color: "#ef9f27", marginBottom: 6 }}>Layer 2 — Catch the Ring</div>
            <div style={{ fontSize: 12, color: "var(--color-text-secondary)", lineHeight: 1.9 }}>
              ✓ 15%+ zone batch hold trigger<br />
              ✓ Referral network graph check<br />
              ✓ Device fingerprint / IMEI flag
            </div>
          </div>
          <div>
            <div style={{ fontSize: 12, fontWeight: 500, color: "#639922", marginBottom: 6 }}>Layer 3 — Protect the Honest</div>
            <div style={{ fontSize: 12, color: "var(--color-text-secondary)", lineHeight: 1.9 }}>
              ✓ Tier 1 (trusted) — instant approve<br />
              ✓ Tier 2 (new) — 2hr soft hold<br />
              ✓ Tier 3 (flagged) — 24hr manual review
            </div>
          </div>
        </div>
        <div style={{ background: "#1a3a5c", borderRadius: "var(--border-radius-md)", padding: "10px 14px", marginTop: 14, fontSize: 12, color: "#94a3b8", textAlign: "center" }}>
          Key: Is the disruption real? (Weather API) + Was THIS worker actually affected? (Behavioral Data) — Both must be YES
        </div>
      </div>
    </div>
  );
}
