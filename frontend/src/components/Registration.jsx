import React, { useState } from "react";
import { DISTRICTS, PLATFORMS, getRiskTier } from "../data";

export default function Registration({ workers, onRegister }) {
  const [form, setForm] = useState({ name:"", phone:"", district:"", platform:"", weeklyEarnings:"", upi:"" });
  const [flash, setFlash] = useState(null);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const submit = () => {
    const { name, phone, district, platform, weeklyEarnings, upi } = form;
    if (!name || !phone || !district || !platform || !weeklyEarnings || !upi) {
      setFlash({ type: "err", msg: "Please fill in all fields." }); return;
    }
    if (!/^\d{10}$/.test(phone)) {
      setFlash({ type: "err", msg: "Enter a valid 10-digit phone number." }); return;
    }
    const riskScore = DISTRICTS[district] || 70;
    const worker = {
      id: "W" + Date.now().toString().slice(-6),
      ...form, riskScore,
      tier: getRiskTier(riskScore),
      joined: new Date().toLocaleDateString("en-IN")
    };
    onRegister(worker);
    setFlash({ type: "ok", msg: `${name} registered! Risk Score: ${riskScore}/130 (${getRiskTier(riskScore)})` });
    setForm({ name:"", phone:"", district:"", platform:"", weeklyEarnings:"", upi:"" });
  };

  return (
    <div>
      <h1 className="gs-h1">Worker Registration</h1>
      <p className="gs-sub">Register gig workers — name, phone, district, platform, weekly earnings</p>

      {flash && <div className={flash.type === "ok" ? "gs-ok" : "gs-err"}>{flash.type === "ok" ? "✓ " : ""}{flash.msg}</div>}

      <div className="gs-card">
        <div className="gs-card-title">Personal & Work Details</div>
        <div className="gs-grid2">
          <div className="gs-fg"><label>Full Name</label>
            <input placeholder="e.g. Rajan Kumar" value={form.name} onChange={e => set("name", e.target.value)} />
          </div>
          <div className="gs-fg"><label>Phone (UPI linked)</label>
            <input placeholder="e.g. 9876543210" value={form.phone} onChange={e => set("phone", e.target.value)} />
          </div>
          <div className="gs-fg"><label>District</label>
            <select value={form.district} onChange={e => set("district", e.target.value)}>
              <option value="">Select district</option>
              {Object.keys(DISTRICTS).map(d => (
                <option key={d} value={d}>{d} (Risk: {DISTRICTS[d]})</option>
              ))}
            </select>
          </div>
          <div className="gs-fg"><label>Platform</label>
            <select value={form.platform} onChange={e => set("platform", e.target.value)}>
              <option value="">Select platform</option>
              {Object.keys(PLATFORMS).map(p => (
                <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)} ({PLATFORMS[p]}×)</option>
              ))}
            </select>
          </div>
          <div className="gs-fg"><label>Weekly Earnings (₹)</label>
            <input type="number" placeholder="e.g. 3500" value={form.weeklyEarnings} onChange={e => set("weeklyEarnings", e.target.value)} />
          </div>
          <div className="gs-fg"><label>UPI ID</label>
            <input placeholder="e.g. rajan@upi" value={form.upi} onChange={e => set("upi", e.target.value)} />
          </div>
        </div>
        <div className="gs-actions">
          <button className="gs-btn" onClick={submit}>Register Worker →</button>
        </div>
      </div>

      {workers.length > 0 && (
        <div className="gs-card" style={{ padding: 0, overflow: "hidden" }}>
          <table className="gs-table">
            <thead>
              <tr><th>Name</th><th>District</th><th>Platform</th><th>Weekly ₹</th><th>Risk Score</th><th>Tier</th><th>UPI</th></tr>
            </thead>
            <tbody>
              {workers.map(w => (
                <tr key={w.id}>
                  <td>{w.name}</td>
                  <td>{w.district}</td>
                  <td style={{ textTransform: "capitalize" }}>{w.platform}</td>
                  <td>₹{parseInt(w.weeklyEarnings).toLocaleString()}</td>
                  <td><strong>{w.riskScore}</strong>/130</td>
                  <td><span className={`bdg ${w.tier === "HIGH" ? "bdg-r" : w.tier === "MEDIUM" ? "bdg-o" : "bdg-g"}`}>{w.tier}</span></td>
                  <td style={{ fontSize: 11, color: "var(--color-text-secondary)" }}>{w.upi}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
