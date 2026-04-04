import React, { useState, useEffect, useRef } from "react";
import { DISTRICTS, TRIGGERS, checkTriggers, simulateTrigger, fireAutoClaim, resetTriggers } from "../data";

const POLL_MS = 30000;

export default function AutoTriggerEngine({ workers, policies, onClaimFiled }) {
  const [district,    setDistrict]    = useState("Chennai");
  const [triggerData, setTriggerData] = useState(null);
  const [log,         setLog]         = useState([]);
  const [monitoring,  setMonitoring]  = useState(false);
  const [lastChecked, setLastChecked] = useState(null);
  const [busy,        setBusy]        = useState(false);
  const [flash,       setFlash]       = useState(null);
  const [apiOnline,   setApiOnline]   = useState(false);
  const intervalRef = useRef(null);

  useEffect(() => {
    fetch("http://localhost:5000/api/health")
      .then(r => { if (r.ok) setApiOnline(true); })
      .catch(() => setApiOnline(false));
  }, []);

  useEffect(() => {
    if (monitoring) {
      runCheck();
      intervalRef.current = setInterval(runCheck, POLL_MS);
    } else {
      clearInterval(intervalRef.current);
    }
    return () => clearInterval(intervalRef.current);
  }, [monitoring, district]);   // eslint-disable-line

  async function runCheck() {
    setLastChecked(new Date());
    const result = await checkTriggers(district);
    setTriggerData(result);
    setLog(prev => [{
      time:     new Date().toLocaleTimeString("en-IN"),
      district,
      fired:    result.triggered?.length || 0,
      triggers: result.triggered?.map(t => t.label) || [],
    }, ...prev.slice(0, 19)]);

    if (result.any_active && policies.filter(p => p.status === "active" && p.district === district).length > 0) {
      setBusy(true);
      const r = await fireAutoClaim(district);
      setBusy(false);
      if (r.claims_filed > 0) {
        setFlash({ type: "ok", msg: `✓ Auto-claim fired! ${r.claims_filed} claim(s) sent for ${r.workers_affected} worker(s) in ${district}` });
        onClaimFiled && onClaimFiled(r);
      }
    }
  }

  async function handleSim(type) {
    setFlash(null);
    const r = await simulateTrigger(type, district);
    if (r.error) {
      setFlash({ type: "err", msg: r.error });
    } else {
      setFlash({ type: "ok", msg: `✓ Simulated: ${type} in ${district} — checking triggers…` });
      await runCheck();
    }
  }

  async function handleReset() {
    await resetTriggers();
    setFlash({ type: "ok", msg: "✓ All disruptions cleared" });
    await runCheck();
  }

  const rColor = t => t.severity === "HIGH" ? "#e24b4a" : "#ef9f27";

  return (
    <div>
      <h1 className="gs-h1">Auto-Trigger Engine</h1>
      <p className="gs-sub">5 external APIs polled every 30s — disruption detected = zero-touch payout sent automatically</p>

      {/* API status */}
      <div style={{
        padding: "10px 16px", borderRadius: 8, marginBottom: 16, fontSize: 13, fontWeight: 500,
        background: apiOnline ? "#f0fdf4" : "#fef3c7",
        color:      apiOnline ? "#166534"  : "#92400e",
        border:    `1px solid ${apiOnline ? "#86efac" : "#fde68a"}`,
      }}>
        {apiOnline
          ? <><span className="gs-pulse" />Flask ML Backend connected — real triggers active</>
          : "⚠ Backend offline — open a terminal and run: cd backend && python app.py"}
      </div>

      {flash && (
        <div className={flash.type === "ok" ? "gs-ok" : "gs-err"}>
          {flash.msg}
        </div>
      )}

      {/* Controls */}
      <div className="gs-card">
        <div className="gs-card-title">Monitor District</div>
        <div className="gs-grid2">
          <div className="gs-fg">
            <label>District</label>
            <select value={district} onChange={e => setDistrict(e.target.value)}>
              {Object.keys(DISTRICTS).map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
          <div className="gs-fg" style={{ flexDirection: "row", alignItems: "flex-end", gap: 8 }}>
            <button
              className="gs-btn"
              style={{ flex: 1, background: monitoring ? "#e24b4a" : undefined }}
              onClick={() => setMonitoring(m => !m)}
            >
              {monitoring ? "⬛ Stop" : "▶ Start Monitoring (30s)"}
            </button>
            <button className="gs-btn-sec" style={{ flex: 1 }} onClick={runCheck}>
              ↻ Check Now
            </button>
          </div>
        </div>
        {lastChecked && (
          <div style={{ fontSize: 12, color: "#6b7280", marginTop: 6 }}>
            Last checked: {lastChecked.toLocaleTimeString("en-IN")}
            {monitoring && <span style={{ color: "#639922" }}> · auto-polling every 30s</span>}
            {busy        && <span style={{ color: "#ef9f27" }}> · filing auto-claims…</span>}
          </div>
        )}
      </div>

      {/* Live status */}
      {triggerData && (
        <div className="gs-card">
          <div className="gs-card-title">
            Live Status — {district}
            {triggerData.any_active
              ? <span style={{ color: "#e24b4a", marginLeft: 10, fontSize: 12 }}>⚡ {triggerData.triggered.length} ACTIVE</span>
              : <span style={{ color: "#639922", marginLeft: 10, fontSize: 12 }}>✓ All clear</span>}
          </div>

          {/* Weather snapshot */}
          {triggerData.weather && (
            <div style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap" }}>
              {[
                { label: "Rainfall",    value: `${triggerData.weather.rainfall_mm} mm`, icon: "🌧" },
                { label: "Temperature", value: `${triggerData.weather.temp} °C`,         icon: "🌡" },
                { label: "Wind",        value: `${triggerData.weather.wind} km/h`,       icon: "💨" },
              ].map(({ label, value, icon }) => (
                <div key={label} style={{
                  flex: "1 1 80px", padding: "10px 12px", borderRadius: 8, textAlign: "center",
                  background: "#f9fafb", border: "1px solid #e5e7eb",
                }}>
                  <div style={{ fontSize: 18 }}>{icon}</div>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>{value}</div>
                  <div style={{ fontSize: 11, color: "#6b7280" }}>{label}</div>
                </div>
              ))}
            </div>
          )}

          {/* Trigger grid */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
            {[...(triggerData.triggered || []), ...(triggerData.safe || [])].map(t => {
              const active = triggerData.triggered?.some(ft => ft.id === t.id);
              return (
                <div key={t.id} style={{
                  padding: "12px 14px", borderRadius: 8,
                  border: `1px solid ${active ? rColor(t) : "#e5e7eb"}`,
                  background: active
                    ? (t.severity === "HIGH" ? "#fef2f2" : "#fffbeb")
                    : "#fff",
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                    <span style={{ fontWeight: 600, fontSize: 13 }}>{t.label}</span>
                    <span style={{
                      fontSize: 11, padding: "2px 8px", borderRadius: 10, fontWeight: 600,
                      background: active ? rColor(t) : "#f3f4f6",
                      color:      active ? "#fff"     : "#6b7280",
                    }}>
                      {active ? "FIRED" : "SAFE"}
                    </span>
                  </div>
                  <div style={{ fontSize: 11, color: "#6b7280" }}>
                    {t.source} · {t.current_value || t.threshold}
                  </div>
                  {/* Confidence bar */}
                  <div style={{ background: "#f3f4f6", borderRadius: 4, height: 5, marginTop: 6 }}>
                    <div style={{
                      width: `${t.confidence || 0}%`, height: "100%", borderRadius: 4,
                      background: (t.confidence || 0) > 80 ? "#e24b4a" : (t.confidence || 0) > 40 ? "#ef9f27" : "#639922",
                      transition: "width 0.6s",
                    }} />
                  </div>
                  <div style={{ fontSize: 10, color: "#9ca3af", marginTop: 2 }}>
                    Confidence: {t.confidence || 0}%
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Simulation panel */}
      <div className="gs-card">
        <div className="gs-card-title">Simulate Disruption — Demo Panel</div>
        <p style={{ fontSize: 13, color: "#6b7280", marginBottom: 12 }}>
          Click any disruption below to demo the full auto-claim pipeline end-to-end.
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {TRIGGERS.map(t => (
            <button key={t.id} onClick={() => handleSim(t.id)} style={{
              padding: "8px 14px", borderRadius: 8, border: "none", cursor: "pointer",
              fontSize: 13, fontWeight: 600,
              background: t.severity === "HIGH" ? "#fef2f2" : "#fffbeb",
              color:      t.severity === "HIGH" ? "#a32d2d" : "#854f0b",
            }}>
              {t.icon} {t.label}
            </button>
          ))}
          <button onClick={handleReset} style={{
            padding: "8px 14px", borderRadius: 8, cursor: "pointer", fontSize: 13,
            background: "#f9fafb", border: "1px solid #e5e7eb", color: "#374151",
          }}>
            ↺ Reset All
          </button>
        </div>
      </div>

      {/* Trigger log */}
      {log.length > 0 && (
        <div className="gs-card" style={{ padding: 0, overflow: "hidden" }}>
          <div style={{ padding: "12px 16px", borderBottom: "1px solid #e5e7eb", fontWeight: 600, fontSize: 13 }}>
            Trigger Log
            <span style={{ fontSize: 12, color: "#6b7280", fontWeight: 400, marginLeft: 8 }}>
              last {log.length} checks
            </span>
          </div>
          <table className="gs-table">
            <thead>
              <tr><th>Time</th><th>District</th><th>Status</th><th>Triggers Fired</th></tr>
            </thead>
            <tbody>
              {log.map((entry, i) => (
                <tr key={i}>
                  <td style={{ fontFamily: "monospace", fontSize: 12 }}>{entry.time}</td>
                  <td>{entry.district}</td>
                  <td>
                    <span className={`bdg ${entry.fired > 0 ? "bdg-r" : "bdg-g"}`}>
                      {entry.fired > 0 ? `${entry.fired} FIRED` : "CLEAR"}
                    </span>
                  </td>
                  <td style={{ fontSize: 12 }}>
                    {entry.triggers.length > 0 ? entry.triggers.join(", ") : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
