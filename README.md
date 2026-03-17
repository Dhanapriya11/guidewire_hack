🛡️ GigShield — AI-Powered Parametric Insurance for India's Gig Workers

> Like the traditional Tamil **சீட்டு (Chittu Fund)** — community-powered, automated, and instant.

**Team:** Akilan B | Dhanapriya VA | Dharshini S | Gandhiraj J
**Hackathon:** Guidewire DEVTrails 2026 — Phase 1 Submission
**Persona:** Food Delivery Partners (Zomato / Swiggy)

---

## 📌 The Problem

India's platform-based delivery workers are the backbone of our digital economy. Yet they are completely unprotected from income loss caused by external disruptions:

- 🌧️ **No Weather Protection** — Heavy rain halts deliveries. Zero income, zero safety net.
- 🚫 **No Curfew Coverage** — Unplanned lockdowns mean instant earnings loss.
- 💸 **No Savings Buffer** — Gig workers live week-to-week with no financial cushion.
- 📋 **No Insurance Access** — Traditional insurers ignore this informal workforce.

> **20–30% of monthly income** is lost during disruptions. India has **15 Million+ platform gig workers** — none of them have income disruption insurance.

**Sources:**
- [1] Guidewire DEVTrails 2026 Problem Statement
- [2] NITI Aayog — India's Booming Gig Economy, June 2022, Pg.25 Table 15
- [3] ILO India Gig Worker Report 2022

---

## 💡 Our Solution — The GigShield சீட்டு Model

GigShield is inspired by the traditional Tamil **சீட்டு (Chittu Fund)** — a community savings tradition where members pool small weekly amounts. When disruption strikes, affected workers get paid from the pool automatically.

```
Worker joins → ₹20–60/week auto-deducted → Community pool grows
       ↓
Disruption detected (AI + Weather APIs)
       ↓
Auto-payout to UPI in < 30 seconds ⚡
```

**Key differentiators:**
- ✅ Zero paperwork — fully automated
- ✅ Instant UPI payout — no claim filing needed
- ✅ AI fraud detection — keeps pool healthy
- ✅ Only ₹20–60/week — affordable for every worker
- ✅ சீட்டு community pool — workers' money, workers' protection

---

## 🎯 Persona & Scenario

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

## 🔄 Application Workflow

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

## 💰 Weekly Premium Model — சீட்டு Style

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

## ⚡ Parametric Triggers — Zero-Touch Auto-Claim

| Trigger | Parameter | Data Source | Severity | Payout |
|---------|-----------|-------------|----------|--------|
| 🌧️ Heavy Rainfall | > 50mm in 24h | OpenMeteo API | High | 75% daily |
| 🌡️ Extreme Heat | > 42°C temperature | IMD API | Medium | 50% daily |
| 💨 High Wind Speed | > 35 km/h | OpenMeteo API | Medium | 50% daily |
| 🌊 Flood Warning | Official IMD alert | IMD Alerts API | High | 75% daily |
| 🚫 Govt Curfew | Movement restricted | GDELT News API | High | 75% daily |
| ✊ Transport Strike | Delivery zones blocked | Local Auth API | Medium | 50% daily |

> **All 6 triggers are FULLY AUTOMATED** — payout sent without worker filing any claim or making any phone call.

---

## 🤖 AI / ML Integration Plan

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

## 📊 Historical Data Analysis

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

## 🏗️ System Architecture

```
🌧️ Weather APIs / External Data
   (OpenMeteo, IMD, News APIs, Location Data)
          ↓
⚙️ Data Processing Layer
   (Cleaning, Filtering, Feature Extraction)
          ↓
🤖 AI Risk Model
   (Risk Score Calculation using ML + Historical Data)
          ↓
🧠 Decision Engine
   (Threshold Check + Multi-Source Validation — Confidence ≥ 80%)
          ↓
⚡ Auto Claim Trigger System
   (Zone-based Worker Identification)
          ↓
🔐 Fraud Detection Engine
   (Duplicate Check, GPS Validation, Activity Check)
          ↓
💰 Instant UPI Payout System
   (Auto-transfer within 30 seconds)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, Flask REST API, Pandas, NumPy, Scikit-learn, SQLite / PostgreSQL |
| **Frontend** | HTML5 + CSS3, Vanilla JavaScript, Chart.js, Mobile-first, No framework |
| **APIs** | OpenMeteo (weather), IMD India (alerts), GDELT (news/curfews), Razorpay mock UPI, Platform APIs (mock) |
| **ML / Data** | Kaggle weather dataset, district_risk_profile.csv, Risk scoring model, Fraud detection rules, Pandas pipeline |

---

## 📅 Development Plan

| Phase | Deadline | Deliverables |
|-------|----------|-------------|
| **Phase 1** | Mar 20 | Idea + Risk Analysis + UI Prototype + README + 2-min video |
| **Phase 2** | Apr 4 | Registration, Policies, Claims, Dynamic Pricing |
| **Phase 3** | Apr 17 | Fraud Detection, Payouts, Analytics Dashboard, Final submission |

---

## 🔒 System Design & Security

### System Reliability
- Multi-source APIs with backup support
- Retry mechanism for API failures
- Data caching during downtime

### Trust & Safety
- Fraud detection (duplicate + GPS check)
- Multi-source validation before any payout
- Transparent payout rules visible to all workers

---

## 📈 Market Opportunity

| Metric | Data |
|--------|------|
| Gig workers in India (2025) | 15+ Million |
| Expected by 2030 | 23 Million |
| Avg weekly earnings | ₹2,500–₹5,000 |
| Income loss from disruptions | 20–30% monthly |
| Target (Phase 1) | Food delivery, Tier 1 & 2 cities |

> "A small weekly premium from millions creates a large, sustainable protection ecosystem."

---

## 📁 Repository Structure

```
gigshield/
├── README.md                    ← This file
├── backend/
│   ├── app.py                   ← Flask REST API
│   ├── risk_engine.py           ← AI risk scoring & premium calculation
│   ├── fraud_detector.py        ← ML fraud detection (6 methods)
│   ├── payout_engine.py         ← Mock UPI payout processing
│   └── requirements.txt
├── frontend/
│   └── index.html               ← Complete web app (single file)
└── ml/
    ├── analysis.py              ← Run this first to generate risk profiles
    └── district_risk_profile.csv ← Output: district risk scores & premiums
```

---

## 🚀 How to Run

```bash
# Step 1 — Generate risk data from Kaggle dataset
cd ml/
python analysis.py    # place indian_weather.xlsx here first

# Step 2 — Start backend
cd backend/
pip install -r requirements.txt
cp ../ml/district_risk_profile.csv .
python app.py         # runs on http://localhost:5000

# Step 3 — Open frontend
open frontend/index.html   # works standalone in any browser
```

---

## 🔗 Links
- **Dataset:** https://www.kaggle.com/datasets/ameydilipmorye/indian-rainfall-and-weather-data/data

---

## 👥 Team

| Name | Role |
|------|------|
| Akilan B | Backend & ML |
| Dhanapriya VA | Frontend & UI |
| Dharshini S | Data Analysis |
| Gandhiraj J | System Design |

---

*Built for Guidewire DEVTrails 2026 | Phase 1 | GigShield Team*
