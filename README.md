# GigShield — AI-Powered Parametric Insurance for India's Gig Workers

> Like the traditional Tamil **சீட்டு (Chittu Fund)** — community-powered, automated, and instant.

**Team:** Akilan B | Dhanapriya VA | Dharshini S | Gandhiraj J
**Hackathon:** Guidewire DEVTrails 2026 — Phase 1 Submission
**Persona:** Food Delivery Partners (Zomato / Swiggy)

---

## The Problem

India's platform-based delivery workers are the backbone of our digital economy. Yet they are completely unprotected from income loss caused by external disruptions:

-  **No Weather Protection** — Heavy rain halts deliveries. Zero income, zero safety net.
-  **No Curfew Coverage** — Unplanned lockdowns mean instant earnings loss.
-  **No Savings Buffer** — Gig workers live week-to-week with no financial cushion.
-  **No Insurance Access** — Traditional insurers ignore this informal workforce.

> **20–30% of monthly income** is lost during disruptions. India has **15 Million+ platform gig workers** — none of them have income disruption insurance.

**Sources:**
- [1] Guidewire DEVTrails 2026 Problem Statement
- [2] NITI Aayog — India's Booming Gig Economy, June 2022, Pg.25 Table 15
- [3] ILO India Gig Worker Report 2022

---

##  Adversarial Defense & Anti-Spoofing Strategy

### The Market Crash Scenario

Here's what happened. 500 delivery partners filed claims at the same time. All of them showed GPS coordinates inside the flood-affected zone. All of them passed the basic weather trigger check. The system paid out. The pool was drained.

But here's the thing — real floods don't work like that.

When a genuine disruption hits a city, workers don't all file claims within the same 4-minute window. They're scrambling. Some are stuck on the road. Some find out later. Some call their family first. Real distress is messy and scattered. What we saw was clean, coordinated, and suspiciously synchronized. That's not a weather event. That's an attack.

---

### How We Spot a Fake GPS vs a Genuinely Stranded Worker

The GPS coordinate alone means nothing. Anyone can spoof a location on an Android phone in under 2 minutes using a free app. What we look at instead is the **story the GPS tells over time.**

A real delivery worker who gets caught in rain doesn't teleport. Their GPS history shows them moving through their normal delivery zone — then slowing down, then stopping. There's a natural trail. A spoofed GPS shows someone sitting at home in Tambaram suddenly appearing in Nagapattinam with no movement history connecting those two points. The coordinates jump. There's no travel trail. No speed continuity.

We cross-check three things:

**1. GPS Trail Continuity**
We don't just look at where they are during the claim. We look at where they were 2 hours before, 1 hour before, and 30 minutes before. If the location jumped more than physically possible given their last known position and the time elapsed — that's a flag. A bike can do 40 km/h max in city traffic. If someone's GPS shows them 80 km away from where they were 30 minutes ago, the math doesn't work.

**2. Platform Activity Cross-Check**
A genuinely stranded worker was active on the platform before the disruption hit. They had orders. They were moving. Their app was open. When rain stops deliveries, their last platform ping should be near the affected zone. If a worker's Zomato/Swiggy app shows zero activity for the past 6 hours but they're claiming income loss from a 2-hour rain event — that doesn't add up. They weren't working to begin with.

**3. Device Sensor Fingerprinting**
When GPS is spoofed on Android, the accelerometer and gyroscope often tell a different story. A phone sitting on a table at home shows flat, stable sensor readings. A phone in a jacket pocket on a motorcycle shows vibration patterns, tilt shifts, and movement signatures. We log this passively during the app session. If the GPS says "moving through flood zone" but the accelerometer says "stationary on flat surface" — the device itself is contradicting the claim.

---

### What Data Catches a Coordinated Fraud Ring

A single fraudster is hard to catch. Five hundred acting together is actually easier — because coordination leaves fingerprints.

**Timing Clustering**
In the Market Crash scenario, 500 claims came in close together. Real disruptions don't produce synchronized claims. We run a simple time-distribution check. If more than 15% of a zone's registered workers file within the same 10-minute window, that's statistically abnormal. We flag the entire batch and hold payouts for manual review.

**Network Graph Analysis**
Fraud rings don't appear out of nowhere. They recruit. Workers who were referred by the same person, registered on the same day, use the same device model, and share overlapping contact numbers — that's a cluster. We build a lightweight social graph of referral chains and registration metadata. When a suspicious claim batch maps cleanly onto one referral cluster, we know it's organized.

**IP and Device Duplication**
When 500 people install the app from the same Wi-Fi network or the same 3 or 4 mobile devices — even if they use different phone numbers — the device fingerprint gives it away. In India, fraud rings often use one coordinator's phone to register 10-15 fake accounts. Same IMEI hash, different SIM. We track this.

**Behavioral Baseline Deviation**
Every registered worker builds a behavioral baseline over their first few weeks — typical working hours, typical zone, typical order frequency. When someone who normally works 10am–4pm in Coimbatore suddenly files a flood claim for a Chennai zone at 11pm, that's outside their baseline. One anomaly is noise. Fifty workers all deviating from their baseline in the same direction on the same night is a signal.

**Claim-to-Premium Ratio Spike**
In a healthy pool, the claim ratio stays within expected actuarial ranges. When a sudden event pushes the ratio to 300% of normal — especially for a zone that historically had low disruption frequency — we pause automated payouts and require a secondary verification step. The pool doesn't drain because the second gate never opens.

---

### How We Protect Honest Workers While Blocking Bad Actors

This is the hardest part. Getting this wrong means a genuine worker sitting in a flooded street doesn't get paid because our system got scared. That's unacceptable. We don't want to build a paranoid system that treats every worker as a suspect.

Our approach has three layers:

**Tier 1 — Auto-Approve (Low Risk)**
Workers with 4+ weeks of verified platform activity, consistent GPS history, no previous flags, and claim behavior matching their baseline get paid immediately. No delay. These workers have earned trust through their track record.

**Tier 2 — Soft Hold (Medium Risk)**
New workers (less than 2 weeks on platform), workers with one or two minor anomalies, or workers whose GPS trail has gaps but not impossible jumps — they get a 2-hour hold. During this window, we send a simple one-tap verification: "Are you currently unable to work due to [event]? Tap Yes to confirm." If they confirm, payout releases. Most genuine workers respond within minutes. Fraudsters using automated scripts often don't.

**Tier 3 — Full Review (High Risk)**
Workers flagged by GPS spoofing indicators, part of a timing cluster, or linked to a known referral fraud network — their claim goes to manual review. They are notified immediately: "Your claim is under review. We'll update you within 24 hours." They are not accused of fraud. They are simply told the system needs more time. If the review clears them, they get paid with a small delay bonus to compensate for the wait.

Nobody is permanently blocked based on a single flag. Every flag is a probability score, not a verdict. A worker needs to cross multiple independent thresholds before a payout is stopped completely.

---

### Why GPS Spoofing Alone Isn't Enough for Fraudsters

Think about what a fraudster actually needs to do to beat GigShield:

1. Spoof GPS to a flood-affected zone ✓ (easy, free apps exist)
2. Have platform activity history in that zone ✗ (hard — requires actually working there for weeks)
3. Match accelerometer/sensor data to outdoor movement ✗ (hard — requires real physical movement)
4. File the claim outside the coordinated timing window ✗ (hard — coordination itself is the evidence)
5. Not be connected to other flagged accounts ✗ (hard — fraud rings share infrastructure)

Any single check is bypassable. All five together? The attack surface shrinks dramatically. That's the point. We don't rely on any one signal. We make it expensive — in time, effort, and coordination — to fake a legitimate claim.

---

### Lessons From the Market Crash

The attack revealed one gap: our original system trusted the weather trigger too much. If IMD confirms rain in a zone, we assumed everyone claiming in that zone was legitimate. The Market Crash showed that a real weather event can be used as cover for a coordinated fraud wave. The disruption is real. The claimants are not.

The fix is separating two questions we were treating as one:

- **Is the disruption real?** → Weather API answers this.
- **Was this specific worker actually affected?** → Behavioral data answers this.

Both questions need independent answers before a payout goes out. That's the core change. The weather API is not enough. It never was.

---

*"The pool belongs to the community. Protecting it from fraudsters is how we protect every honest worker who depends on it."*

---

##  Our Solution — The GigShield சீட்டு Model

GigShield is inspired by the traditional Tamil **சீட்டு (Chittu Fund)** — a community savings tradition where members pool small weekly amounts. When disruption strikes, affected workers get paid from the pool automatically.

```
Worker joins → ₹20–60/week auto-deducted → Community pool grows
       ↓
Disruption detected (AI + Weather APIs)
       ↓
Auto-payout to UPI in < 30 seconds 
```

**Key differentiators:**
-  Zero paperwork — fully automated
-  Instant UPI payout — no claim filing needed
- AI fraud detection — keeps pool healthy
- Only ₹20–60/week — affordable for every worker
- சீட்டு community pool — workers' money, workers' protection

---

##  Persona & Scenario

### Our Persona
**Food Delivery Partner** on Zomato / Swiggy

| Attribute | Detail |
|-----------|--------|
| Weekly Earnings | ₹2,500–₹5,000 |
| Working Hours | 8–12 hrs/day outdoors |
| Risk Exposure | Highly rain-sensitive |
| Employment Type | No formal benefits |
| Payout Cycle | Weekly by platform |
| Device | Android smartphone |

### Sample Scenario — Rajan from Chennai

| Day | Event |
|-----|-------|
| **MON** | Rajan earns ₹700. GigShield auto-deducts ₹60 → community pool. |
| **TUE** | Heavy rain (82mm) detected in Chennai by OpenMeteo + IMD API. |
| **TUE** | AI confirms disruption (confidence 94%). Fraud check: PASSED. |
| **TUE** | ₹300 payout auto-sent to Rajan's UPI. Zero action from Rajan. |
| **SUN** | Week ends. Contributed ₹60 — received ₹300 back. Net gain: ₹240. |
| **NET** | Without GigShield: Rajan would have lost ₹300 with no recourse. |

---

##  Application Workflow

```
01. Worker Onboarding
    └─ Register via web app (name, phone, district, platform, weekly earnings)

02. AI Risk Profiling
    └─ Fetch district risk score from historical weather data
    └─ Calculate weekly premium dynamically

03. Policy Creation
    └─ Policy auto-created
    └─ ₹20–60/week auto-deducted from platform payout every Monday
    └─ No bank details needed — deducted directly from platform payouts

04. Real-Time Monitoring
    └─ APIs check weather, news, curfew alerts every 30 minutes
    └─ Covers all registered worker zones simultaneously

05. Auto Claim Trigger
    └─ If disruption threshold crossed → all workers in zone identified instantly
    └─ No manual claim required from worker

06. Instant UPI Payout
    └─ Fraud check runs automatically
    └─ If passed → payout sent to UPI in under 30 seconds
```

**Platform Choice: WEB APP**
> No install needed. Works on any Android browser. Optimised for low-end phones common among delivery workers.

---

##  Weekly Premium Model — சீட்டு Style

### Formula
```
Premium = Weekly Earnings × Risk Rate (2–5%) × Platform Multiplier × Season Multiplier
```

### District Risk Rate (from historical weather data)
| Risk Level | Score | Rate | Weekly Premium |
|------------|-------|------|----------------|
| High Risk | ≥ 100 | 5% | ₹60/week |
| Medium Risk | ≥ 70 | 3.5% | ₹40/week |
| Low Risk | < 70 | 2% | ₹20/week |

### Platform Multiplier
| Platform | Multiplier | Reason |
|----------|-----------|--------|
| Zomato / Swiggy | 1.1× | Outdoor, rain-sensitive |
| Zepto / Blinkit | 1.0× | Quick commerce |
| Amazon / Flipkart | 0.9× | Scheduled routes |
| Dunzo | 1.05× | Hyperlocal delivery |

### Season Multiplier
| Season | Months | Multiplier |
|--------|--------|-----------|
| Monsoon | Jun–Sep | 1.5× |
| Summer | Mar–May | 1.2× |
| Autumn | Oct–Nov | 0.9× |
| Winter | Dec–Feb | 0.8× |

### சீட்டு Pool Model
> All weekly premiums pool together. Payouts come from pool — not from company reserves. If pool is healthy (>3× monthly claims), premiums stay low. Surplus rolls to next week — **workers never lose their contribution.**

---

##  Parametric Triggers — Zero-Touch Auto-Claim
| Trigger | Parameter | Data Source | Severity | Payout |
|---------|-----------|-------------|----------|--------|
|  Heavy Rainfall | > 50mm in 24h | OpenMeteo API | High | 75% daily |
|  Extreme Heat | > 42°C temperature | IMD API | Medium | 50% daily |
|  High Wind Speed | > 35 km/h | OpenMeteo API | Medium | 50% daily |
|  Flood Warning | Official IMD alert | IMD Alerts API | High | 75% daily |
|  Govt Curfew | Movement restricted | GDELT News API | High | 75% daily |
|  Transport Strike | Delivery zones blocked | Local Auth API | Medium | 50% daily |

> **All 6 triggers are FULLY AUTOMATED** — payout sent without worker filing any claim or making any phone call.

---

##  AI / ML Integration Plan

### 01. Dynamic Risk Profiling
- 10+ years IMD weather data analyzed
- District-level risk score calculated (0–130)
- Weighted formula: Rainfall 40% + Max Rain 25% + Wind Speed 20% + Disruption Rate 15%

### 02. Premium Calculation ML
- Real-time season & platform multipliers applied
- Weekly auto-recalibration per district
- Prevents under-pricing and over-charging
- Capped: Min ₹20 / Max ₹60 per week

### 03. Fraud Detection Engine
- Duplicate claim detection (24h window)
- GPS location vs registered zone check
- Claim velocity analysis (claims per week)
- Platform activity gap cross-verification

### 04. Parametric Auto-Trigger
- Multi-API monitoring every 30 minutes
- 2+ source confirmation required before triggering
- Confidence threshold ≥ 80% required
- Zone-based worker batch identification

---

##  Historical Data Analysis

**Dataset:** Kaggle — Indian Rainfall & Weather Prediction Dataset
**Link:** https://www.kaggle.com/datasets/ameydilipmorye/indian-rainfall-and-weather-data/data
**Format:** XLSX → loaded with `pandas read_excel()`

**Columns used:** `date_of_record`, `district`, `state`, `rainfall`, `avg_temp`, `max_temp`, `wind_speed`, `latitude`, `longitude`

**Analysis Steps:**
```
Load XLSX
  → Flag disruption days (rain > 50mm / temp > 40°C / wind > 30 km/h)
  → Aggregate by district
  → Calculate Risk Score (weighted formula)
  → Assign Premium Tier (High / Medium / Low)
  → Export district_risk_profile.csv
```

**Risk Score Formula:**
```python
risk_score = (
    avg_rainfall    * 0.40 +
    max_rainfall    * 0.25 +
    avg_wind_speed  * 0.20 +
    disruption_rate * 0.15
)
```

**Output:** `district_risk_profile.csv` — used by the backend to set weekly premiums per worker zone.

---



##  Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, Flask REST API, Pandas, NumPy, Scikit-learn, SQLite / PostgreSQL |
| **Frontend** | HTML5 + CSS3, Vanilla JavaScript, Chart.js, Mobile-first, No framework |
| **APIs** | OpenMeteo (weather), IMD India (alerts), GDELT (news/curfews), Razorpay mock UPI, Platform APIs (mock) |
| **ML / Data** | Kaggle weather dataset, district_risk_profile.csv, Risk scoring model, Fraud detection rules, Pandas pipeline |



## System Design & Security

### System Reliability
- Multi-source APIs with backup support
- Retry mechanism for API failures
- Data caching during downtime

### Trust & Safety
- Fraud detection (duplicate + GPS check)
- Multi-source validation before any payout
- Transparent payout rules visible to all workers

---

## Market Opportunity

| Metric | Data |
|--------|------|
| Gig workers in India (2025) | 15+ Million |
| Expected by 2030 | 23 Million |
| Avg weekly earnings | ₹2,500–₹5,000 |
| Income loss from disruptions | 20–30% monthly |
| Target (Phase 1) | Food delivery, Tier 1 & 2 cities |

> "A small weekly premium from millions creates a large, sustainable protection ecosystem."



*Built for Guidewire DEVTrails 2026 | Phase 1 | GigShield Team*
