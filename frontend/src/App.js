import React, { useState } from "react";
import Registration      from "./components/Registration";
import PolicyManagement  from "./components/PolicyManagement";
import PremiumCalculator from "./components/PremiumCalculator";
import ClaimsManagement  from "./components/ClaimsManagement";
import { SeettuPool }    from "./components/SeettuPool";
import AutoTriggerEngine from "./components/AutoTriggerEngine";
import "./App.css";

const TABS = [
  { id: "register", label: "01 Registration"   },
  { id: "policies", label: "02 Policy Mgmt"    },
  { id: "premium",  label: "03 Premium (ML)"   },
  { id: "triggers", label: "⚡ Auto-Triggers"  },
  { id: "claims",   label: "04 Claims"          },
  { id: "pool",     label: "சீட்டு Pool"       },
];

function loadState(key, fallback) {
  try { return JSON.parse(localStorage.getItem(key)) || fallback; } catch { return fallback; }
}

export default function App() {
  const [tab,       setTab]       = useState("register");
  const [workers,   setWorkers]   = useState(() => loadState("gs_workers",  []));
  const [policies,  setPolicies]  = useState(() => loadState("gs_policies", []));
  const [claims,    setClaims]    = useState(() => loadState("gs_claims",   []));
  const [pool,      setPool]      = useState(() => parseFloat(localStorage.getItem("gs_pool") || "0"));
  const [totalPaid, setTotalPaid] = useState(() => parseFloat(localStorage.getItem("gs_paid") || "0"));

  function persist(key, value) { localStorage.setItem(key, JSON.stringify(value)); }

  function handleRegister(worker) {
    const updated = [...workers, worker];
    setWorkers(updated); persist("gs_workers", updated);
  }

  function handleCreatePolicy(policy) {
    const updated  = [...policies, policy];
    const newPool  = pool + policy.weeklyPremium * 4;
    setPolicies(updated); persist("gs_policies", updated);
    setPool(newPool); localStorage.setItem("gs_pool", newPool);
  }

  function handleCancelPolicy(id) {
    const updated = policies.map(p => p.id === id ? { ...p, status: "cancelled" } : p);
    setPolicies(updated); persist("gs_policies", updated);
  }

  function handleSubmitClaim(claim) {
    // Auto-approve if fraud check passed (zero-touch)
    const finalClaim = claim.fraudPass
      ? { ...claim, status: "approved" }
      : claim;
    const updated = [...claims, finalClaim];
    setClaims(updated); persist("gs_claims", updated);
    if (finalClaim.status === "approved") {
      const newPool = Math.max(0, pool - finalClaim.amount);
      const newPaid = totalPaid + finalClaim.amount;
      setPool(newPool); localStorage.setItem("gs_pool", newPool);
      setTotalPaid(newPaid); localStorage.setItem("gs_paid", newPaid);
    }
  }

  function handleApproveClaim(id) {
    const claim   = claims.find(c => c.id === id);
    const updated = claims.map(c => c.id === id ? { ...c, status: "approved" } : c);
    const newPool = Math.max(0, pool - claim.amount);
    const newPaid = totalPaid + claim.amount;
    setClaims(updated); persist("gs_claims", updated);
    setPool(newPool);   localStorage.setItem("gs_pool", newPool);
    setTotalPaid(newPaid); localStorage.setItem("gs_paid", newPaid);
  }

  // Called by AutoTriggerEngine when backend fires auto-claims
  function handleAutoClaims(result) {
    if (!result.claims) return;
    const updated = [...claims];
    let poolDelta = 0;
    let paidDelta = 0;
    result.claims.forEach(c => {
      updated.push(c);
      if (c.status === "approved") {
        poolDelta -= c.amount;
        paidDelta += c.amount;
      }
    });
    setClaims(updated); persist("gs_claims", updated);
    const newPool = Math.max(0, pool + poolDelta);
    const newPaid = totalPaid + paidDelta;
    setPool(newPool);   localStorage.setItem("gs_pool", newPool);
    setTotalPaid(newPaid); localStorage.setItem("gs_paid", newPaid);
  }

  return (
    <div className="gs-app">
      <header className="gs-header">
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span className="gs-logo">GigShield</span>
          <span className="gs-htitle">Protect Your Worker — Phase 2</span>
        </div>
        <span className="gs-badge">DEVTrails 2026</span>
      </header>

      <nav className="gs-nav">
        {TABS.map(t => (
          <button
            key={t.id}
            className={`gs-nb ${tab === t.id ? "on" : ""}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <main className="gs-body">
        {tab === "register" && (
          <Registration workers={workers} onRegister={handleRegister} />
        )}
        {tab === "policies" && (
          <PolicyManagement workers={workers} policies={policies} pool={pool}
            onCreatePolicy={handleCreatePolicy} onCancelPolicy={handleCancelPolicy} />
        )}
        {tab === "premium" && (
          <PremiumCalculator />
        )}
        {tab === "triggers" && (
          <AutoTriggerEngine
            workers={workers}
            policies={policies}
            onClaimFiled={handleAutoClaims}
          />
        )}
        {tab === "claims" && (
          <ClaimsManagement
            workers={workers} policies={policies} claims={claims}
            totalPaid={totalPaid}
            onSubmitClaim={handleSubmitClaim}
            onApproveClaim={handleApproveClaim}
          />
        )}
        {tab === "pool" && (
          <SeettuPool policies={policies} pool={pool} totalPaid={totalPaid} />
        )}
      </main>
    </div>
  );
}
