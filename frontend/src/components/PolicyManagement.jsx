import React, { useState } from "react";
import { DISTRICTS, PLATFORMS, SEASONS, calcPremium, getRiskTier, getSeason } from "../data";

export default function PolicyManagement({ workers, policies, onCreatePolicy, onCancelPolicy, pool }) {
  const [form, setForm] = useState({ workerId: "", coverage: "", season: getSeason(), duration: "6" });
  const [flash, setFlash] = useState(null);
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const active = policies.filter(p => p.status === "active").length;
  const totalCoverage = policies.reduce((s, p) => s + (p.coverage || 0), 0);

  const submit = () => {
    if (!form.workerId || !form.coverage) { setFlash({ type: "err", msg: "Select worker and coverage plan." }); return; }
    const worker = workers.find(w => w.id === form.workerId);
    const weekly = calcPremium(parseInt(worker.weeklyEarnings), worker.district, worker.platform, form.season);
    const dailyPayout = Math.round(parseInt(worker.weeklyEarnings) * 0.7 / 7);
    const expires = new Date(Date.now() + parseInt(form.duration) * 30 * 24 * 60 * 60 * 1000).toLocaleDateString("en-IN");
    const policy = {
      id: "POL" + Date.now().toString().slice(-6),
      workerId: worker.id, workerName: worker.name,
      district: worker.district, platform: worker.platform,
      weeklyPremium: weekly, coverage: parseInt(form.coverage),
      dailyPayout, season: form.season, duration: form.duration,
      expires, status: "active", riskScore: DISTRICTS[worker.district] || 70
    };
    onCreatePolicy(policy);
    setFlash({ type: "ok", msg: `Policy created! Weekly premium: ₹${weekly} · Added ₹${weekly * 4} to community pool.` });
    setForm({ workerId: "", coverage: "", season: getSeason(), duration: "6" });
  };

  return (
    <div>
      <h1 className="gs-h1">Insurance Policy Management</h1>
      <p className="gs-sub">Dynamic policies — ₹20–60/week auto-deducted from platform payout every Monday</p>

      <div className="gs-stat">
        <div className="gs-sc"><div className="gs-sl">Total Policies</div><div className="gs-sv ora">{policies.length}</div></div>
        <div className="gs-sc"><div className="gs-sl">Active</div><div className="gs-sv">{active}</div></div>
        <div className="gs-sc"><div className="gs-sl">Pool Balance</div><div className="gs-sv">₹{Math.round(pool).toLocaleString()}</div></div>
        <div className="gs-sc"><div className="gs-sl">Total Coverage</div><div className="gs-sv">₹{totalCoverage.toLocaleString()}</div></div>
      </div>

      {flash && <div className={flash.type === "ok" ? "gs-ok" : "gs-err"}>{flash.type === "ok" ? "✓ " : ""}{flash.msg}</div>}

      {workers.length === 0
        ? <div className="gs-err">No workers registered yet. Go to Registration first.</div>
        : (
          <div className="gs-card">
            <div className="gs-card-title">Create New Policy</div>
            <div className="gs-grid2">
              <div className="gs-fg"><label>Select Worker</label>
                <select value={form.workerId} onChange={e => set("workerId", e.target.value)}>
                  <option value="">Choose worker</option>
                  {workers.map(w => (
                    <option key={w.id} value={w.id}>{w.name} — {w.district} (Risk {w.riskScore})</option>
                  ))}
                </select>
              </div>
              <div className="gs-fg"><label>Coverage Plan</label>
                <select value={form.coverage} onChange={e => set("coverage", e.target.value)}>
                  <option value="">Select plan</option>
                  <option value="50000">Basic — ₹50,000 coverage</option>
                  <option value="100000">Standard — ₹1,00,000 coverage</option>
                  <option value="200000">Premium — ₹2,00,000 coverage</option>
                </select>
              </div>
              <div className="gs-fg"><label>Season</label>
                <select value={form.season} onChange={e => set("season", e.target.value)}>
                  {Object.keys(SEASONS).map(s => (
                    <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)} ({SEASONS[s]}×)</option>
                  ))}
                </select>
              </div>
              <div className="gs-fg"><label>Duration</label>
                <select value={form.duration} onChange={e => set("duration", e.target.value)}>
                  <option value="3">3 months</option>
                  <option value="6">6 months</option>
                  <option value="12">12 months</option>
                </select>
              </div>
            </div>
            <div className="gs-actions">
              <button className="gs-btn" onClick={submit}>Create Policy & Add to Pool →</button>
            </div>
          </div>
        )}

      {policies.length > 0 && (
        <div className="gs-card" style={{ padding: 0, overflow: "hidden" }}>
          <table className="gs-table">
            <thead>
              <tr><th>Policy ID</th><th>Worker</th><th>Weekly Premium</th><th>Coverage</th><th>Daily Payout</th><th>Expires</th><th>Status</th><th></th></tr>
            </thead>
            <tbody>
              {policies.map(p => (
                <tr key={p.id}>
                  <td style={{ fontFamily: "monospace", fontSize: 11 }}>{p.id}</td>
                  <td>{p.workerName}</td>
                  <td><strong>₹{p.weeklyPremium}</strong>/wk</td>
                  <td>₹{p.coverage.toLocaleString()}</td>
                  <td>₹{p.dailyPayout.toLocaleString()}</td>
                  <td>{p.expires}</td>
                  <td><span className={`bdg ${p.status === "active" ? "bdg-g" : p.status === "cancelled" ? "bdg-r" : "bdg-o"}`}>{p.status}</span></td>
                  <td>{p.status === "active" && <button className="gs-btnr" onClick={() => onCancelPolicy(p.id)}>Cancel</button>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
