import React, { useState } from "react";
import { TRIGGERS, runFraudCheck } from "../data";

export default function ClaimsManagement({ workers, policies, claims, onSubmitClaim, onApproveClaim, totalPaid }) {
  const [form, setForm] = useState({ policyId: "", triggerId: "", gps: "yes", active: "yes" });
  const [flash, setFlash] = useState(null);
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const activePols = policies.filter(p => p.status === "active");
  const pending = claims.filter(c => c.status === "pending").length;
  const approved = claims.filter(c => c.status === "approved").length;
  const lastPaid = claims.filter(c => c.status === "approved").slice(-1)[0];

  const submit = () => {
    if (!form.policyId || !form.triggerId) { setFlash({ type: "err", msg: "Select policy and disruption trigger." }); return; }
    const policy = policies.find(p => p.id === form.policyId);
    const worker = workers.find(w => w.id === policy.workerId);
    const trigger = TRIGGERS.find(t => t.id === form.triggerId);
    const amount = Math.round(policy.dailyPayout * trigger.pct);
    const fraud = runFraudCheck(worker, form.triggerId, form.gps, form.active, claims);
    const status = fraud.passed ? "pending" : "rejected";
    const claim = {
      id: "CLM" + Date.now().toString().slice(-6),
      workerId: worker.id, workerName: worker.name,
      policyId: policy.id, trigger: trigger.label,
      amount, fraudPass: fraud.passed, fraudReason: fraud.reason,
      status, date: new Date().toLocaleDateString("en-IN"),
      rawDate: new Date().toISOString()
    };
    onSubmitClaim(claim);
    if (fraud.passed) {
      setFlash({ type: "ok", msg: `Fraud check PASSED ✓ — ₹${amount} claim pending approval for ${worker.name}` });
    } else {
      setFlash({ type: "err", msg: `Fraud check FAILED ✗ — ${fraud.reason}. Claim rejected.` });
    }
  };

  return (
    <div>
      <h1 className="gs-h1">Claims Management</h1>
      <p className="gs-sub">Zero-touch parametric claims — fraud check → auto-approve → instant UPI payout in &lt;30s</p>

      <div className="gs-stat">
        <div className="gs-sc"><div className="gs-sl">Total Claims</div><div className="gs-sv ora">{claims.length}</div></div>
        <div className="gs-sc"><div className="gs-sl">Pending Review</div><div className="gs-sv">{pending}</div></div>
        <div className="gs-sc"><div className="gs-sl">Approved</div><div className="gs-sv">{approved}</div></div>
        <div className="gs-sc"><div className="gs-sl">Pool Paid Out</div><div className="gs-sv">₹{Math.round(totalPaid).toLocaleString()}</div></div>
      </div>

      {flash && <div className={flash.type === "ok" ? "gs-ok" : "gs-err"}>{flash.type === "ok" ? "✓ " : ""}{flash.msg}</div>}

      {activePols.length === 0
        ? <div className="gs-err">No active policies found. Create a policy first.</div>
        : (
          <div className="gs-card">
            <div className="gs-card-title">File Disruption Claim — Fraud check runs automatically</div>
            <div className="gs-grid2">
              <div className="gs-fg"><label>Active Policy</label>
                <select value={form.policyId} onChange={e => set("policyId", e.target.value)}>
                  <option value="">Select policy</option>
                  {activePols.map(p => (
                    <option key={p.id} value={p.id}>{p.id} — {p.workerName} (₹{p.dailyPayout}/day)</option>
                  ))}
                </select>
              </div>
              <div className="gs-fg"><label>Disruption Trigger</label>
                <select value={form.triggerId} onChange={e => set("triggerId", e.target.value)}>
                  <option value="">Select trigger</option>
                  {TRIGGERS.map(t => (
                    <option key={t.id} value={t.id}>{t.icon} {t.label} ({Math.round(t.pct * 100)}% payout)</option>
                  ))}
                </select>
              </div>
              <div className="gs-fg"><label>GPS Zone Match</label>
                <select value={form.gps} onChange={e => set("gps", e.target.value)}>
                  <option value="yes">Yes — in registered district</option>
                  <option value="no">No — outside registered district</option>
                </select>
              </div>
              <div className="gs-fg"><label>Platform Active Before Disruption?</label>
                <select value={form.active} onChange={e => set("active", e.target.value)}>
                  <option value="yes">Yes — was online before disruption</option>
                  <option value="no">No — was not online</option>
                </select>
              </div>
            </div>
            <div className="gs-actions">
              <button className="gs-btn" onClick={submit}>Run Fraud Check & Submit →</button>
            </div>
          </div>
        )}

      {claims.length > 0 && (
        <>
          <div className="gs-card" style={{ padding: 0, overflow: "hidden" }}>
            <table className="gs-table">
              <thead>
                <tr><th>Claim ID</th><th>Worker</th><th>Trigger</th><th>Amount</th><th>Fraud Check</th><th>Status</th><th></th></tr>
              </thead>
              <tbody>
                {claims.map(c => (
                  <tr key={c.id}>
                    <td style={{ fontFamily: "monospace", fontSize: 11 }}>{c.id}</td>
                    <td>{c.workerName}</td>
                    <td>{c.trigger}</td>
                    <td>₹{c.amount.toLocaleString()}</td>
                    <td><span style={{ color: c.fraudPass ? "#639922" : "#e24b4a", fontWeight: 500 }}>{c.fraudPass ? "✓ PASSED" : "✗ FAILED"}</span></td>
                    <td><span className={`bdg ${c.status === "approved" ? "bdg-g" : c.status === "rejected" ? "bdg-r" : "bdg-o"}`}>{c.status}</span></td>
                    <td>{c.status === "pending" && c.fraudPass && (
                      <button className="gs-btng" onClick={() => onApproveClaim(c.id)}>Pay ₹{c.amount}</button>
                    )}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {lastPaid && (
            <div className="gs-upi">
              <div style={{ fontSize: 11, color: "#639922", marginBottom: 4 }}>
                <span className="gs-pulse" /> Latest UPI Payout Sent
              </div>
              <div className="gs-upi-amt">₹{lastPaid.amount.toLocaleString()}</div>
              <div className="gs-upi-sub">Auto-transferred in &lt;30 seconds via mock UPI · {lastPaid.workerName}</div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
