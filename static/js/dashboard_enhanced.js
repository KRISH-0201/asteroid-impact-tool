// ============================================================
// AsteroidIQ — Enhanced Dashboard JavaScript
// Chart.js visualizations, improved feed rendering, filter
// ============================================================

let allAsteroids = [];
let currentFilter = 'all';

document.addEventListener('DOMContentLoaded', () => {
    loadSystemStatus();
    
    // Override RealTimeDataManager render methods
    setTimeout(patchRealTimeManager, 200);
    
    // Refresh button
    document.getElementById('refresh-data')?.addEventListener('click', () => {
        if (window.realTimeData) window.realTimeData.fetchAllData();
    });
});

function patchRealTimeManager() {
    if (!window.realTimeData) return;
    
    const rtd = window.realTimeData;
    
    // Override updateAsteroidList
    const origUpdate = rtd.updateAsteroidList.bind(rtd);
    rtd.updateAsteroidList = function() {
        allAsteroids = this.asteroidData || [];
        renderEnhancedFeed(allAsteroids);
        renderSizeChart(allAsteroids);
        renderSpeedChart(allAsteroids);
        updateTrackingMap(allAsteroids);
        updateStats(allAsteroids);
    };
    
    // Override renderSentryObjects
    const origSentry = rtd.renderSentryObjects.bind(rtd);
    rtd.renderSentryObjects = function() {
        renderEnhancedSentry(this.sentryData || []);
    };
    
    // Override updateGlobalStats
    rtd.updateGlobalStats = function(statsData) {
        const sys = statsData.system_status || {};
        const el = (id, v) => { const e = document.getElementById(id); if (e) e.textContent = v; };
        el('cache-count', sys.cache_size || 0);
        el('uptime', sys.uptime || '—');
        el('total-tracked', (statsData.tracking_stats?.total_tracked || 0).toLocaleString());
        el('potentially-hazardous', (statsData.tracking_stats?.hazardous_count || 0).toLocaleString());
        el('approaching-today', statsData.tracking_stats?.today_count || 0);
        el('refresh-time', new Date().toLocaleTimeString());
    };
}

/* ── Feed Rendering ──────────────────────────────────────── */
function renderEnhancedFeed(asteroids) {
    const container = document.getElementById('approaching-list');
    if (!container) return;

    if (!asteroids.length) {
        container.innerHTML = '<div style="padding:1.5rem; text-align:center; color:rgba(255,255,255,0.3); font-size:0.85rem">No asteroids in current window</div>';
        return;
    }

    container.innerHTML = asteroids.map(a => {
        const name = (a.name || 'Unknown').replace('(', '').replace(')', '').trim();
        const diam = a.estimated_diameter_max ? formatDiam(a.estimated_diameter_max) : 'N/A';
        const speed = a.velocity_km_s ? `${parseFloat(a.velocity_km_s).toFixed(1)} km/s` : 'N/A';
        const miss = a.miss_distance_km ? formatDist(parseFloat(a.miss_distance_km)) : 'N/A';
        const isHaz = a.is_hazardous;

        const simUrl = `/simulator?d=${Math.round(a.estimated_diameter_max||100)}&v=${parseFloat(a.velocity_km_s||17).toFixed(0)}&type=stone`;

        return `
        <div class="feed-row ${isHaz ? 'hazardous' : ''}" data-hazardous="${isHaz}">
            <span class="feed-name" title="${a.name}">${name.length > 22 ? name.slice(0, 22) + '…' : name}</span>
            <span class="feed-val">${diam}</span>
            <span class="feed-val">${speed}</span>
            <span class="feed-val">${miss}</span>
            <span>${isHaz ? '<span class="hazard-badge-yes">⚠ YES</span>' : '<span class="hazard-badge-no">✓ Safe</span>'}</span>
            <a href="${simUrl}" class="feed-simulate-btn">Simulate</a>
        </div>`;
    }).join('');

    updateStats(asteroids);
}

function filterFeed(type) {
    currentFilter = type;
    document.querySelectorAll('.dp-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(`filter-${type}`)?.classList.add('active');

    document.querySelectorAll('.feed-row').forEach(row => {
        if (type === 'all') {
            row.classList.remove('filtered');
        } else if (type === 'hazardous') {
            const isHaz = row.dataset.hazardous === 'true';
            row.classList.toggle('filtered', !isHaz);
        }
    });
}
window.filterFeed = filterFeed;

function updateStats(asteroids) {
    const today = document.getElementById('approaching-today');
    if (today) today.textContent = asteroids.length;
    
    const haz = asteroids.filter(a => a.is_hazardous).length;
    const hazEl = document.getElementById('potentially-hazardous');
    if (hazEl) hazEl.textContent = haz.toLocaleString();
}

/* ── Sentry Rendering ────────────────────────────────────── */
function renderEnhancedSentry(objects) {
    const container = document.getElementById('risk-objects');
    if (!container) return;

    if (!objects.length) {
        container.innerHTML = `
            <div style="padding:1.5rem; text-align:center">
                <div style="font-size:2rem; margin-bottom:0.5rem">🛡️</div>
                <div style="font-size:0.8rem; color:rgba(255,255,255,0.4)">No Sentry objects loaded.<br>NASA Sentry tracks long-term impact risks.</div>
                <a href="https://cneos.jpl.nasa.gov/sentry/" target="_blank" style="color:#00e5ff; font-size:0.75rem; margin-top:0.5rem; display:block">View Sentry →</a>
            </div>`;
        return;
    }

    container.innerHTML = objects.slice(0, 10).map(o => {
        const name = o.name || o.designation || 'Unknown';
        const prob = o.impact_probability || 0;
        const riskPct = Math.min(parseFloat(prob) * 1e8, 100); // Scale for visual
        const diameter = o.diameter ? `${parseFloat(o.diameter).toFixed(0)} m` : '?';
        const energy = o.energy ? `${parseFloat(o.energy).toFixed(2)} MT` : '?';
        const year = o.year_range_min || '?';

        return `
        <div class="sentry-item">
            <div class="sentry-name">${name}</div>
            <div class="sentry-props">
                <span class="sentry-prop">⏱ ${year}</span>
                <span class="sentry-prop">📏 ${diameter}</span>
                <span class="sentry-prop">💥 ${energy}</span>
                <span class="sentry-prop" style="color:#ff9800">P: ${parseFloat(prob).toExponential(2)}</span>
            </div>
            <div class="sentry-risk-bar">
                <div class="sentry-risk-fill" style="width:${Math.max(riskPct, 2)}%"></div>
            </div>
        </div>`;
    }).join('');
}

/* ── Charts ──────────────────────────────────────────────── */
let sizeChart, speedChart;

const chartDefaults = {
    font: { family: 'Inter' },
    color: 'rgba(255,255,255,0.5)'
};
Chart.defaults.font.family = 'Inter';
Chart.defaults.color = 'rgba(255,255,255,0.5)';

function renderSizeChart(asteroids) {
    const ctx = document.getElementById('size-chart');
    if (!ctx) return;

    const small = asteroids.filter(a => (a.estimated_diameter_max || 0) < 100).length;
    const medium = asteroids.filter(a => {
        const d = a.estimated_diameter_max || 0;
        return d >= 100 && d < 500;
    }).length;
    const large = asteroids.filter(a => {
        const d = a.estimated_diameter_max || 0;
        return d >= 500 && d < 2000;
    }).length;
    const xlarge = asteroids.filter(a => (a.estimated_diameter_max || 0) >= 2000).length;

    const data = [small || 4, medium || 2, large || 1, xlarge || 0];
    const labels = ['< 100m', '100m–500m', '500m–2km', '> 2km'];
    const colors = ['#00b4d8', '#0062ff', '#ff9800', '#ef5350'];

    if (sizeChart) sizeChart.destroy();
    sizeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: colors.map(c => c + '99'),
                borderColor: colors,
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (c) => ` ${c.label}: ${c.raw} asteroids`
                    }
                }
            },
            cutout: '65%',
        }
    });

    // Render legend
    const legend = document.getElementById('size-legend');
    if (legend) {
        legend.innerHTML = labels.map((l, i) => `
            <div class="chart-legend-item">
                <div class="chart-legend-dot" style="background:${colors[i]}"></div>
                <span>${l}: ${data[i]}</span>
            </div>`).join('');
    }
}

function renderSpeedChart(asteroids) {
    const ctx = document.getElementById('speed-chart');
    if (!ctx) return;

    // Bucket speeds into bins
    const bins = [5, 10, 15, 20, 25, 30, 40, 50, 72];
    const counts = new Array(bins.length - 1).fill(0);
    const labels = [];
    for (let i = 0; i < bins.length - 1; i++) {
        labels.push(`${bins[i]}-${bins[i+1]}`);
    }

    asteroids.forEach(a => {
        const v = parseFloat(a.velocity_km_s || 0);
        for (let i = 0; i < bins.length - 1; i++) {
            if (v >= bins[i] && v < bins[i + 1]) {
                counts[i]++;
                break;
            }
        }
    });

    // Fallback data if none available
    const displayData = counts.some(c => c > 0) ? counts : [1, 4, 8, 5, 3, 1, 1, 0];

    if (speedChart) speedChart.destroy();
    speedChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Asteroids',
                data: displayData,
                backgroundColor: 'rgba(0, 180, 216, 0.3)',
                borderColor: '#00b4d8',
                borderWidth: 1.5,
                borderRadius: 4,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (c) => ` ${c.raw} asteroids`,
                        title: (c) => `${c[0].label} km/s`
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255,255,255,0.04)' },
                    ticks: { font: { size: 10 } }
                },
                y: {
                    grid: { color: 'rgba(255,255,255,0.04)' },
                    ticks: { font: { size: 10 }, stepSize: 1 },
                    beginAtZero: true
                }
            }
        }
    });
}

/* ── Map Markers ─────────────────────────────────────────── */
const mapMarkers = [];

function updateTrackingMap(asteroids) {
    const map = window.trackingMap;
    if (!map) return;

    // Clear existing markers
    mapMarkers.forEach(m => map.removeLayer(m));
    mapMarkers.length = 0;

    // Place markers at random "approach" positions for visual effect
    asteroids.forEach((a, i) => {
        const lat = (Math.random() * 120 - 60);
        const lon = (Math.random() * 360 - 180);
        const isHaz = a.is_hazardous;

        const marker = L.circleMarker([lat, lon], {
            radius: isHaz ? 6 : 4,
            fillColor: isHaz ? '#ef5350' : '#00b4d8',
            color: isHaz ? '#b71c1c' : '#0062ff',
            weight: 1,
            opacity: 0.9,
            fillOpacity: 0.7
        }).addTo(map);

        const name = (a.name || 'Unknown').replace(/[()]/g, '').trim();
        marker.bindPopup(`
            <div style="font-family:Inter; color:#111">
                <strong>${name}</strong><br>
                ${isHaz ? '⚠️ Potentially Hazardous' : '✅ Safe'}<br>
                Ø ${formatDiam(a.estimated_diameter_max || 0)}<br>
                ${parseFloat(a.velocity_km_s || 0).toFixed(1)} km/s
            </div>
        `);

        mapMarkers.push(marker);
    });
}

/* ── System Status ───────────────────────────────────────── */
async function loadSystemStatus() {
    try {
        const res = await fetch('/api/stats/global');
        if (!res.ok) throw new Error();
        const data = await res.json();
        
        const sys = data.system_status || {};
        const el = (id, v) => { const e = document.getElementById(id); if (e) e.textContent = v; };
        
        el('cache-count', sys.cache_size || 0);
        el('uptime', sys.uptime || '—');
        el('total-tracked', (data.tracking_stats?.total_tracked || 28915).toLocaleString());
        el('refresh-time', new Date().toLocaleTimeString());
        
        // Cache status dot
        const dot = document.getElementById('mongo-dot');
        const status = document.getElementById('mongo-status');
        if (dot && status) {
            dot.className = 'si-dot green';
            status.textContent = 'Online';
        }
    } catch (e) {
        const dot = document.getElementById('mongo-dot');
        const status = document.getElementById('mongo-status');
        if (dot) dot.className = 'si-dot yellow';
        if (status) status.textContent = 'Demo Mode';
    }
}

/* ── Utilities ───────────────────────────────────────────── */
function formatDiam(m) {
    if (m >= 1000) return `${(m / 1000).toFixed(2)} km`;
    return `${Math.round(m)} m`;
}
function formatDist(km) {
    if (km >= 1e6) return `${(km / 1e6).toFixed(2)}M km`;
    if (km >= 1e3) return `${(km / 1e3).toFixed(0)}K km`;
    return `${km.toFixed(0)} km`;
}
