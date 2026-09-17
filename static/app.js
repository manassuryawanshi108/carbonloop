/**
 * CarbonLoop Application Logic
 * Reactive Dashboard, Chart.js Visualizations, Traceability Modal, and Scenario Engine
 */

let authToken = localStorage.getItem("carbonloop_token");
let currentUser = null;
let monthlyTrendChartInstance = null;
let scopeDonutChartInstance = null;
let scenarioCompareChartInstance = null;

const FACTOR_UNITS = {
  "ELEC_IN_GRID": "kWh",
  "FUEL_DIESEL_L": "L",
  "FUEL_PETROL_L": "L",
  "FUEL_LPG_KG": "kg",
  "FUEL_CNG_KG": "kg",
  "TRANSIT_BUS_PKM": "pkm",
  "TRANSIT_RAIL_PKM": "pkm",
  "VEHICLE_MOTO_KM": "km",
  "VEHICLE_CAR_KM": "km",
  "FLIGHT_DOMESTIC_PKM": "pkm",
  "WASTE_LANDFILL_KG": "kg",
  "WATER_MAINS_M3": "m3"
};

// INITIALIZATION
document.addEventListener("DOMContentLoaded", async () => {
  lucide.createIcons();
  await ensureAuthentication();
  await refreshDashboard();
});

// AUTHENTICATION HELPER
async function ensureAuthentication() {
  if (!authToken) {
    // Auto-login to GreenTech Demo Pvt. Ltd. by default for frictionless demo
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "demo@greentech.in", password: "demo1234" })
      });
      if (res.ok) {
        const data = await res.json();
        authToken = data.access_token;
        localStorage.setItem("carbonloop_token", authToken);
        currentUser = data;
      }
    } catch (e) {
      console.error("Auto login failed:", e);
    }
  }

  // Verify profile
  if (authToken) {
    try {
      const res = await fetch("/api/auth/me", {
        headers: { "Authorization": `Bearer ${authToken}` }
      });
      if (res.ok) {
        currentUser = await res.json();
        document.getElementById("user-badge").textContent = currentUser.email;
        if (currentUser.is_synthetic) {
          document.getElementById("demo-banner").classList.remove("hidden");
        }
      } else {
        localStorage.removeItem("carbonloop_token");
        authToken = null;
      }
    } catch (e) {
      console.error("Profile check failed:", e);
    }
  }
}

function logoutOrSwitch() {
  const email = prompt("Enter email to login or test custom tenant (or leave empty to reload demo):", "demo@greentech.in");
  if (!email) return;
  const pwd = prompt("Enter password:", "demo1234");
  if (!pwd) return;

  fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: email.trim(), password: pwd.trim() })
  })
  .then(res => res.json())
  .then(data => {
    if (data.access_token) {
      authToken = data.access_token;
      localStorage.setItem("carbonloop_token", authToken);
      window.location.reload();
    } else {
      alert("Login failed: " + (data.detail || "Invalid credentials"));
    }
  })
  .catch(err => alert("Error: " + err.message));
}

// TAB NAVIGATION
function switchTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(el => el.classList.add("hidden"));
  document.querySelectorAll(".tab-btn").forEach(el => el.classList.remove("active"));

  const targetTab = document.getElementById(`tab-${tabId}`);
  const targetBtn = document.getElementById(`tab-btn-${tabId}`);

  if (targetTab) targetTab.classList.remove("hidden");
  if (targetBtn) targetBtn.classList.add("active");

  lucide.createIcons();

  if (tabId === "dashboard") refreshDashboard();
  if (tabId === "activities") loadActivities();
  if (tabId === "scenarios") runLiveSimulation();
  if (tabId === "targets") loadTargets();
  if (tabId === "ai") fetchAINarrative();
  if (tabId === "factors") loadFactors();
}

// REFRESH DASHBOARD
async function refreshDashboard() {
  if (!authToken) return;
  try {
    const headers = { "Authorization": `Bearer ${authToken}` };

    // 1. Fetch KPIs
    const kpiRes = await fetch("/api/footprint/kpis", { headers });
    if (kpiRes.ok) {
      const kpis = await kpiRes.json();
      document.getElementById("kpi-total-tonnes").textContent = kpis.total_co2e_tonnes.toFixed(3);
      document.getElementById("kpi-total-kg").textContent = Number(kpis.total_co2e_kg).toLocaleString();
      document.getElementById("kpi-scope2-tonnes").textContent = kpis.scope2_tonnes.toFixed(3);
      document.getElementById("kpi-scope3-tonnes").textContent = kpis.scope3_tonnes.toFixed(3);
      document.getElementById("kpi-intensity-employee").textContent = kpis.intensity_per_employee_t.toFixed(3);
      document.getElementById("kpi-intensity-kg").textContent = Number(kpis.intensity_per_employee_kg).toLocaleString();

      const s2Pct = (kpis.scope2_tonnes / Math.max(kpis.total_co2e_tonnes, 0.001) * 100).toFixed(1);
      const s3Pct = (kpis.scope3_tonnes / Math.max(kpis.total_co2e_tonnes, 0.001) * 100).toFixed(1);
      document.getElementById("kpi-scope2-pct").textContent = `${s2Pct}%`;
      document.getElementById("kpi-scope3-pct").textContent = `${s3Pct}%`;
    }

    // 2. Fetch Monthly Trend
    const monthlyRes = await fetch("/api/footprint/monthly", { headers });
    if (monthlyRes.ok) {
      const monthlyData = await monthlyRes.json();
      renderMonthlyTrendChart(monthlyData);
    }

    // 3. Fetch Summary for Scope Donut
    const summaryRes = await fetch("/api/footprint/summary", { headers });
    if (summaryRes.ok) {
      const summary = await summaryRes.json();
      renderScopeDonutChart(summary.scopes);
    }

  } catch (err) {
    console.error("Dashboard refresh error:", err);
  }
}

// RENDER MONTHLY TREND CHART
function renderMonthlyTrendChart(data) {
  const ctx = document.getElementById("monthlyTrendChart").getContext("2d");
  const labels = data.map(d => d.month);
  const s1 = data.map(d => d.scope1_kg);
  const s2 = data.map(d => d.scope2_kg);
  const s3 = data.map(d => d.scope3_kg);

  if (monthlyTrendChartInstance) {
    monthlyTrendChartInstance.destroy();
  }

  monthlyTrendChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Scope 1 (Direct Fuels)",
          data: s1,
          backgroundColor: "rgba(245, 158, 11, 0.8)",
          borderColor: "#f59e0b",
          borderWidth: 1,
          borderRadius: 4
        },
        {
          label: "Scope 2 (Purchased Electricity)",
          data: s2,
          backgroundColor: "rgba(244, 63, 94, 0.85)",
          borderColor: "#f43f5e",
          borderWidth: 1,
          borderRadius: 4
        },
        {
          label: "Scope 3 (Commuting & Travel)",
          data: s3,
          backgroundColor: "rgba(14, 165, 233, 0.8)",
          borderColor: "#0ea5e9",
          borderWidth: 1,
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          stacked: true,
          grid: { color: "rgba(51, 65, 85, 0.3)" },
          ticks: { color: "#94a3b8", font: { family: "monospace", size: 10 } }
        },
        y: {
          stacked: true,
          grid: { color: "rgba(51, 65, 85, 0.3)" },
          ticks: {
            color: "#94a3b8",
            font: { family: "monospace", size: 10 },
            callback: (val) => `${val / 1000} t`
          }
        }
      },
      plugins: {
        legend: {
          position: "top",
          labels: { color: "#cbd5e1", font: { size: 11 } }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${Number(ctx.raw).toLocaleString()} kg CO2e`
          }
        }
      }
    }
  });
}

// RENDER SCOPE DONUT CHART
function renderScopeDonutChart(scopes) {
  const ctx = document.getElementById("scopeDonutChart").getContext("2d");
  const s1 = scopes["Scope 1"] ? scopes["Scope 1"].co2e_kg : 0;
  const s2 = scopes["Scope 2"] ? scopes["Scope 2"].co2e_kg : 0;
  const s3 = scopes["Scope 3"] ? scopes["Scope 3"].co2e_kg : 0;

  if (scopeDonutChartInstance) {
    scopeDonutChartInstance.destroy();
  }

  scopeDonutChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Scope 1 (Direct)", "Scope 2 (Electricity)", "Scope 3 (Value Chain)"],
      datasets: [{
        data: [s1, s2, s3],
        backgroundColor: ["#f59e0b", "#f43f5e", "#0ea5e9"],
        borderColor: "#020617",
        borderWidth: 3,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "70%",
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${Number(ctx.raw).toLocaleString()} kg CO2e`
          }
        }
      }
    }
  });
}

// LOAD ACTIVITIES TABLE
async function loadActivities() {
  if (!authToken) return;
  const scopeFilter = document.getElementById("activity-scope-filter").value;
  let url = "/api/activities?limit=100";
  if (scopeFilter) url += `&scope=${encodeURIComponent(scopeFilter)}`;

  try {
    const res = await fetch(url, {
      headers: { "Authorization": `Bearer ${authToken}` }
    });
    if (!res.ok) return;
    const activities = await res.json();
    const tbody = document.getElementById("activities-table-body");
    tbody.innerHTML = "";

    if (activities.length === 0) {
      tbody.innerHTML = `<tr><td colspan="9" class="py-8 text-center text-slate-500">No activities found matching criteria.</td></tr>`;
      return;
    }

    activities.forEach(act => {
      const tr = document.createElement("tr");
      tr.className = "hover:bg-slate-800/40 transition";

      // Data quality badge color
      let qualityBadge = "";
      if (act.data_quality === "MEASURED") {
        qualityBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-800">MEASURED</span>`;
      } else if (act.data_quality === "SYNTHETIC") {
        qualityBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-950 text-amber-300 border border-amber-800">SYNTHETIC</span>`;
      } else {
        qualityBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300">USER_ENTERED</span>`;
      }

      // Scope badge color
      let scopeColor = "text-slate-400";
      if (act.scope === "Scope 1") scopeColor = "text-amber-400 font-medium";
      if (act.scope === "Scope 2") scopeColor = "text-rose-400 font-bold";
      if (act.scope === "Scope 3") scopeColor = "text-sky-400 font-medium";

      tr.innerHTML = `
        <td class="py-3 px-4 font-mono text-slate-400">${act.activity_date}</td>
        <td class="py-3 px-4 font-medium text-white">
          ${act.activity_type}
          <div class="text-[11px] text-slate-500 font-normal">${act.category}</div>
        </td>
        <td class="py-3 px-4 ${scopeColor}">${act.scope}</td>
        <td class="py-3 px-4 text-right font-mono text-slate-200">${Number(act.activity_value).toLocaleString()} ${act.activity_unit}</td>
        <td class="py-3 px-4 text-right font-mono text-slate-400">${Number(act.factor_value).toFixed(4)}</td>
        <td class="py-3 px-4 text-right font-mono font-bold text-emerald-400">${Number(act.co2e_kg).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
        <td class="py-3 px-4 text-right font-mono text-slate-300">${(act.co2e_tonnes).toFixed(3)}</td>
        <td class="py-3 px-4 text-center">${qualityBadge}</td>
        <td class="py-3 px-4 text-center">
          <button onclick="openTraceModal('${act.id}')" class="text-emerald-400 hover:text-emerald-300 hover:underline font-mono text-[11px] flex items-center justify-center gap-1 mx-auto bg-slate-950 px-2 py-1 rounded border border-slate-800">
            <span>&radic; Trace</span>
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Activities load error:", err);
  }
}

function filterActivities() {
  loadActivities();
}

// CLICK-TO-TRACE MODAL
async function openTraceModal(activityId) {
  if (!authToken) return;
  try {
    const res = await fetch(`/api/activities/${activityId}/trace`, {
      headers: { "Authorization": `Bearer ${authToken}` }
    });
    if (!res.ok) throw new Error("Trace record not found");
    const trace = await res.json();

    const modalBody = document.getElementById("trace-modal-body");
    modalBody.innerHTML = `
      <!-- Activity Summary Box -->
      <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2 font-mono">
        <div class="flex justify-between items-center text-slate-400 pb-2 border-b border-slate-800/80">
          <span>Activity ID: <strong class="text-slate-200">${trace.activity_id}</strong></span>
          <span class="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded">${trace.scope} &bull; ${trace.category}</span>
        </div>
        <div class="grid grid-cols-2 gap-2 text-xs pt-1">
          <div><span class="text-slate-500">Activity Input:</span> <span class="text-emerald-400 font-bold">${Number(trace.raw_input.value).toLocaleString()} ${trace.raw_input.unit}</span></div>
          <div><span class="text-slate-500">Data Quality:</span> <span class="text-amber-400">${trace.raw_input.data_quality}</span></div>
        </div>
        ${trace.raw_input.notes ? `<div class="text-[11px] text-slate-400 pt-1">Notes: ${trace.raw_input.notes}</div>` : ""}
      </div>

      <!-- Verified Emission Factor Box -->
      <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
        <div class="flex justify-between items-start">
          <div>
            <span class="text-[10px] font-mono uppercase bg-emerald-950 text-emerald-300 px-2 py-0.5 rounded border border-emerald-800">Primary Official Source</span>
            <h4 class="font-bold text-sm text-white mt-1">${trace.emission_factor.name}</h4>
          </div>
          <span class="font-mono text-xs bg-slate-800 px-2 py-1 rounded text-slate-300">${trace.emission_factor.factor_id}</span>
        </div>
        <div class="grid grid-cols-2 gap-2 text-xs font-mono pt-1 text-slate-300">
          <div>Coefficient: <strong class="text-emerald-400">${trace.emission_factor.value}</strong> kg CO₂e / ${trace.emission_factor.unit}</div>
          <div>Jurisdiction: <span class="text-slate-300">${trace.emission_factor.geography} (${trace.emission_factor.year})</span></div>
        </div>
        <div class="text-xs text-slate-400 pt-1">
          <strong>Source Authority:</strong> ${trace.emission_factor.source}
        </div>
        <div class="text-xs text-slate-400">
          <strong>Methodology:</strong> ${trace.emission_factor.methodology}
        </div>
        <div class="pt-2">
          <a href="${trace.emission_factor.source_url}" target="_blank" class="text-xs text-emerald-400 hover:text-emerald-300 underline font-mono flex items-center gap-1">
            <span>&rarr; Open Official Gazette / Source Portal</span>
          </a>
        </div>
      </div>

      <!-- Calculation Formula Provenance -->
      <div class="bg-emerald-950/20 p-4 rounded-xl border border-emerald-800/40 space-y-2 font-mono">
        <span class="text-[10px] uppercase text-emerald-400 font-bold tracking-wider">Deterministic Formula Executed</span>
        <div class="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs text-emerald-300 font-bold overflow-x-auto">
          ${trace.calculation_result.formula}
        </div>
        <div class="flex justify-between text-xs pt-1 text-slate-300 font-sans">
          <span>Gross CO₂ Equivalent:</span>
          <span class="font-mono font-bold text-white">${Number(trace.calculation_result.co2e_kg).toLocaleString(undefined, {minimumFractionDigits: 3})} kg CO₂e (${trace.calculation_result.co2e_tonnes.toFixed(4)} t CO₂e)</span>
        </div>
      </div>

      <!-- Standards Compliance Stamp -->
      <div class="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800/80">
        <span class="flex items-center gap-1"><span class="text-emerald-400">&check;</span> ISO 14064-1 Auditable</span>
        <span class="flex items-center gap-1"><span class="text-emerald-400">&check;</span> GHG Protocol Corporate Standard</span>
        <span class="flex items-center gap-1"><span class="text-emerald-400">&check;</span> SEBI BRSR Core Assurable</span>
      </div>
    `;

    document.getElementById("trace-modal").classList.remove("hidden");
  } catch (err) {
    alert("Trace lookup failed: " + err.message);
  }
}

function closeTraceModal() {
  document.getElementById("trace-modal").classList.add("hidden");
}

// LOG ACTIVITY MODAL
function openActivityModal() {
  document.getElementById("activity-modal").classList.remove("hidden");
  updateFormUnits();
  lucide.createIcons();
}

function closeActivityModal() {
  document.getElementById("activity-modal").classList.add("hidden");
}

function updateFormUnits() {
  const type = document.getElementById("form-act-type").value;
  const unit = FACTOR_UNITS[type] || "unit";
  document.getElementById("form-act-unit").value = unit;
}

async function handleActivitySubmit(event) {
  event.preventDefault();
  if (!authToken) return;

  const date = document.getElementById("form-act-date").value;
  const type = document.getElementById("form-act-type").value;
  const val = parseFloat(document.getElementById("form-act-val").value);
  const unit = document.getElementById("form-act-unit").value;
  const quality = document.getElementById("form-act-quality").value;
  const notes = document.getElementById("form-act-notes").value;

  try {
    const res = await fetch("/api/activities", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${authToken}`
      },
      body: JSON.stringify({
        activity_date: date,
        activity_type: type,
        activity_value: val,
        activity_unit: unit,
        data_quality: quality,
        notes: notes
      })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Submission failed");
    }

    closeActivityModal();
    document.getElementById("activity-form").reset();
    await refreshDashboard();
    switchTab("activities");
    alert("Activity calculated and logged with complete audit provenance!");
  } catch (err) {
    alert("Error logging activity: " + err.message);
  }
}

// SCENARIO SIMULATION ENGINE
async function runLiveSimulation() {
  const solar = parseFloat(document.getElementById("slider-solar").value);
  const hvac = parseFloat(document.getElementById("slider-hvac").value);
  const transit = parseFloat(document.getElementById("slider-transit").value);
  const flights = parseFloat(document.getElementById("slider-flights").value);
  const waste = parseFloat(document.getElementById("slider-waste").value);

  document.getElementById("val-solar").textContent = `${solar}%`;
  document.getElementById("val-hvac").textContent = `+${hvac.toFixed(1)} °C`;
  document.getElementById("val-transit").textContent = `${transit}%`;
  document.getElementById("val-flights").textContent = `${flights}%`;
  document.getElementById("val-waste").textContent = `${waste}%`;

  if (!authToken) return;

  try {
    const res = await fetch("/api/scenarios/simulate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${authToken}`
      },
      body: JSON.stringify({
        solar_share_pct: solar,
        hvac_temp_offset_c: hvac,
        transit_shift_pct: transit,
        flight_reduction_pct: flights,
        waste_composting_pct: waste
      })
    });

    if (!res.ok) return;
    const sim = await res.json();

    document.getElementById("sim-base-tonnes").textContent = sim.baseline_total_tonnes.toFixed(3);
    document.getElementById("sim-reduc-tonnes").textContent = sim.total_projected_reduction_tonnes.toFixed(3);
    document.getElementById("sim-reduc-pct").textContent = `${sim.projected_reduction_pct.toFixed(1)}%`;
    document.getElementById("sim-resid-tonnes").textContent = sim.projected_residual_tonnes.toFixed(3);

    // Breakdown list
    const breakdownList = document.getElementById("sim-breakdown-list");
    breakdownList.innerHTML = `
      <div class="flex justify-between items-center bg-slate-950 p-2.5 rounded-lg border border-slate-800">
        <span class="flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-emerald-400"></span> Rooftop Solar PV Generation (${sim.interventions.solar_pv.share_pct}%)</span>
        <span class="font-mono font-bold text-emerald-400">-${sim.interventions.solar_pv.reduction_tonnes.toFixed(3)} t CO₂e</span>
      </div>
      <div class="flex justify-between items-center bg-slate-950 p-2.5 rounded-lg border border-slate-800">
        <span class="flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-teal-400"></span> HVAC Thermostat Setpoint (+${sim.interventions.hvac_efficiency.temp_offset_c}°C)</span>
        <span class="font-mono font-bold text-emerald-400">-${sim.interventions.hvac_efficiency.reduction_tonnes.toFixed(3)} t CO₂e</span>
      </div>
      <div class="flex justify-between items-center bg-slate-950 p-2.5 rounded-lg border border-slate-800">
        <span class="flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-sky-400"></span> Transit Shift to Metro/Bus (${sim.interventions.transit_shift.shift_pct}%)</span>
        <span class="font-mono font-bold text-emerald-400">-${sim.interventions.transit_shift.reduction_tonnes.toFixed(3)} t CO₂e</span>
      </div>
      <div class="flex justify-between items-center bg-slate-950 p-2.5 rounded-lg border border-slate-800">
        <span class="flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-indigo-400"></span> Virtual Meeting Flight Reduction (${sim.interventions.virtual_travel.reduction_pct}%)</span>
        <span class="font-mono font-bold text-emerald-400">-${sim.interventions.virtual_travel.reduction_tonnes.toFixed(3)} t CO₂e</span>
      </div>
      <div class="flex justify-between items-center bg-slate-950 p-2.5 rounded-lg border border-slate-800">
        <span class="flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-amber-400"></span> Landfill Organic Composting (${sim.interventions.waste_diversion.composting_pct}%)</span>
        <span class="font-mono font-bold text-emerald-400">-${sim.interventions.waste_diversion.reduction_tonnes.toFixed(3)} t CO₂e</span>
      </div>
    `;

    renderScenarioCompareChart(sim.baseline_total_tonnes, sim.projected_residual_tonnes, sim.total_projected_reduction_tonnes);

  } catch (err) {
    console.error("Simulation error:", err);
  }
}

function resetScenarioSliders() {
  document.getElementById("slider-solar").value = 40;
  document.getElementById("slider-hvac").value = 2.0;
  document.getElementById("slider-transit").value = 30;
  document.getElementById("slider-flights").value = 25;
  document.getElementById("slider-waste").value = 50;
  runLiveSimulation();
}

function renderScenarioCompareChart(baseTonnes, residualTonnes, reductionTonnes) {
  const ctx = document.getElementById("scenarioCompareChart").getContext("2d");

  if (scenarioCompareChartInstance) {
    scenarioCompareChartInstance.destroy();
  }

  scenarioCompareChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Measured Baseline", "Projected Scenario Outcome"],
      datasets: [
        {
          label: "Residual Footprint (t CO₂e)",
          data: [baseTonnes, residualTonnes],
          backgroundColor: ["rgba(244, 63, 94, 0.8)", "rgba(14, 165, 233, 0.8)"],
          borderRadius: 6
        },
        {
          label: "Projected Avoided Carbon (t CO₂e)",
          data: [0, reductionTonnes],
          backgroundColor: "rgba(16, 185, 129, 0.85)",
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          stacked: true,
          grid: { display: false },
          ticks: { color: "#cbd5e1", font: { weight: "bold", size: 11 } }
        },
        y: {
          stacked: true,
          grid: { color: "rgba(51, 65, 85, 0.3)" },
          ticks: {
            color: "#94a3b8",
            callback: (val) => `${val} t`
          }
        }
      },
      plugins: {
        legend: { position: "top", labels: { color: "#cbd5e1" } },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${Number(ctx.raw).toFixed(3)} t CO₂e`
          }
        }
      }
    }
  });
}

// TARGETS MANAGEMENT
async function loadTargets() {
  if (!authToken) return;
  try {
    const res = await fetch("/api/targets", {
      headers: { "Authorization": `Bearer ${authToken}` }
    });
    if (!res.ok) return;
    const targets = await res.json();
    const container = document.getElementById("target-card-container");
    container.innerHTML = "";

    if (targets.length === 0) {
      container.innerHTML = `<p class="text-xs text-slate-500 text-center py-4">No targets defined yet. Click 'Set New Target'.</p>`;
      return;
    }

    targets.forEach(tgt => {
      const card = document.createElement("div");
      card.className = "bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-3";
      card.innerHTML = `
        <div class="flex justify-between items-start">
          <div>
            <span class="text-[10px] font-mono uppercase bg-emerald-950 text-emerald-300 px-2 py-0.5 rounded border border-emerald-800">Active Reduction Target</span>
            <h4 class="font-bold text-base text-white mt-1">${tgt.target_name}</h4>
          </div>
          <span class="font-mono text-sm font-bold text-emerald-400 bg-slate-900 px-3 py-1 rounded border border-slate-800">-${tgt.target_reduction_pct}% by ${tgt.target_year}</span>
        </div>
        
        <!-- Progress Bar -->
        <div class="space-y-1 pt-2">
          <div class="flex justify-between text-xs text-slate-400 font-mono">
            <span>Distance to Target</span>
            <span class="font-bold text-white">${tgt.progress_pct}% Achieved</span>
          </div>
          <div class="w-full bg-slate-900 h-3 rounded-full overflow-hidden border border-slate-800">
            <div class="bg-gradient-to-r from-emerald-600 to-teal-400 h-full rounded-full transition-all duration-500" style="width: ${Math.min(tgt.progress_pct, 100)}%"></div>
          </div>
        </div>

        <div class="grid grid-cols-3 gap-3 pt-2 text-xs font-mono text-slate-300 border-t border-slate-800/80">
          <div><span class="text-slate-500">Base Footprint:</span> ${(tgt.target_co2e_kg / (1 - tgt.target_reduction_pct/100) / 1000).toFixed(2)} t</div>
          <div><span class="text-slate-500">Target Ceiling:</span> ${(tgt.target_co2e_kg / 1000).toFixed(2)} t</div>
          <div><span class="text-slate-500">Current Footprint:</span> ${(tgt.current_footprint_kg / 1000).toFixed(2)} t</div>
        </div>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    console.error("Targets load error:", err);
  }
}

function openTargetModal() {
  document.getElementById("target-modal").classList.remove("hidden");
}

function closeTargetModal() {
  document.getElementById("target-modal").classList.add("hidden");
}

async function handleTargetSubmit(event) {
  event.preventDefault();
  if (!authToken) return;

  const name = document.getElementById("form-target-name").value;
  const year = parseInt(document.getElementById("form-target-year").value);
  const pct = parseFloat(document.getElementById("form-target-pct").value);

  try {
    const res = await fetch("/api/targets", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${authToken}`
      },
      body: JSON.stringify({
        target_name: name,
        target_year: year,
        target_reduction_pct: pct
      })
    });

    if (!res.ok) throw new Error("Failed to set target");
    closeTargetModal();
    await loadTargets();
    alert("Decarbonization target created successfully!");
  } catch (err) {
    alert("Error setting target: " + err.message);
  }
}

// AI NARRATIVE & INSIGHTS
async function fetchAINarrative() {
  if (!authToken) return;
  const loading = document.getElementById("ai-loading");
  const results = document.getElementById("ai-results-container");

  loading.classList.remove("hidden");
  results.classList.add("hidden");

  try {
    const res = await fetch("/api/ai/narrative", {
      method: "POST",
      headers: { "Authorization": `Bearer ${authToken}` }
    });
    if (!res.ok) throw new Error("AI service unavailable");
    const aiData = await res.json();

    document.getElementById("ai-source-badge").textContent = aiData.source || "CarbonLoop Verified Intelligence Core";
    document.getElementById("ai-exec-summary").textContent = aiData.executive_summary;
    document.getElementById("ai-hotspot-narration").textContent = aiData.hotspot_analysis;
    document.getElementById("ai-regulatory-context").textContent = aiData.regulatory_context;

    const actionsGrid = document.getElementById("ai-actions-grid");
    actionsGrid.innerHTML = "";

    (aiData.recommended_actions || []).forEach((act, idx) => {
      const card = document.createElement("div");
      card.className = "bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2";
      card.innerHTML = `
        <div class="flex justify-between items-start">
          <span class="text-[10px] font-mono bg-emerald-950 text-emerald-300 px-2 py-0.5 rounded border border-emerald-800">${act.impact_scope || "Scope 2"} &bull; ${act.timeframe || "Short-term"}</span>
          <span class="text-slate-500 font-mono text-[10px]">#0${idx + 1}</span>
        </div>
        <h5 class="font-bold text-sm text-white">${act.title}</h5>
        <p class="text-xs text-slate-300 leading-relaxed">${act.description}</p>
      `;
      actionsGrid.appendChild(card);
    });

    loading.classList.add("hidden");
    results.classList.remove("hidden");
  } catch (err) {
    loading.innerHTML = `<p class="text-xs text-rose-400">Failed to generate AI insights: ${err.message}</p>`;
  }
}

// EMISSION FACTORS REGISTRY TABLE
async function loadFactors() {
  try {
    const res = await fetch("/api/factors");
    if (!res.ok) return;
    const factors = await res.json();
    const tbody = document.getElementById("factors-table-body");
    tbody.innerHTML = "";

    factors.forEach(f => {
      const tr = document.createElement("tr");
      tr.className = "hover:bg-slate-800/40 transition";
      tr.innerHTML = `
        <td class="py-3 px-4 font-mono font-bold text-emerald-400">${f.factor_id}</td>
        <td class="py-3 px-4 font-medium text-white">
          ${f.name}
          <div class="text-[11px] text-slate-500 font-normal">${f.methodology}</div>
        </td>
        <td class="py-3 px-4 font-mono text-slate-300">${f.scope}</td>
        <td class="py-3 px-4 text-right font-mono font-bold text-white">${Number(f.value).toFixed(4)}</td>
        <td class="py-3 px-4 font-mono text-slate-400">${f.unit}</td>
        <td class="py-3 px-4 text-slate-300">${f.source}</td>
        <td class="py-3 px-4">
          <a href="${f.source_url}" target="_blank" class="text-emerald-400 hover:underline font-mono text-[11px]">
            Portal &rarr;
          </a>
        </td>
        <td class="py-3 px-4 text-center">
          <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300">
            ${f.confidence}
          </span>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Factors load error:", err);
  }
}
