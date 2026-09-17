# CarbonLoop (Problem Statement ES-02)
**Closed-Loop Verifiable Carbon Accounting & Decarbonization Intelligence Platform**

---

## 1. Overview & Problem Statement

**CarbonLoop** addresses **Problem Statement ES-02**: monitoring and reducing carbon footprints at individual and organizational levels.

Unlike traditional enterprise carbon platforms that rely on black-box spend proxies and US/EU-centric emissions factors, CarbonLoop enforces:
1. **100% Deterministic Calculations**: $\text{Emissions} = \text{Activity} \times \text{Factor}$, driven by primary official sources:
   - **India National Grid Electricity**: **0.7275 kg CO₂e / kWh** (Central Electricity Authority CO₂ Baseline Database Version 20.0, FY 2023–24).
   - **Fuels, Transport, Waste, Water**: UK Department for Energy Security and Net Zero (DESNZ) / DEFRA 2024 Conversion Factors v1.1.
2. **Strict AI Boundary**: Downstream narration, hotspot explanation, and decarbonization recommendations only. The AI layer is architecturally isolated and never calculates or modifies numbers (`Raw Data → Validation → Deterministic Engine → Verified JSON → AI`).
3. **5-Tuple Click-to-Trace Audit**: Every single computed metric traces directly back to:
   $$\text{Traceability} = (\text{Activity Input}, \text{Normalized Unit}, \text{Factor ID}, \text{Official Gazette Source}, \text{Formula}, \text{Final CO}_2\text{e})$$
4. **Data Quality Labeling**: Every number in the UI and API is explicitly categorized: `[MEASURED]`, `[USER-ENTERED]`, `[SYNTHETIC DEMO DATA]`, `[ESTIMATE]`, or `[SIMULATION/PROJECTION]`.
5. **Closed-Loop Reduction Simulator**: Interactive parameter adjustment (rooftop solar %, HVAC thermostat °C, transit modal shift %, flight reduction %, waste composting %) displaying projected residual emissions versus measured baseline.

---

## 2. System Architecture

```
                                  STRICT SECURITY & INTEGRITY BOUNDARY
                                                     │
┌───────────────────────┐                            │
│   RAW ACTIVITY DATA   │ (Utility Bills, Fuel Logs, │
│      (User/API)       │  Commuter Surveys, Waste)  │
└──────────┬────────────┘                            │
           │                                         │
           ▼                                         │
┌───────────────────────┐                            │
│  SCHEMA VALIDATION    │ (Rejects negative numbers, │
│      & SANITIZING     │  enforces unit fidelity)   │
└──────────┬────────────┘                            │
           │                                         │
           ▼                                         │
┌───────────────────────┐                            │
│  DETERMINISTIC CARBON │ (Pure math: E = A × EF;    │
│      CALC ENGINE      │  CEA v20.0 + DESNZ 2024;   │
│  (100% Python/SQLite) │  SEBI BRSR KPIs; Scenarios)│
└──────────┬────────────┘                            │
           │                                         │
           ▼                                         │
┌───────────────────────┐                            │
│   VERIFIED NUMERIC    │ (Immutable Audit Records,  │
│    RESULTS PAYLOAD    │  Traceability 5-Tuple,     │
│  (Database & State)   │  Data Quality Tags)        │
└──────────┬────────────┘                            │
           │                                         │
═══════════╪═════════════════════════════════════════╪══════════════════════════
           │ READ-ONLY (Deterministic verified JSON) │
           ▼                                         │
┌───────────────────────┐                            │
│     AI LAYER (LLM)    │ • Hotspot narration        │
│  (Gemini / Anthropic) │ • Contextual explanations  │
│  [NO WRITE/NO COMPUTE]│ • Policy recommendations   │
│                       │ • Plain-language summaries │
└───────────────────────┘                            │
                                                     │
```

---

## 3. Technology Stack

- **Backend**: FastAPI (Python 3.12), Pydantic v2
- **Database**: SQLite with multi-tenant foreign keys and audit history
- **Deterministic Calculation Engine**: Pure Python mathematical module with float precision
- **Frontend**: Single Page Application (SPA), HTML5, Tailwind CSS, Chart.js, Lucide Icons
- **Security**: JWT Authentication (HS256), salted password hashing, organization scoping

---

## 4. GHG Scope & Category Coverage

CarbonLoop explicitly maps supported activities to GHG Protocol and SEBI BRSR scopes:

| Activity | Scope | Category | Calculation Method | Verified Source |
| :--- | :--- | :--- | :--- | :--- |
| **Grid Electricity** | Scope 2 | Purchased Electricity (Location-based) | $\text{kWh} \times 0.727493$ | CEA CO₂ Baseline Database v20.0 |
| **Diesel Generator (DG Set)** | Scope 1 | Direct Stationary Combustion | $\text{Litres} \times 2.512300$ | DESNZ 2024 v1.1 |
| **Fleet Petrol Vehicles** | Scope 1 | Direct Mobile Combustion | $\text{Litres} \times 2.084520$ | DESNZ 2024 v1.1 |
| **Canteen Commercial LPG** | Scope 1 | Direct Stationary Combustion | $\text{kg} \times 2.939361$ | DESNZ 2024 v1.1 |
| **Compressed Natural Gas (CNG)** | Scope 1 | Direct Stationary/Mobile Combustion | $\text{kg} \times 2.568164$ | DESNZ 2024 v1.1 |
| **Employee Bus Commute** | Scope 3 | Category 7: Employee Commuting | $\text{pkm} \times 0.108460$ | DESNZ 2024 v1.1 |
| **Employee Rail/Metro Commute**| Scope 3 | Category 7: Employee Commuting | $\text{pkm} \times 0.035460$ | DESNZ 2024 v1.1 |
| **Employee Two-Wheeler Commute**| Scope 3 | Category 7: Employee Commuting | $\text{km} \times 0.113670$ | DESNZ 2024 v1.1 |
| **Employee Solo Car Commute** | Scope 3 | Category 7: Employee Commuting | $\text{km} \times 0.169840$ | DESNZ 2024 v1.1 |
| **Domestic Business Flights** | Scope 3 | Category 6: Business Travel | $\text{pkm} \times 0.272570$ (with RF)| DESNZ 2024 v1.1 |
| **Commercial Landfill Waste** | Scope 3 | Category 5: Waste Generated in Ops | $\text{kg} \times 0.520334$ | DESNZ 2024 v1.1 |
| **Mains Water Utility** | Scope 3 | Category 1/5: Water Supply & Treatment | $\text{m}^3 \times 0.338850$ | DESNZ 2024 v1.1 |

*Note on Exclusions:* Scope 3 Category 1 (Purchased Goods spend-based EEIO) and Category 2 (Capital Goods) are excluded in v1 due to lack of primary invoice activity data and documented 40–80% variance in spend-based proxies.

---

## 5. Demonstration Organization: GreenTech Demo Pvt. Ltd.

CarbonLoop comes pre-loaded with **GreenTech Demo Pvt. Ltd.**, an Indian technology and light manufacturing SME in Mumbai, Maharashtra (50 employees, 15,000 sq ft facility, 12 months full calendar year baseline).

- **Total Annual Footprint**: **176.534 t CO₂e** (176,534.49 kg CO₂e)
- **Scope 1**: 14.113 t CO₂e (8.0%)
- **Scope 2 (Primary Hotspot)**: **122.364 t CO₂e (69.3%)**
- **Scope 3**: 40.057 t CO₂e (22.7%)
- **Per-Employee Carbon Intensity**: **3.531 t CO₂e / employee / year** (3,530.69 kg CO₂e)
- **Demo Credentials**:
  - Email: `demo@greentech.in`
  - Password: `demo1234`
- **Mandatory Label**: Labeled **SYNTHETIC DEMONSTRATION DATASET** across the user interface and database.

---

## 6. How to Run and Test

### 6.1 Running the Automated Test Suite (10 Hand-Computed Cases)
```bash
cd /home/manas/carbonloop
PYTHONPATH=. ./venv/bin/pytest tests/test_engine.py -v
```
All 10 benchmark test cases pass with numerical tolerance `< 0.01 kg CO₂e`.

### 6.2 Running the Live End-to-End Demo Flow Test
```bash
cd /home/manas/carbonloop
PYTHONPATH=. ./venv/bin/python tests/verify_demo_flow.py
```
Exercises all 10 steps over HTTP against the running server.

### 6.3 Starting the Development Server
```bash
cd /home/manas/carbonloop
PYTHONPATH=. ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Navigate to: `http://localhost:8000` to view the interactive application.

---

## 7. Interactive Demo Flow Walkthrough

1. **Login**: Authenticate as `demo@greentech.in` (auto-logged in on first load).
2. **Dashboard Overview**: Inspect Gross Annual Footprint (176.534 t), Scope 1/2/3 breakdown, 12-month seasonal trend chart, and SEBI BRSR per-employee intensity (3.531 t/emp).
3. **Hotspot Identification**: The system flags Scope 2 Grid Electricity as the dominant hotspot at 69.3% of total emissions.
4. **Activity Log & Audit**: Click on any row to open the **Click-to-Trace Provenance Modal** showing the full 5-tuple: raw input, normalized value, factor ID, official source authority with link to CEA / DESNZ portal, math formula, and output.
5. **Log New Activity**: Click "+ Log Activity", select a category (e.g., 15,000 kWh Grid Electricity), enter notes, and submit. The deterministic engine calculates results on-the-fly and updates the database.
6. **Decarbonization Simulator**: Navigate to the simulator tab, adjust sliders for Rooftop Solar PV, HVAC setpoint offset, transit modal shift, flight reduction, and waste composting. View immediate projected avoided carbon and dual-series comparison against the measured baseline (strictly tagged `SIMULATION/PROJECTION`).
7. **Target Setting**: Set an SBTi-aligned 30% reduction commitment by 2030 and view distance-to-target tracking.
8. **AI Climate Insights**: Review technical narration explaining the drivers of the electricity hotspot, regulatory context under SEBI BRSR Core, and recommended action steps.
9. **Factor Registry**: Browse the complete catalog of verified emission factors with official citations.

---

## 8. Limitations & Assumptions

1. **Grid Electricity Factor**: CarbonLoop uses the CEA Version 20.0 national weighted average grid factor (0.7275 kg CO₂/kWh). While regional state grids vary slightly, the national combined grid factor is the standard recognized under Indian CDM and corporate reporting frameworks.
2. **Flight Radiative Forcing**: Business travel flights apply DESNZ factors with Radiative Forcing (RF) to capture high-altitude indirect warming effects.
3. **Decarbonization Simulations**: Scenario outputs are explicitly labeled `SIMULATION/PROJECTION` and do not represent realized reductions until physically measured and logged in future accounting periods.
