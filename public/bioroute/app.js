// ═══════════════════════════════════════════════════════
// BioRoute — Frontend Application
// ═══════════════════════════════════════════════════════
const API = '';

// ── State ───────────────────────────────────────────────
let map, layerGroups = {}, currentFilter = 'all', selectedTruckId = null;
let navigationSim = { active: false, paused: false, timer: null, truckId: null, routeData: null, coords: [], stopIndices: [], index: 0, tick: 0, marker: null, traveledLine: null, pendingLine: null, speed: 1 };

// ── Init ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initMap();
  loadDashboard();
  loadReports();
  loadTrucks();
  loadRoutePlan();
  initForms();
  initNavigationSimulator();
});

// ── Tabs ────────────────────────────────────────────────
function initTabs() {
  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
      if (tab.dataset.tab === 'dashboard' && map) setTimeout(() => map.invalidateSize(), 100);
    });
  });
}

// ── Toast ───────────────────────────────────────────────
function showToast(msg, type = 'success') {
  const c = document.getElementById('toast-container');
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.textContent = msg;
  c.appendChild(t);
  setTimeout(() => t.remove(), 4000);
}


function navigateTo(tabName) {
  const tab = document.querySelector(`.nav-tab[data-tab="${tabName}"]`);
  if (tab) tab.click();
}

async function refreshConnectedTabs() {
  await Promise.all([loadReports(currentFilter), loadTrucks()]);
  await loadDashboard();
  await loadRoutePlan();
}

// ── API Helper ──────────────────────────────────────────
async function api(path, opts = {}) {
  try {
    const res = await fetch(`${API}${path}`, { headers: { 'Content-Type': 'application/json' }, ...opts });
    return await res.json();
  } catch (e) { showToast('API Error: ' + e.message, 'error'); return null; }
}

// ══════════════════════════════════════════════════════════
// DASHBOARD
// ══════════════════════════════════════════════════════════
async function loadDashboard() {
  const [summary, analytics] = await Promise.all([
    api('/api/v1/dashboard/summary'),
    api('/api/v1/analytics/savings')
  ]);
  if (summary?.data) renderKPIs(summary.data);
  if (analytics?.data) renderAnalytics(analytics.data);
  loadMapData();
}

function renderKPIs(d) {
  const grid = document.getElementById('kpi-grid');
  grid.innerHTML = [
    kpiCard(d.totalActiveHotspots, 'Active Hotspots', 'orange', 'warning'),
    kpiCard(d.criticalHotspots, 'Critical', 'red', 'critical'),
    kpiCard(d.pendingReports, 'Pending Reports', 'blue', 'info'),
    kpiCard(d.trucksAvailable, 'Trucks Available', 'green', 'success'),
    kpiCard(`${d.estimatedDistanceSavedKm} km`, 'Distance Saved', 'green', 'success'),
    kpiCard(`${d.estimatedCO2ReducedKg} kg`, 'CO₂ Reduced', 'green', 'success'),
  ].join('');
}
function kpiCard(val, label, color, cls) {
  return `<div class="kpi-card ${cls}"><div class="kpi-value ${color}">${val}</div><div class="kpi-label">${label}</div></div>`;
}

function renderAnalytics(d) {
  // Savings
  const sp = document.getElementById('savings-panel');
  sp.innerHTML = [
    savingsCard(d.summary.totalDistanceSavedKm, 'km', 'Distance Saved', 70),
    savingsCard(d.summary.totalFuelSavedLiters, 'L', 'Fuel Saved', 60),
    savingsCard(d.summary.totalCO2ReducedKg, 'kg', 'CO₂ Reduced', 80),
    savingsCard(d.summary.totalUTurnsReduced, '', 'U-Turns Eliminated', 55),
  ].join('');

  // Chart
  const maxVal = Math.max(...d.daily.map(x => x.distanceSavedKm));
  document.getElementById('daily-chart').innerHTML = `<div class="bar-chart">${
    d.daily.map(x => `<div class="bar-col"><div class="bar-value">${x.distanceSavedKm}</div><div class="bar" style="height:${(x.distanceSavedKm/maxVal*100)}%"></div><div class="bar-label">${x.date.slice(5)}</div></div>`).join('')
  }</div>`;

  // Top Areas
  document.getElementById('top-areas').innerHTML = d.topAreas.map(a => `
    <div class="area-item">
      <div><div class="area-name">${a.area}</div><div class="area-count">${a.hotspots} hotspots</div></div>
      <div class="area-score" style="color:${a.priorityScore>=100?'var(--red)':a.priorityScore>=75?'var(--orange)':'var(--blue)'}">${a.priorityScore}</div>
    </div>
  `).join('');
}
function savingsCard(val, unit, label, pct) {
  return `<div class="savings-card"><div class="savings-value">${val}<span style="font-size:14px;color:var(--text-muted)"> ${unit}</span></div><div class="savings-label">${label}</div><div class="savings-bar-container"><div class="savings-bar"><div class="savings-bar-fill" style="width:${pct}%"></div></div></div></div>`;
}

// ══════════════════════════════════════════════════════════
// MAP
// ══════════════════════════════════════════════════════════
function initMap() {
  map = L.map('map', { zoomControl: false }).setView([12.9716, 77.5946], 12);
  L.control.zoom({ position: 'bottomright' }).addTo(map);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '© OpenStreetMap © CARTO', maxZoom: 19
  }).addTo(map);
  layerGroups = { hotspots: L.layerGroup().addTo(map), trucks: L.layerGroup().addTo(map),
    staticRoute: L.layerGroup(), optRoute: L.layerGroup().addTo(map) };
}

async function loadMapData() {
  const [markers, routes] = await Promise.all([api('/api/v1/map/markers'), api('/api/v1/map/routes')]);
  if (markers?.data) renderMarkers(markers.data.markers);
  if (routes?.data) renderRoutes(routes.data.routes);
}

function renderMarkers(markers) {
  layerGroups.hotspots.clearLayers();
  layerGroups.trucks.clearLayers();
  const hotspotListEl = document.getElementById('hotspot-list');
  let hotspotHtml = '';

  markers.forEach(m => {
    if (m.type === 'truck') {
      const icon = L.divIcon({ className: '', html: `<div style="font-size:22px;filter:drop-shadow(0 0 6px rgba(59,130,246,0.6))">🚛</div>`, iconSize: [28, 28], iconAnchor: [14, 14] });
      L.marker([m.latitude, m.longitude], { icon }).bindPopup(`<b>${m.popupData.title}</b><br>Status: ${m.popupData.status}<br>Load: ${m.popupData.currentLoadKg}/${m.popupData.capacityKg} kg`).addTo(layerGroups.trucks);
    } else {
      const color = m.markerColor;
      L.circleMarker([m.latitude, m.longitude], { radius: m.type === 'hotspot' ? 10 : 7, fillColor: color, color: color, weight: 2, opacity: 0.9, fillOpacity: 0.6 })
        .bindPopup(`<b>${m.popupData.title}</b><br>Fill: ${m.popupData.fillLevelPercent}%<br>Score: ${m.popupData.priorityScore}<br>Waste: ${m.popupData.estimatedWasteKg} kg`)
        .addTo(layerGroups.hotspots);

      if (m.type === 'hotspot') {
        const badgeCls = `badge-${m.priorityLevel}`;
        hotspotHtml += `<div class="hotspot-item" onclick="map.setView([${m.latitude},${m.longitude}],15)">
          <div class="hotspot-dot" style="background:${color}"></div>
          <div class="hotspot-info"><div class="hotspot-name">${m.popupData.wasteType.replace(/_/g,' ')}</div><div class="hotspot-area">${m.popupData.area}</div></div>
          <div style="text-align:right"><div class="hotspot-score" style="color:${color}">${m.popupData.priorityScore}</div><span class="hotspot-badge ${badgeCls}">${m.priorityLevel}</span></div>
        </div>`;
      }
    }
  });
  hotspotListEl.innerHTML = hotspotHtml || '<p style="color:var(--text-muted);font-size:13px">No hotspots found</p>';
}

function renderRoutes(routes) {
  layerGroups.staticRoute.clearLayers();
  layerGroups.optRoute.clearLayers();
  const boundsLayers = [];

  routes.forEach(r => {
    if (!r.polyline?.coordinates?.length) return;
    const latlngs = r.polyline.coordinates.map(c => [c[1], c[0]]);
    const routeColor = r.color || '#3B82F6';
    const style = r.routeType === 'static'
      ? { color: '#94A3B8', weight: 2, dashArray: '10, 8', opacity: 0.45 }
      : { color: routeColor, weight: selectedTruckId && r.assignedTruckId === selectedTruckId ? 7 : 5, opacity: selectedTruckId && r.assignedTruckId !== selectedTruckId ? 0.25 : 0.95 };

    const line = L.polyline(latlngs, style).bindPopup(
      `<b>${r.routeType === 'static' ? 'Static baseline' : r.routeName || 'Truck optimized route'}</b><br>` +
      `Truck: ${r.assignedTruckId || 'N/A'}<br>` +
      `Areas: ${(r.assignedAreas || []).join(', ')}<br>` +
      `${r.totalDistanceKm} km · ${r.estimatedDurationMin} min<br>` +
      `Source: ${r.routeSource || 'mock'}` +
      (r.routeWarning ? `<br><span style="color:#F97316">${r.routeWarning}</span>` : '')
    );
    const group = r.routeType === 'static' ? 'staticRoute' : 'optRoute';
    line.addTo(layerGroups[group]);
    if (!selectedTruckId || r.assignedTruckId === selectedTruckId) boundsLayers.push(line);
  });

  if (boundsLayers.length) {
    const all = L.featureGroup(boundsLayers);
    map.fitBounds(all.getBounds(), { padding: [50, 50] });
  }
}

function toggleLayer(name) {
  const btn = document.getElementById(`toggle-${name === 'staticRoute' ? 'static-route' : name === 'optRoute' ? 'opt-route' : name}`);
  if (map.hasLayer(layerGroups[name])) { map.removeLayer(layerGroups[name]); btn.classList.remove('active'); }
  else { map.addLayer(layerGroups[name]); btn.classList.add('active'); }
}

// ══════════════════════════════════════════════════════════
// REPORTS
// ══════════════════════════════════════════════════════════
async function loadReports(status) {
  const url = status && status !== 'all' ? `/api/v1/reports?verificationStatus=${status}` : '/api/v1/reports';
  const res = await api(url);
  if (!res?.data) return;
  const tbody = document.getElementById('reports-tbody');
  tbody.innerHTML = res.data.reports.map(r => {
    const badgeCls = r.verificationStatus === 'verified' ? 'badge-low' : r.verificationStatus === 'rejected' ? 'badge-critical' : 'badge-normal';
    const sevCls = r.severity === 'critical' ? 'badge-critical' : r.severity === 'high' ? 'badge-high' : 'badge-normal';
    return `<tr>
      <td style="font-family:monospace;color:var(--purple)">${r.reportId}</td>
      <td>${r.area}</td>
      <td style="color:var(--yellow)">${(r.wasteCategory||'').replace(/_/g,' ')}</td>
      <td><span class="hotspot-badge ${sevCls}">${r.severity}</span></td>
      <td><span class="hotspot-badge ${badgeCls}">${r.verificationStatus}</span></td>
      <td style="color:var(--text-muted)">${new Date(r.createdAt).toLocaleDateString()}</td>
      <td>${r.verificationStatus === 'pending' ? `<button class="btn btn-sm btn-primary" onclick="verifyReport('${r.reportId}')">✅ Verify</button> <button class="btn btn-sm btn-danger" onclick="rejectReport('${r.reportId}')">❌ Reject</button>` : '—'}</td>
    </tr>`;
  }).join('');
}

function filterReports(status) {
  currentFilter = status;
  document.querySelectorAll('#report-filters .btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  loadReports(status);
}

async function verifyReport(id) {
  const res = await api(`/api/v1/reports/${id}/verify`, { method: 'PATCH', body: JSON.stringify({ adminRemarks: 'Verified via dashboard' }) });
  if (res?.success) {
    showToast(`Report ${id} verified! Hotspot ${res.data.generatedHotspotId} created`);
    await loadReports(currentFilter);
    await loadDashboard();
    await loadMapData();
    await loadRoutePlan();
  }
}
async function rejectReport(id) {
  const res = await api(`/api/v1/reports/${id}/reject`, { method: 'PATCH', body: JSON.stringify({ adminRemarks: 'Rejected' }) });
  if (res?.success) {
    showToast(`Report ${id} rejected`, 'info');
    await loadReports(currentFilter);
    await loadDashboard();
  }
}

// ══════════════════════════════════════════════════════════
// FORMS
// ══════════════════════════════════════════════════════════
function initForms() {
  // Citizen Report
  document.getElementById('citizen-report-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const body = Object.fromEntries(fd);
    body.latitude = parseFloat(body.latitude);
    body.longitude = parseFloat(body.longitude);
    const res = await api('/api/v1/reports', { method: 'POST', body: JSON.stringify(body) });
    if (res?.success) {
      showToast(`Report ${res.data.reportId} submitted! Now visible in Citizen Reports.`);
      e.target.reset();
      currentFilter = 'pending';
      await loadReports('pending');
      await loadDashboard();
      navigateTo('reports');
    }
  });

  // Priority Calculator
  document.getElementById('priority-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const body = Object.fromEntries(fd);
    body.fillLevelPercent = parseInt(body.fillLevelPercent);
    body.hoursOverflow = parseInt(body.hoursOverflow);
    body.isMonsoonSeason = body.isMonsoonSeason === 'true';
    const res = await api('/api/v1/priority/calculate', { method: 'POST', body: JSON.stringify(body) });
    if (res?.data) renderPriorityResult(res.data);
  });
}

function renderPriorityResult(d) {
  const sb = d.scoreBreakdown;
  const color = d.priorityLevel === 'critical' ? 'var(--red)' : d.priorityLevel === 'high' ? 'var(--orange)' : d.priorityLevel === 'normal' ? 'var(--blue)' : 'var(--green)';
  document.getElementById('priority-result').innerHTML = `
    <div class="priority-result">
      <div class="score-row"><span class="label">Base Waste Type Score</span><span class="value">${sb.baseWasteTypeScore}</span></div>
      <div class="score-row"><span class="label">Time Overflow Penalty</span><span class="value">+${sb.timeOverflowPenalty}</span></div>
      <div class="score-row"><span class="label">Population Density Boost</span><span class="value">+${sb.populationDensityBoost}</span></div>
      <div class="score-row"><span class="label">Citizen Severity Boost</span><span class="value">+${sb.citizenSeverityBoost}</span></div>
      <div class="score-row"><span class="label">Toxicity Boost</span><span class="value">+${sb.toxicityBoost}</span></div>
      <div class="score-row score-total">
        <span class="label" style="font-weight:700;color:var(--text-primary)">Final Priority Score</span>
        <span class="value" style="color:${color}">${d.finalPriorityScore}</span>
      </div>
      <div style="margin-top:12px;text-align:center">
        <span class="hotspot-badge badge-${d.priorityLevel}" style="font-size:14px;padding:6px 20px">${d.priorityLevel.toUpperCase()}</span>
      </div>
      <p style="margin-top:12px;font-size:11px;color:var(--text-muted);line-height:1.5">${d.explanation}</p>
    </div>`;
}

function getGeolocation() {
  if (!navigator.geolocation) return showToast('Geolocation not supported', 'error');
  navigator.geolocation.getCurrentPosition(pos => {
    document.querySelector('[name="latitude"]').value = pos.coords.latitude.toFixed(4);
    document.querySelector('[name="longitude"]').value = pos.coords.longitude.toFixed(4);
    showToast('Location detected!');
  }, () => showToast('Location access denied', 'error'));
}

// ══════════════════════════════════════════════════════════
// ROUTE PLAN
// ══════════════════════════════════════════════════════════
async function loadRoutePlan() {
  const url = selectedTruckId ? `/api/v1/routes/tomorrow-plan?truckId=${selectedTruckId}` : '/api/v1/routes/tomorrow-plan';
  const res = await api(url);
  if (!res?.data) {
    document.getElementById('route-plan-content').innerHTML = '<p style="color:var(--text-muted)">No route plan available. Click Run Optimization.</p>';
    return;
  }
  const d = res.data;
  const routes = d.routes || [];
  if (!routes.length) {
    document.getElementById('route-plan-content').innerHTML = '<p style="color:var(--text-muted)">No route for selected truck.</p>';
    return;
  }
  if (!selectedTruckId) selectedTruckId = routes[0].assignedTruck?.truckId;
  const route = routes.find(r => r.assignedTruck?.truckId === selectedTruckId) || routes[0];
  const sv = d.savings || route.savings || { distanceSavedKm: 0, fuelSavedLiters: 0, co2ReducedKg: 0, uTurnsReduced: 0 };

  const selector = `
    <div class="route-selector">
      ${routes.map(r => `
        <button class="route-chip ${r.assignedTruck?.truckId === selectedTruckId ? 'active' : ''}"
          onclick="selectTruckRoute('${r.assignedTruck?.truckId}')"
          style="border-color:${r.routeColor || '#3B82F6'}">
          <span style="color:${r.routeColor || '#3B82F6'}">●</span>
          ${r.assignedTruck?.vehicleNumber || r.assignedTruck?.truckId}
          <small>${(r.assignedAreas || []).join(' · ')}</small>
        </button>
      `).join('')}
    </div>`;

  let html = `${selector}
    <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:20px">
      ${kpiCard(`${route.totalDistanceKm} km`, 'Selected Truck Distance', 'blue', 'info')}
      ${kpiCard(`${route.estimatedDurationMin} min`, 'Est. Duration', 'blue', 'info')}
      ${kpiCard(`${route.totalStops}`, 'Stops For This Truck', 'orange', 'warning')}
      ${kpiCard(`${route.totalWasteKg} kg`, 'Truck Waste Load', 'orange', 'warning')}
    </div>
    <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:20px">
      ${kpiCard(`${sv.distanceSavedKm} km`, 'Total Distance Saved', 'green', 'success')}
      ${kpiCard(`${sv.fuelSavedLiters} L`, 'Total Fuel Saved', 'green', 'success')}
      ${kpiCard(`${sv.co2ReducedKg} kg`, 'Total CO₂ Reduced', 'green', 'success')}
      ${kpiCard(`${sv.uTurnsReduced}`, 'U-Turns Cut', 'green', 'success')}
    </div>
    <div class="card" style="margin-bottom:16px;border-left:4px solid ${route.routeColor || 'var(--blue)'}">
      <div class="section-title">${route.routeName || 'Truck Route'} — ${route.assignedTruck?.vehicleNumber || 'Unassigned'}</div>
      <p style="color:var(--text-muted);font-size:13px;line-height:1.6">
        Assigned areas: <b style="color:var(--green)">${(route.assignedAreas || []).join(', ')}</b><br>
        Route source: <b style="color:var(--green)">${route.routeSource || 'mock'}</b>.
        ${route.routeWarning ? `<br><span style="color:var(--orange)">${route.routeWarning}</span>` : '<br>This route follows road-network geometry and stays inside the truck’s assigned zone.'}
      </p>
      <button class="btn btn-primary" onclick="startTruckRoute('${route.assignedTruck?.truckId}')">▶ Start ${route.assignedTruck?.vehicleNumber || 'Truck'} Route</button>
      <button class="btn btn-secondary" onclick="showTruckRouteOnMap('${route.assignedTruck?.truckId}')">🗺️ Show On Map</button>
    </div>
    <div class="card"><div class="section-title">Directions & Priority Sequence</div>`;

  route.stops.forEach(s => {
    const color = s.priorityLevel === 'critical' ? 'var(--red)' : s.priorityLevel === 'high' ? 'var(--orange)' : 'var(--blue)';
    html += `<div class="stop-item" onclick="navigateTo('dashboard'); setTimeout(()=>map.setView([${s.latitude},${s.longitude}],15),150)">
      <div class="stop-number" style="background:${color};color:white">${s.sequenceNumber}</div>
      <div class="stop-details">
        <div class="stop-address">${s.address}</div>
        <div class="stop-meta">${s.area} · ${s.wasteType.replace(/_/g,' ')} · ${s.estimatedPickupKg} kg · ${s.serviceTimeMinutes} min service · ETA ${new Date(s.eta).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</div>
        <div class="direction-note">${s.directionInstruction || 'Continue to next stop.'}</div>
        <div class="priority-note">${s.priorityInstruction || ''}</div>
      </div>
      <div style="text-align:right"><div style="font-size:16px;font-weight:700;color:${color}">${s.priorityScore}</div><span class="hotspot-badge badge-${s.priorityLevel}">${s.priorityLevel}</span></div>
    </div>`;
  });
  html += '</div>';
  document.getElementById('route-plan-content').innerHTML = html;
}

function selectTruckRoute(truckId) {
  selectedTruckId = truckId;
  loadRoutePlan();
  showTruckRouteOnMap(truckId);
}

async function showTruckRouteOnMap(truckId) {
  selectedTruckId = truckId;
  navigateTo('dashboard');
  const routes = await api(`/api/v1/map/routes?truckId=${truckId}`);
  if (routes?.data) renderRoutes(routes.data.routes);
}

async function startTruckRoute(truckId) {
  const res = await api(`/api/v1/trucks/${truckId}/start`, { method: 'PATCH', body: JSON.stringify({}) });
  if (!res?.success) return;

  showToast(`${res.data.vehicleNumber} navigation started`, 'success');
  await loadTrucks();
  await loadRoutePlan();

  // Google-Maps-like simulation: animate the selected truck along its road polyline.
  await startNavigationSimulation(truckId);
}

async function triggerOptimization() {
  const btn = document.getElementById('btn-optimize');
  btn.disabled = true;
  btn.textContent = '⏳ Running...';
  const res = await api('/api/v1/routes/optimize', { method: 'POST', body: JSON.stringify({ routeDate: '2026-05-09' }) });
  if (!res?.data) { btn.disabled = false; btn.textContent = '⚡ Run Optimization'; return; }
  showToast(`Optimization started — Job ${res.data.jobId}`, 'info');
  const jobId = res.data.jobId;
  const poll = setInterval(async () => {
    const st = await api(`/api/v1/routes/optimization-jobs/${jobId}`);
    if (st?.data?.status === 'completed') {
      clearInterval(poll);
      showToast('Route optimization complete! Road-following route updated.');
      btn.disabled = false;
      btn.textContent = '⚡ Run Optimization';
      await loadRoutePlan();
      await loadMapData();
      await loadDashboard();
      await loadTrucks();
      navigateTo('routes');
    } else if (st?.data?.status === 'failed') {
      clearInterval(poll);
      showToast('Optimization failed', 'error');
      btn.disabled = false;
      btn.textContent = '⚡ Run Optimization';
    }
  }, 2000);
}


// ══════════════════════════════════════════════════════════
// GOOGLE-MAPS-LIKE TRUCK NAVIGATION SIMULATION
// ══════════════════════════════════════════════════════════
function initNavigationSimulator() {
  if (document.getElementById('navigation-panel')) return;
  const panel = document.createElement('div');
  panel.id = 'navigation-panel';
  panel.className = 'navigation-panel hidden';
  panel.innerHTML = `
    <div class="nav-topline">
      <div>
        <div class="nav-title">🧭 Truck Navigation</div>
        <div class="nav-subtitle" id="nav-subtitle">Select a truck and start route</div>
      </div>
      <button class="nav-close" onclick="stopNavigationSimulation(false)">×</button>
    </div>
    <div class="nav-road-strip">
      <div class="nav-road-fill" id="nav-road-fill"></div>
    </div>
    <div class="nav-main-instruction" id="nav-main-instruction">Waiting for route...</div>
    <div class="nav-priority-row">
      <span id="nav-priority-badge" class="hotspot-badge badge-normal">NORMAL</span>
      <span id="nav-step-meta">0 / 0 stops</span>
    </div>
    <div class="nav-next-card" id="nav-next-card"></div>
    <div class="nav-actions">
      <button class="btn btn-sm btn-secondary" id="nav-pause-btn" onclick="toggleNavigationPause()">⏸ Pause</button>
      <button class="btn btn-sm btn-secondary" onclick="changeSimulationSpeed()">⚡ Speed <span id="nav-speed-label">1x</span></button>
      <button class="btn btn-sm btn-danger" onclick="stopNavigationSimulation(true)">■ Stop</button>
    </div>
  `;
  document.body.appendChild(panel);
}

function latLngDistanceMeters(a, b) {
  const R = 6371000;
  const lat1 = a[0] * Math.PI / 180;
  const lat2 = b[0] * Math.PI / 180;
  const dLat = (b[0] - a[0]) * Math.PI / 180;
  const dLon = (b[1] - a[1]) * Math.PI / 180;
  const h = Math.sin(dLat/2)**2 + Math.cos(lat1)*Math.cos(lat2)*Math.sin(dLon/2)**2;
  return 2 * R * Math.asin(Math.sqrt(h));
}

function bearingDegrees(a, b) {
  const lat1 = a[0] * Math.PI / 180;
  const lat2 = b[0] * Math.PI / 180;
  const dLon = (b[1] - a[1]) * Math.PI / 180;
  const y = Math.sin(dLon) * Math.cos(lat2);
  const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);
  return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360;
}

function closestCoordIndex(coords, stop) {
  let best = 0;
  let bestDist = Infinity;
  const point = [Number(stop.latitude), Number(stop.longitude)];
  coords.forEach((c, i) => {
    const d = latLngDistanceMeters(c, point);
    if (d < bestDist) { bestDist = d; best = i; }
  });
  return best;
}

function truckNavIcon(color = '#22C55E', heading = 0) {
  return L.divIcon({
    className: 'truck-nav-icon-wrap',
    iconSize: [42, 42],
    iconAnchor: [21, 21],
    html: `<div class="truck-nav-icon" style="--truck-color:${color}; transform: rotate(${heading}deg)">➤</div>`
  });
}

function getPriorityColor(level) {
  return level === 'critical' ? 'var(--red)' : level === 'high' ? 'var(--orange)' : level === 'normal' ? 'var(--blue)' : 'var(--green)';
}

async function startNavigationSimulation(truckId) {
  navigateTo('dashboard');
  selectedTruckId = truckId;

  const routeRes = await api(`/api/v1/trucks/${truckId}/route`);
  if (!routeRes?.data?.route?.polyline?.coordinates?.length) {
    showToast('No road-following route found for this truck. Run optimization first.', 'error');
    return;
  }

  stopNavigationSimulation(false);

  const routeData = routeRes.data;
  const coords = routeData.route.polyline.coordinates.map(([lng, lat]) => [lat, lng]);
  const stopIndices = (routeData.stops || []).map(s => closestCoordIndex(coords, s));
  const color = routeData.route.routeColor || '#22C55E';

  navigationSim = {
    active: true,
    paused: false,
    timer: null,
    truckId,
    routeData,
    coords,
    stopIndices,
    index: 0,
    tick: 0,
    marker: null,
    traveledLine: null,
    pendingLine: null,
    speed: 1,
  };

  await showTruckRouteOnMap(truckId);

  const start = coords[0];
  const next = coords[1] || coords[0];
  navigationSim.marker = L.marker(start, {
    icon: truckNavIcon(color, bearingDegrees(start, next)),
    zIndexOffset: 9999
  }).addTo(map);

  navigationSim.traveledLine = L.polyline([start], { color, weight: 8, opacity: 0.95 }).addTo(map);
  navigationSim.pendingLine = L.polyline(coords, { color: '#94A3B8', weight: 5, opacity: 0.35, dashArray: '8,8' }).addTo(map);

  map.setView(start, 15);
  document.getElementById('navigation-panel')?.classList.remove('hidden');
  updateNavigationPanel();

  navigationSim.timer = setInterval(simulationTick, 650);
}

async function simulationTick() {
  if (!navigationSim.active || navigationSim.paused) return;

  const step = Math.max(1, navigationSim.speed);
  navigationSim.index = Math.min(navigationSim.index + step, navigationSim.coords.length - 1);
  navigationSim.tick += 1;

  const idx = navigationSim.index;
  const current = navigationSim.coords[idx];
  const next = navigationSim.coords[Math.min(idx + 1, navigationSim.coords.length - 1)] || current;
  const heading = bearingDegrees(current, next);
  const color = navigationSim.routeData.route.routeColor || '#22C55E';

  navigationSim.marker?.setLatLng(current);
  navigationSim.marker?.setIcon(truckNavIcon(color, heading));
  navigationSim.traveledLine?.setLatLngs(navigationSim.coords.slice(0, idx + 1));
  navigationSim.pendingLine?.setLatLngs(navigationSim.coords.slice(idx));

  // Follow camera like a navigation app, but not too aggressively.
  if (navigationSim.tick % 4 === 0) map.panTo(current, { animate: true, duration: 0.5 });

  updateNavigationPanel();

  // Sync the simulated GPS position to backend every few ticks so other tabs update too.
  if (navigationSim.tick % 5 === 0) {
    const progress = Math.round((idx / (navigationSim.coords.length - 1)) * 100);
    const currentStopIndex = getCurrentStopNumber();
    api(`/api/v1/trucks/${navigationSim.truckId}/location`, {
      method: 'PATCH',
      body: JSON.stringify({
        latitude: current[0],
        longitude: current[1],
        heading,
        routeProgressPercent: progress,
        currentStopIndex,
        driverStatus: 'active'
      })
    });
  }

  if (idx >= navigationSim.coords.length - 1) {
    stopNavigationSimulation(true, true);
  }
}

function getNextStopIndex() {
  const idx = navigationSim.index || 0;
  const stops = navigationSim.routeData?.stops || [];
  for (let i = 0; i < navigationSim.stopIndices.length; i++) {
    if (navigationSim.stopIndices[i] >= idx) return i;
  }
  return stops.length - 1;
}

function getCurrentStopNumber() {
  const idx = navigationSim.index || 0;
  let passed = 0;
  for (const stopIdx of navigationSim.stopIndices) {
    if (idx >= stopIdx) passed += 1;
  }
  return passed;
}

function updateNavigationPanel() {
  if (!navigationSim.active || !navigationSim.routeData) return;
  const routeData = navigationSim.routeData;
  const stops = routeData.stops || [];
  const nextStopIdx = getNextStopIndex();
  const nextStop = stops[nextStopIdx];
  const currentCoord = navigationSim.coords[navigationSim.index];
  const progress = Math.round((navigationSim.index / Math.max(1, navigationSim.coords.length - 1)) * 100);
  const completedStops = getCurrentStopNumber();

  const subtitle = document.getElementById('nav-subtitle');
  const fill = document.getElementById('nav-road-fill');
  const main = document.getElementById('nav-main-instruction');
  const badge = document.getElementById('nav-priority-badge');
  const meta = document.getElementById('nav-step-meta');
  const card = document.getElementById('nav-next-card');

  if (!nextStop) {
    main.textContent = 'Return to depot and complete route';
    card.innerHTML = 'All assigned priority stops completed.';
    fill.style.width = `${progress}%`;
    meta.textContent = `${completedStops} / ${stops.length} stops`;
    return;
  }

  const distanceToStop = Math.round(latLngDistanceMeters(currentCoord, [nextStop.latitude, nextStop.longitude]));
  const priorityColor = getPriorityColor(nextStop.priorityLevel);
  const instruction = distanceToStop < 80
    ? `Arriving at Stop ${nextStop.sequenceNumber}: ${nextStop.address}`
    : `Head to Stop ${nextStop.sequenceNumber}: ${nextStop.address}`;

  subtitle.textContent = `${routeData.truck.vehicleNumber} · ${routeData.route.routeName}`;
  fill.style.width = `${progress}%`;
  main.textContent = instruction;
  badge.className = `hotspot-badge badge-${nextStop.priorityLevel}`;
  badge.textContent = `${nextStop.priorityLevel.toUpperCase()} · ${nextStop.priorityScore}`;
  meta.textContent = `${completedStops} / ${stops.length} stops · ${progress}% route`;
  card.innerHTML = `
    <div class="nav-card-line"><b style="color:${priorityColor}">${nextStop.wasteType.replace(/_/g,' ')}</b> · ${nextStop.estimatedPickupKg} kg · ${nextStop.serviceTimeMinutes} min service</div>
    <div class="nav-card-line">${distanceToStop < 1000 ? `${distanceToStop} m` : `${(distanceToStop/1000).toFixed(1)} km`} remaining · ETA ${new Date(nextStop.eta).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</div>
    <div class="nav-card-priority">${nextStop.priorityInstruction || ''}</div>
    <div class="nav-card-zone">Assigned zone only: ${(routeData.route.assignedAreas || []).join(' · ')}</div>
  `;
}

function toggleNavigationPause() {
  if (!navigationSim.active) return;
  navigationSim.paused = !navigationSim.paused;
  const btn = document.getElementById('nav-pause-btn');
  if (btn) btn.textContent = navigationSim.paused ? '▶ Resume' : '⏸ Pause';
}

function changeSimulationSpeed() {
  if (!navigationSim.active) return;
  navigationSim.speed = navigationSim.speed === 1 ? 2 : navigationSim.speed === 2 ? 4 : 1;
  const el = document.getElementById('nav-speed-label');
  if (el) el.textContent = `${navigationSim.speed}x`;
}

async function stopNavigationSimulation(showMsg = true, completed = false) {
  if (navigationSim.timer) clearInterval(navigationSim.timer);
  navigationSim.marker?.remove();
  navigationSim.traveledLine?.remove();
  navigationSim.pendingLine?.remove();
  const truckId = navigationSim.truckId;
  navigationSim = { active: false, paused: false, timer: null, truckId: null, routeData: null, coords: [], stopIndices: [], index: 0, tick: 0, marker: null, traveledLine: null, pendingLine: null, speed: 1 };
  document.getElementById('navigation-panel')?.classList.add('hidden');
  if (showMsg) showToast(completed ? 'Route simulation completed — truck returned to depot.' : 'Navigation stopped', completed ? 'success' : 'info');
  if (truckId) {
    if (completed) {
      await api(`/api/v1/trucks/${truckId}/complete`, { method: 'PATCH', body: JSON.stringify({}) });
    }
    await loadTrucks();
    await loadDashboard();
    await loadMapData();
  }
}

// ══════════════════════════════════════════════════════════
// TRUCKS
// ══════════════════════════════════════════════════════════
async function loadTrucks() {
  const res = await api('/api/v1/trucks');
  if (!res?.data) return;
  const el = document.getElementById('trucks-list');
  el.innerHTML = res.data.trucks.map(t => {
    const loadPct = Math.round((t.currentLoadKg || 0) / t.capacityKg * 100);
    const statusColor = t.status === 'active' ? 'var(--green)' : t.status === 'available' ? 'var(--blue)' : 'var(--orange)';
    const barColor = loadPct > 80 ? 'var(--red)' : loadPct > 50 ? 'var(--orange)' : 'var(--green)';
    const areas = (t.assignedAreas || []).join(' · ') || 'No zone assigned';
    const route = t.routeSummary;
    return `<div class="truck-item ${t.truckId === selectedTruckId ? 'selected' : ''}" style="border-left:4px solid ${t.routeColor || 'var(--blue)'}">
      <div class="truck-icon">🚛</div>
      <div class="truck-info">
        <div class="truck-number">${t.vehicleNumber}</div>
        <div class="truck-status" style="color:${statusColor}">● ${t.status.toUpperCase()}${t.assignedRouteId ? ` — ${t.assignedRouteId}` : ''}</div>
        <div class="truck-zone">Zone: ${areas}</div>
        ${route ? `<div class="truck-zone">Stops: ${route.totalStops} · Critical: ${route.priorityBreakdown.critical} · High: ${route.priorityBreakdown.high}</div>` : '<div class="truck-zone">No active route yet</div>'}
        <div class="truck-load-bar"><div class="truck-load-fill" style="width:${loadPct}%;background:${barColor}"></div></div>
        <div style="font-size:11px;color:var(--text-muted);margin-top:2px">${t.currentLoadKg} / ${t.capacityKg} kg (${loadPct}%)</div>
      </div>
      <div class="truck-actions">
        <button class="btn btn-sm btn-secondary" onclick="selectTruckRoute('${t.truckId}')">View Route</button>
        <button class="btn btn-sm btn-primary" onclick="startTruckRoute('${t.truckId}')" ${route ? '' : 'disabled'}>▶ Start</button>
      </div>
    </div>`;
  }).join('');
}
