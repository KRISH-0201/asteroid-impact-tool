// ============================================================
// AsteroidIQ — Simulator UI Controller
// Handles: presets, quick preview, AI chat, keyboard shortcuts,
//          history, toasts, and wires into AsteroidSimulator
// ============================================================

/* ── Historical Presets ─────────────────────────────────── */
const PRESETS = {
    chelyabinsk: {
        asteroid_type: 'stone', diameter: 20, speed: 18, angle: 18,
        latitude: 55.15, longitude: 61.40,
        label: 'Chelyabinsk 2013',
        note: '20m stony asteroid, airburst at ~30km altitude. Real event!'
    },
    tunguska: {
        asteroid_type: 'stone', diameter: 60, speed: 27, angle: 30,
        latitude: 60.89, longitude: 101.89,
        label: 'Tunguska 1908',
        note: '60m asteroid, 15 MT airburst, flattened 2,000 km² of Siberian forest.'
    },
    barringer: {
        asteroid_type: 'iron', diameter: 50, speed: 15, angle: 45,
        latitude: 35.0270, longitude: -111.0228,
        label: 'Barringer Crater (50,000 BC)',
        note: '50m iron asteroid that created the famous Arizona crater (1.2km wide).'
    },
    chicxulub: {
        asteroid_type: 'stone', diameter: 10000, speed: 20, angle: 60,
        latitude: 21.40, longitude: -89.52,
        label: 'Chicxulub (66 MYA)',
        note: 'The dinosaur-killer. 10km asteroid, extinction-level event, 100M MT.'
    },
    city_killer: {
        asteroid_type: 'stone', diameter: 500, speed: 17, angle: 45,
        latitude: 40.7128, longitude: -74.0060,
        label: 'City Killer (500m)',
        note: '500m city-killer class asteroid. Would obliterate a major metropolis.'
    },
    ocean_impact: {
        asteroid_type: 'stone', diameter: 300, speed: 17, angle: 45,
        latitude: 30.0, longitude: -40.0,
        label: 'Mid-Atlantic Ocean Impact',
        note: 'Ocean impact generates massive tsunamis. Coastal cities at severe risk.'
    }
};

/* ── Preset Handling ────────────────────────────────────── */
document.querySelectorAll('.preset-chip').forEach(btn => {
    btn.addEventListener('click', () => {
        const key = btn.dataset.preset;
        const preset = PRESETS[key];
        if (!preset) return;

        // Mark active
        document.querySelectorAll('.preset-chip').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Apply values
        applyPreset(preset);

        // Show toast
        showToast(`✅ Preset loaded: ${preset.label}`, 'success');

        // Inform AI
        addAIMessage(`🎯 Loaded preset: <strong>${preset.label}</strong>. ${preset.note}`);
    });
});

function applyPreset(preset) {
    const sim = window.asteroidSimulator;
    if (!sim) return;

    // Set sliders
    setSlider('diameter-slider', 'diameter', 'diameter-value', preset.diameter, 'm');
    setSlider('speed-slider', 'speed', 'speed-value', preset.speed, ' km/s');
    setSlider('angle-slider', 'angle', 'angle-value', preset.angle, '°');

    // Set asteroid type
    document.querySelectorAll('.asteroid-card').forEach(c => c.classList.remove('active'));
    const card = document.querySelector(`.asteroid-card[data-type="${preset.asteroid_type}"]`);
    if (card) card.classList.add('active');

    // Update sim params
    sim.params.asteroid_type = preset.asteroid_type;
    sim.params.diameter = preset.diameter;
    sim.params.speed = preset.speed;
    sim.params.angle = preset.angle;

    // Move map
    if (sim.map) {
        sim.params.latitude = preset.latitude;
        sim.params.longitude = preset.longitude;
        const latlng = { lat: preset.latitude, lng: preset.longitude };
        sim.updateMarker(latlng);
        sim.updateCoordinatesDisplay(latlng);
        sim.map.setView([preset.latitude, preset.longitude], 5);
    }

    updateQuickPreview();
}

function setSlider(sliderId, paramKey, displayId, value, unit) {
    const slider = document.getElementById(sliderId);
    const display = document.getElementById(displayId);
    if (slider) {
        slider.value = value;
        slider.dispatchEvent(new Event('input'));
    }
    if (display) {
        display.textContent = value + unit;
    }
}

/* ── Quick Preview Live Update ──────────────────────────── */
function updateQuickPreview() {
    const sim = window.asteroidSimulator;
    if (!sim) return;

    const d = sim.params.diameter;
    const v = sim.params.speed;
    const densities = { iron: 7800, stone: 3000, carbon: 2000, comet: 500 };
    const density = densities[sim.params.asteroid_type] || 3000;

    const r = d / 2;
    const vol = (4 / 3) * Math.PI * Math.pow(r, 3);
    const mass = vol * density;
    const ke = 0.5 * mass * Math.pow(v * 1000, 2);
    const energyMT = ke / 4.184e15;

    const eEl = document.getElementById('qp-energy');
    const mEl = document.getElementById('qp-mass');
    const cEl = document.getElementById('qp-category');

    if (eEl) eEl.textContent = formatEnergy(energyMT);
    if (mEl) mEl.textContent = formatMass(mass);
    if (cEl) cEl.textContent = getCategory(d);
}

function formatEnergy(mt) {
    if (mt >= 1e6) return `${(mt / 1e6).toFixed(2)} TT`;
    if (mt >= 1000) return `${(mt / 1000).toFixed(2)} GT`;
    if (mt >= 1) return `${mt.toFixed(2)} MT`;
    if (mt >= 0.001) return `${(mt * 1000).toFixed(1)} KT`;
    return `${(mt * 1e6).toFixed(0)} T`;
}
function formatMass(kg) {
    if (kg >= 1e15) return `${(kg / 1e15).toFixed(2)} Pt`;
    if (kg >= 1e12) return `${(kg / 1e12).toFixed(2)} Gt`;
    if (kg >= 1e9) return `${(kg / 1e9).toFixed(2)} Mt`;
    if (kg >= 1e6) return `${(kg / 1e6).toFixed(2)} kt`;
    if (kg >= 1e3) return `${(kg / 1e3).toFixed(2)} t`;
    return `${kg.toFixed(0)} kg`;
}
function getCategory(d) {
    if (d < 25) return 'Micro';
    if (d < 100) return 'Small';
    if (d < 300) return 'City';
    if (d < 1000) return 'Regional';
    if (d < 3000) return 'Continental';
    return 'Extinction';
}

// Hook into slider events for live preview
['diameter-slider', 'speed-slider', 'angle-slider'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', updateQuickPreview);
});
document.querySelectorAll('.asteroid-card').forEach(c => {
    c.addEventListener('click', updateQuickPreview);
});
setTimeout(updateQuickPreview, 500);

/* ── Diameter Scale Reference ───────────────────────────── */
const DIAMETER_REFS = [
    [10, '🏢 As wide as a large building'],
    [25, '🏟️ Smaller than a sports stadium'],
    [50, '🏙️ Half a city block wide'],
    [100, '📐 Width of a city block (Empire State Building height)'],
    [200, '🌉 Length of two Golden Gate bridges'],
    [500, '🏙️ City-destroyer class — 5 km crater'],
    [1000, '⚠️ Regional devastation — 1 km+ body'],
    [2000, '💀 Extinction-level threat candidate'],
];

document.getElementById('diameter-slider')?.addEventListener('input', (e) => {
    const d = parseInt(e.target.value);
    const ref = document.getElementById('diameter-reference');
    if (!ref) return;
    let text = '🪨 Custom size asteroid';
    for (const [size, label] of DIAMETER_REFS) {
        if (d >= size) text = label;
    }
    ref.textContent = text;
});

/* ── AI Chat Panel ──────────────────────────────────────── */
let lastSimulationData = null;

function addAIMessage(html, isUser = false) {
    const container = document.getElementById('ai-messages');
    if (!container) return;

    const msg = document.createElement('div');
    msg.className = `ai-msg ${isUser ? 'user' : 'ai'}`;
    msg.innerHTML = `<p>${html}</p>`;
    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;
}

function addTypingIndicator() {
    const container = document.getElementById('ai-messages');
    if (!container) return;
    const msg = document.createElement('div');
    msg.className = 'ai-msg ai typing';
    msg.id = 'ai-typing';
    msg.innerHTML = '<p>ARIA is thinking</p>';
    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;
    return msg;
}

function removeTypingIndicator() {
    document.getElementById('ai-typing')?.remove();
}

async function sendAIMessage() {
    const input = document.getElementById('ai-input');
    if (!input) return;
    const text = input.value.trim();
    if (!text) return;

    addAIMessage(text, true);
    input.value = '';

    addTypingIndicator();

    try {
        const res = await fetch('/api/ai/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: text,
                simulation_data: lastSimulationData || (window.asteroidSimulator ? { parameters: window.asteroidSimulator.params } : {})
            })
        });
        removeTypingIndicator();
        if (res.ok) {
            const data = await res.json();
            if (data.response) {
                addAIMessage(data.response);
                return;
            }
        }
    } catch (err) {
        console.warn('AI API call failed, falling back to local NLP:', err);
    }

    removeTypingIndicator();
    const response = generateAIResponse(text, lastSimulationData);
    addAIMessage(response);
}

function generateAIResponse(question, simData) {
    const q = question.toLowerCase().trim();

    // 1. Greetings & Identity
    if (['hi', 'hello', 'hey', 'greetings', 'who are you', 'help', 'what can you do'].some(w => q.startsWith(w) || q === w)) {
        return `Hello! I am <strong>ARIA</strong> (Asteroid Risk Intelligence Assistant), your planetary defense and impact physics advisor.<br><br>
        Ask me about:<br>
        • <strong>Simulation Results</strong>: Impact energy, crater size, fatalities, or blast waves.<br>
        • <strong>Planetary Defense</strong>: NASA's DART mission, kinetic deflection, or gravity tractors.<br>
        • <strong>Known Asteroids</strong>: Apophis (2029 pass), Bennu, Tunguska, or Chicxulub dinosaur killer.<br>
        • <strong>Physics</strong>: Airbursts vs ground craters, tsunamis, or thermal radiation.`;
    }

    // 2. Active Simulation Metrics
    if (simData) {
        const energy = simData.impact_basic?.energy_megatons || 0;
        const crater = simData.crater?.diameter_km || 0;
        const deaths = (simData.crater?.people_killed || 0) + (simData.fireball?.deaths || 0) + (simData.shockwave?.deaths || 0) + (simData.winds?.deaths || 0);
        const blast = simData.shockwave?.max_range_km || 0;
        const fireball = simData.fireball?.radius_km || 0;

        if (q.includes('energy') || q.includes('powerful') || q.includes('how big') || q.includes('megaton') || q.includes('hiroshima')) {
            return `The simulated impact released <strong>${formatEnergy(energy)}</strong> of kinetic energy — equivalent to approximately <strong>${Math.round(energy / 0.015).toLocaleString()} Hiroshima bombs</strong>. ${energy > 100 ? "This is a catastrophic regional to global destruction event." : energy > 1 ? "Massive regional destruction guaranteed." : "A powerful localized impact event."}`;
        }
        if (q.includes('crater') || q.includes('hole') || q.includes('depth') || q.includes('size')) {
            if (crater <= 0) return "This asteroid detonated as an <strong>atmospheric airburst</strong> before reaching the ground; no surface crater was excavated.";
            return `The impact would excavate a crater approximately <strong>${crater.toFixed(2)} km wide</strong> and about <strong>${(crater * 0.15).toFixed(2)} km deep</strong>. For comparison, Arizona's Barringer Crater is 1.2 km wide.`;
        }
        if (q.includes('death') || q.includes('kill') || q.includes('casualti') || q.includes('people') || q.includes('fatalit') || q.includes('survive')) {
            return `Estimated casualty toll: <strong>${deaths.toLocaleString()} fatalities</strong>. This combines ground-zero crater vaporization, thermal fireball radiation burns, blast overpressure building collapses, and hurricane-force winds.`;
        }
        if (q.includes('fireball') || q.includes('thermal') || q.includes('burn') || q.includes('radiation')) {
            return `The thermal fireball extends to a lethal radius of <strong>${fireball.toFixed(2)} km</strong>, causing immediate combustible ignition and severe third-degree burns within seconds.`;
        }
        if (q.includes('blast') || q.includes('shockwave') || q.includes('wind') || q.includes('pressure')) {
            return `The shockwave blast wave extends to a lethal radius of <strong>${blast.toFixed(2)} km</strong>, shattering reinforced concrete structures within the inner zone.`;
        }
        if (q.includes('defend') || q.includes('mitigat') || q.includes('stop') || q.includes('prevent') || q.includes('deflect')) {
            const sim = window.asteroidSimulator;
            const d = sim?.params?.diameter || 100;
            if (d < 150) return `For this <strong>${d}m</strong> asteroid, a <strong>Kinetic Impactor</strong> (like NASA's DART mission) launched 5–10 years early is 100% effective! Even a 1 cm/s trajectory change causes a full Earth miss over time.`;
            if (d < 500) return `A <strong>${d}m</strong> asteroid is in the City Killer class. A single kinetic impactor is insufficient; multiple coordinated impactors or a <strong>standoff nuclear explosion</strong> are required.`;
            return `A <strong>${d}m+</strong> asteroid is in the continental to extinction class. Decades of warning time and international space agency coordination would be required. Immediate civil evacuation is the primary short-term response.`;
        }
        if (q.includes('tsunami') || q.includes('ocean') || q.includes('sea') || q.includes('water')) {
            return `An ocean impact generates towering water cavity waves hundreds of meters high that propagate across ocean basins, causing catastrophic coastal flooding thousands of kilometers away.`;
        }
    }

    // 3. Known Asteroids & History
    if (q.includes('tunguska')) return `The <strong>1908 Tunguska Event</strong> was a 15 MT asteroid airburst over Siberia that flattened 2,150 km² of forest with no ground crater because it exploded at 8–10 km altitude.`;
    if (q.includes('apophis') || q.includes('2029')) return `<strong>Apophis (99942)</strong> is a ~370m asteroid making a historically close flyby on April 13, 2029, passing within 31,600 km of Earth (closer than geostationary satellites). Impact risk in 2029 is 0%.`;
    if (q.includes('bennu')) return `<strong>Bennu (101955)</strong> is a ~500m asteroid visited by NASA's OSIRIS-REx sample return mission. It currently has the highest cumulative impact probability on NASA's Sentry Table for the late 22nd century (~1 in 1,750).`;
    if (q.includes('dart') || q.includes('dimorphos')) return `NASA's <strong>DART</strong> mission successfully redirected the asteroid Dimorphos in September 2022 by crashing into it at 6.1 km/s, shortening its orbital period by 33 minutes!`;
    if (q.includes('chelyabinsk')) return `The <strong>2013 Chelyabinsk Superbolide</strong> was a ~20m asteroid that exploded over Russia at 30 km altitude with ~500 KT energy, injuring 1,500 people primarily from broken window glass.`;
    if (q.includes('chicxulub') || q.includes('dinosaur') || q.includes('extinction')) return `The <strong>Chicxulub Impactor</strong> (66 million years ago) was ~10–14 km wide, releasing ~100 million MT. It triggered global firestorms, an impact winter, and the Cretaceous-Paleogene extinction wiping out 75% of species including non-avian dinosaurs.`;
    if (q.includes('barringer') || q.includes('arizona')) return `<strong>Barringer Crater</strong> in Arizona was created 50,000 years ago by a 50-meter metallic iron asteroid, excavating a 1.2 km wide, 170m deep crater.`;
    if (q.includes('nasa') || q.includes('sentry') || q.includes('track') || q.includes('detect')) return `NASA's CNEOS and the automated Sentry System continuously monitor near-Earth objects using ground telescopes (ATLAS, Pan-STARRS, Catalina) and planetary radar. Over 34,000 NEOs are currently tracked.`;

    // 4. Default
    return `Regarding <em>"${question}"</em>: Impact physics is governed by <strong>diameter</strong> (mass scales cubically), <strong>density</strong> (iron, stone, or cometary ice), and <strong>velocity</strong> (kinetic energy scales quadratically with $v^2$). Try running a simulation to see the exact blast zones and planetary defense options!`;
}

// Wire up AI input
document.getElementById('ai-send')?.addEventListener('click', sendAIMessage);
document.getElementById('ai-input')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendAIMessage();
});

// Called by asteroid_simulator.js after results are loaded
window.onSimulationComplete = function(data) {
    lastSimulationData = data;
    
    const energy = data.impact_basic?.energy_megatons || 0;
    const crater = data.crater?.diameter_km || 0;
    const deaths = (data.crater?.people_killed || 0) + (data.fireball?.deaths || 0) + (data.shockwave?.deaths || 0) + (data.winds?.deaths || 0);
    const riskPct = data.risk_assessment?.threat_level_pct || 0;
    
    addAIMessage(`
        🔴 <strong>Impact Analysis Complete!</strong><br>
        Energy: <strong>${formatEnergy(energy)}</strong> · 
        Crater: <strong>${crater.toFixed(1)} km</strong> · 
        Estimated fatalities: <strong>${deaths.toLocaleString()}</strong><br>
        AI Threat Score: <strong>${riskPct.toFixed(0)}%</strong> · 
        ${data.mitigation_outcome || 'No defense deployed.'}<br>
        <small style="color:rgba(255,255,255,0.4)">Ask me anything about these results →</small>
    `);
    
    // Show results panel
    const rp = document.getElementById('results-panel');
    if (rp) rp.style.display = 'flex';
    
    // Show zone legend
    const zl = document.getElementById('zone-legend');
    if (zl) zl.style.display = 'flex';
    
    // Render rich results
    renderResults(data);
};

/* ── Rich Results Renderer ──────────────────────────────── */
function renderResults(data) {
    const container = document.getElementById('results-content');
    if (!container) return;

    const energy = data.impact_basic?.energy_megatons || 0;
    const craterD = data.crater?.diameter_km || 0;
    const fireballR = data.fireball?.radius_km || 0;
    const blastMax = data.shockwave?.max_range_km || 0;
    const windSpeed = data.winds?.max_speed_kmh || 0;
    const magnitude = data.earthquake?.magnitude || 0;
    const deaths = (data.crater?.people_killed || 0) + (data.fireball?.deaths || 0) + (data.shockwave?.deaths || 0) + (data.winds?.deaths || 0) + (data.earthquake?.deaths || 0);
    const hiroshima = energy / 0.015;
    const riskPct = data.risk_assessment?.threat_level_pct || 0;

    const econ = data.economic_impact || {};
    const totalEcon = econ.total_economic_impact_usd || 0;
    const recoveryYrs = econ.summary?.recovery_timeline_years?.toFixed(1) || '?';
    const econClass = econ.summary?.impact_classification || '';
    const pctGDP = econ.summary?.percent_global_gdp?.toFixed(4) || '0';

    const atmo = data.atmospheric_entry || {};
    const survived = atmo.survived !== undefined ? (atmo.survived ? '🌍 Ground Impact' : '💨 Airburst') : '—';
    const maxTemp = atmo.max_temperature ? `${Math.round(atmo.max_temperature / 1000).toFixed(1)}K K` : '—';

    const mitigations = data.mitigation_options || [];
    const comparisons = data.real_world_comparison || [];
    const riskDetails = data.risk_assessment?.probabilistic_outcomes || {};

    // Threat bar color
    const threatColor = riskPct > 80 ? '#ef5350' : riskPct > 50 ? '#ff9800' : '#69f0ae';

    container.innerHTML = `
        <!-- Threat Score -->
        <div class="result-threat-bar">
            <div class="threat-label-row">
                <span>AI Threat Score</span>
                <strong style="color:${threatColor}">${riskPct.toFixed(1)}%</strong>
            </div>
            <div class="threat-bar-bg">
                <div class="threat-bar-fill" style="width:${Math.min(riskPct, 100)}%;background:${threatColor}"></div>
            </div>
            <div style="font-size:0.7rem;color:rgba(255,255,255,0.4);margin-top:0.375rem">${data.risk_assessment?.details || ''}</div>
        </div>

        <!-- Impact Outcome -->
        ${data.mitigation_outcome && data.mitigation_outcome !== 'No mitigation deployed. Direct impact pending.' ? `
        <div class="comparison-box" style="border-color:rgba(0,200,255,0.25);background:rgba(0,200,255,0.05)">
            🛡️ ${data.mitigation_outcome}
        </div>` : ''}

        <!-- KPI Grid -->
        <div class="result-kpi-grid">
            <div class="kpi-card highlight">
                <div class="kpi-label">⚡ Impact Energy</div>
                <div class="kpi-value">${formatEnergy(energy)}</div>
                <div class="kpi-sub">${Math.round(hiroshima).toLocaleString()} × Hiroshima</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">🕳️ Crater Diameter</div>
                <div class="kpi-value ${craterD > 50 ? 'danger' : ''}">${craterD.toFixed(1)} km</div>
                <div class="kpi-sub">Depth: ${(craterD * 0.1).toFixed(1)} km</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">💀 Fatalities</div>
                <div class="kpi-value ${deaths > 1e6 ? 'danger' : deaths > 1000 ? 'warning' : ''}">${formatDeaths(deaths)}</div>
                <div class="kpi-sub">All effects combined</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">🌍 Entry Mode</div>
                <div class="kpi-value" style="font-size:0.85rem">${survived}</div>
                <div class="kpi-sub">Peak: ${maxTemp}</div>
            </div>
        </div>

        <!-- Damage Breakdown -->
        <div class="result-section-title"><i class="fas fa-radiation"></i> Damage Zones</div>
        <div class="damage-rows">
            <div class="damage-row">
                <span class="dr-label">🔥 Fireball Radius</span>
                <span class="dr-value">${fireballR.toFixed(1)} km</span>
            </div>
            <div class="damage-row">
                <span class="dr-label">💥 Blast Range</span>
                <span class="dr-value">${blastMax.toFixed(1)} km</span>
            </div>
            <div class="damage-row">
                <span class="dr-label">💨 Max Wind Speed</span>
                <span class="dr-value">${windSpeed.toFixed(0)} km/h</span>
            </div>
            <div class="damage-row">
                <span class="dr-label">🌍 Earthquake</span>
                <span class="dr-value">M${magnitude.toFixed(1)}</span>
            </div>
            ${Object.entries(data.shockwave?.damage_zones || {}).map(([k, v]) => `
            <div class="damage-row">
                <span class="dr-label">📐 ${k.charAt(0).toUpperCase() + k.slice(1)} Damage</span>
                <span class="dr-value">${parseFloat(v).toFixed(1)} km radius</span>
            </div>`).join('')}
        </div>

        ${totalEcon > 0 ? `
        <!-- Economic Impact -->
        <div class="result-section-title"><i class="fas fa-dollar-sign"></i> Economic Impact ${econClass ? `— <span style="color:#ff9800">${econClass}</span>` : ''}</div>
        <div class="result-kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Total Damage</div>
                <div class="kpi-value" style="font-size:0.9rem">${formatCurrency(totalEcon)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">% World GDP</div>
                <div class="kpi-value">${pctGDP}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Recovery Time</div>
                <div class="kpi-value">${recoveryYrs} yrs</div>
            </div>
        </div>` : ''}

        ${comparisons.length ? `
        <!-- Historical Comparison -->
        <div class="result-section-title"><i class="fas fa-balance-scale"></i> Comparison</div>
        ${comparisons.map(c => `<div class="comparison-box">${c}</div>`).join('')}` : ''}

        ${mitigations.length ? `
        <!-- Defense Options -->
        <div class="result-section-title"><i class="fas fa-shield-alt"></i> Defense Options</div>
        <div class="mitigation-chips">
            ${mitigations.map(m => `
            <div class="mit-chip">
                <div>
                    <div class="mit-name">🛡️ ${m.strategy}</div>
                    <div class="mit-desc">${m.description}</div>
                </div>
                <span class="mit-badge ${m.feasibility || m.effectiveness}">${m.feasibility || m.effectiveness}</span>
            </div>`).join('')}
        </div>` : ''}

        ${Object.keys(riskDetails).length ? `
        <!-- Probabilistic Outcomes -->
        <div class="result-section-title"><i class="fas fa-percentage"></i> Outcome Probabilities</div>
        <div class="damage-rows">
            ${Object.entries(riskDetails).map(([k, v]) => `
            <div class="damage-row">
                <span class="dr-label">${k}</span>
                <span class="dr-value">${parseFloat(v).toFixed(1)}%</span>
            </div>`).join('')}
        </div>` : ''}
    `;
}

function formatDeaths(n) {
    if (n >= 1e9) return `${(n / 1e9).toFixed(1)}B`;
    if (n >= 1e6) return `${(n / 1e6).toFixed(1)}M`;
    if (n >= 1e3) return `${(n / 1e3).toFixed(0)}K`;
    return n.toLocaleString();
}
function formatCurrency(n) {
    if (n >= 1e15) return `$${(n / 1e15).toFixed(2)} Quadrillion`;
    if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
    if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
    if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
    return `$${n.toLocaleString()}`;
}

/* ── Close / Action Buttons ─────────────────────────────── */
document.getElementById('btn-close-results')?.addEventListener('click', () => {
    document.getElementById('results-panel').style.display = 'none';
    const zl = document.getElementById('zone-legend');
    if (zl) zl.style.display = 'none';
});

document.getElementById('btn-share')?.addEventListener('click', () => {
    const sim = window.asteroidSimulator;
    if (!sim) return;
    const url = new URL(window.location.href);
    url.searchParams.set('type', sim.params.asteroid_type);
    url.searchParams.set('d', sim.params.diameter);
    url.searchParams.set('v', sim.params.speed);
    url.searchParams.set('a', sim.params.angle);
    url.searchParams.set('lat', sim.params.latitude.toFixed(4));
    url.searchParams.set('lon', sim.params.longitude.toFixed(4));
    navigator.clipboard.writeText(url.toString())
        .then(() => showToast('📋 Simulation URL copied!', 'success'))
        .catch(() => showToast('Could not copy URL', 'error'));
});

// ── Export Mission Report ──────────────────────────────────
document.getElementById('btn-export')?.addEventListener('click', () => {
    if (!lastSimulationData) {
        showToast('Run a simulation first to export the report!', 'info');
        return;
    }
    const blob = new Blob([JSON.stringify(lastSimulationData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `AsteroidIQ_Mission_Report_${lastSimulationData.simulation_id || Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('📄 Mission Report exported successfully!', 'success');
});

// ── Scenario Comparison Modal ──────────────────────────────
const compareModal = document.getElementById('compare-modal');
const closeCompareBtn = document.getElementById('close-compare-modal');
const selectA = document.getElementById('preset-select-a');
const selectB = document.getElementById('preset-select-b');
const runCompareBtn = document.getElementById('run-comparison-btn');

document.getElementById('btn-compare')?.addEventListener('click', () => {
    if (compareModal) {
        compareModal.style.display = 'flex';
        updateScenarioPreviews();
    }
});

closeCompareBtn?.addEventListener('click', () => {
    if (compareModal) compareModal.style.display = 'none';
});

compareModal?.addEventListener('click', (e) => {
    if (e.target === compareModal) compareModal.style.display = 'none';
});

function getScenarioParams(key) {
    if (key === 'current') {
        const sim = window.asteroidSimulator;
        return {
            asteroid_type: sim ? sim.params.asteroid_type : 'stone',
            diameter: sim ? sim.params.diameter : 100,
            speed: sim ? sim.params.speed : 17,
            angle: sim ? sim.params.angle : 45,
            latitude: sim ? sim.params.latitude : 40.7128,
            longitude: sim ? sim.params.longitude : -74.0060
        };
    }
    const p = PRESETS[key] || PRESETS.tunguska;
    return {
        asteroid_type: p.asteroid_type,
        diameter: p.diameter,
        speed: p.speed,
        angle: p.angle,
        latitude: p.latitude,
        longitude: p.longitude
    };
}

function updateScenarioPreviews() {
    const keyA = selectA ? selectA.value : 'current';
    const keyB = selectB ? selectB.value : 'tunguska';
    const paramsA = getScenarioParams(keyA);
    const paramsB = getScenarioParams(keyB);

    const prevA = document.getElementById('preview-scenario-a');
    const prevB = document.getElementById('preview-scenario-b');

    if (prevA) {
        prevA.innerHTML = `
            <div class="sc-param-item"><span>Composition:</span> <span class="sc-param-val" style="text-transform:capitalize">${paramsA.asteroid_type}</span></div>
            <div class="sc-param-item"><span>Diameter:</span> <span class="sc-param-val">${paramsA.diameter} m</span></div>
            <div class="sc-param-item"><span>Velocity:</span> <span class="sc-param-val">${paramsA.speed} km/s</span></div>
            <div class="sc-param-item"><span>Angle:</span> <span class="sc-param-val">${paramsA.angle}°</span></div>
        `;
    }
    if (prevB) {
        prevB.innerHTML = `
            <div class="sc-param-item"><span>Composition:</span> <span class="sc-param-val" style="text-transform:capitalize">${paramsB.asteroid_type}</span></div>
            <div class="sc-param-item"><span>Diameter:</span> <span class="sc-param-val">${paramsB.diameter} m</span></div>
            <div class="sc-param-item"><span>Velocity:</span> <span class="sc-param-val">${paramsB.speed} km/s</span></div>
            <div class="sc-param-item"><span>Angle:</span> <span class="sc-param-val">${paramsB.angle}°</span></div>
        `;
    }
}

selectA?.addEventListener('change', updateScenarioPreviews);
selectB?.addEventListener('change', updateScenarioPreviews);

runCompareBtn?.addEventListener('click', async () => {
    const keyA = selectA ? selectA.value : 'current';
    const keyB = selectB ? selectB.value : 'tunguska';
    const paramsA = getScenarioParams(keyA);
    const paramsB = getScenarioParams(keyB);

    runCompareBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running Differential Physics...';
    runCompareBtn.disabled = true;

    try {
        const res = await fetch('/api/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario_a: paramsA, scenario_b: paramsB })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        renderComparisonResults(data);
    } catch (err) {
        showToast(`Comparison error: ${err.message}`, 'error');
    } finally {
        runCompareBtn.innerHTML = '<i class="fas fa-play"></i> Compute Side-by-Side Analysis';
        runCompareBtn.disabled = false;
    }
});

function renderComparisonResults(data) {
    const area = document.getElementById('compare-results-area');
    const grid = document.getElementById('comparison-grid');
    if (!area || !grid) return;

    const sumA = data.scenario_a?.summary || {};
    const sumB = data.scenario_b?.summary || {};

    const metrics = [
        {
            label: 'Kinetic Impact Energy',
            valA: `${sumA.energy_megatons?.toLocaleString(undefined, {maximumFractionDigits:1})} MT`,
            valB: `${sumB.energy_megatons?.toLocaleString(undefined, {maximumFractionDigits:1})} MT`,
            rawA: sumA.energy_megatons || 0,
            rawB: sumB.energy_megatons || 0
        },
        {
            label: 'Crater Diameter',
            valA: `${sumA.crater_diameter_km?.toFixed(2)} km`,
            valB: `${sumB.crater_diameter_km?.toFixed(2)} km`,
            rawA: sumA.crater_diameter_km || 0,
            rawB: sumB.crater_diameter_km || 0
        },
        {
            label: 'Fireball Radiation Radius',
            valA: `${sumA.fireball_radius_km?.toFixed(2)} km`,
            valB: `${sumB.fireball_radius_km?.toFixed(2)} km`,
            rawA: sumA.fireball_radius_km || 0,
            rawB: sumB.fireball_radius_km || 0
        },
        {
            label: 'Estimated Casualties',
            valA: `${sumA.total_deaths?.toLocaleString()}`,
            valB: `${sumB.total_deaths?.toLocaleString()}`,
            rawA: sumA.total_deaths || 0,
            rawB: sumB.total_deaths || 0
        },
        {
            label: 'Economic Damage',
            valA: formatCurrency(sumA.economic_impact_usd || 0),
            valB: formatCurrency(sumB.economic_impact_usd || 0),
            rawA: sumA.economic_impact_usd || 0,
            rawB: sumB.economic_impact_usd || 0
        },
        {
            label: 'Atmospheric Mode',
            valA: sumA.entry_mode === 'airburst' ? '💥 Airburst' : '🎯 Ground Impact',
            valB: sumB.entry_mode === 'airburst' ? '💥 Airburst' : '🎯 Ground Impact',
            rawA: sumA.entry_mode === 'airburst' ? 1 : 2,
            rawB: sumB.entry_mode === 'airburst' ? 1 : 2
        }
    ];

    let html = '';
    metrics.forEach(m => {
        const total = m.rawA + m.rawB;
        const pctA = total > 0 ? Math.min(Math.max((m.rawA / total) * 100, 5), 95) : 50;
        const pctB = 100 - pctA;
        
        let ratio = '';
        if (m.rawA > 0 && m.rawB > 0 && typeof m.rawA === 'number') {
            if (m.rawA > m.rawB) {
                ratio = `<span class="diff-multiplier-pill" style="color:#00e5ff">${(m.rawA / m.rawB).toFixed(1)}x Higher (A)</span>`;
            } else if (m.rawB > m.rawA) {
                ratio = `<span class="diff-multiplier-pill" style="color:#ff9800">${(m.rawB / m.rawA).toFixed(1)}x Higher (B)</span>`;
            } else {
                ratio = `<span class="diff-multiplier-pill">Equal</span>`;
            }
        }

        html += `
            <div class="diff-metric-card">
                <div class="diff-metric-header">
                    <span>${m.label}</span>
                    ${ratio}
                </div>
                <div class="diff-values-row">
                    <div class="diff-val-a">${m.valA}</div>
                    <div style="font-size:0.75rem; color:rgba(255,255,255,0.4)">VS</div>
                    <div class="diff-val-b">${m.valB}</div>
                </div>
                <div class="diff-bar-comparison">
                    <div class="diff-bar-a" style="width:${pctA}%"></div>
                    <div class="diff-bar-b" style="width:${pctB}%"></div>
                </div>
            </div>
        `;
    });

    grid.innerHTML = html;
    area.style.display = 'block';
}

/* ── URL Param Loading ──────────────────────────────────── */
window.addEventListener('load', () => {
    const params = new URLSearchParams(window.location.search);
    
    if (params.has('preset')) {
        const key = params.get('preset');
        const chip = document.querySelector(`.preset-chip[data-preset="${key}"]`);
        if (chip) chip.click();
        return;
    }
    
    const sim = window.asteroidSimulator;
    if (!sim) return;
    
    if (params.has('d')) setSlider('diameter-slider', 'diameter', 'diameter-value', parseFloat(params.get('d')), 'm');
    if (params.has('v')) setSlider('speed-slider', 'speed', 'speed-value', parseFloat(params.get('v')), ' km/s');
    if (params.has('a')) setSlider('angle-slider', 'angle', 'angle-value', parseFloat(params.get('a')), '°');
    if (params.has('type')) {
        const card = document.querySelector(`.asteroid-card[data-type="${params.get('type')}"]`);
        if (card) card.click();
    }
    if (params.has('lat') && params.has('lon')) {
        const lat = parseFloat(params.get('lat'));
        const lon = parseFloat(params.get('lon'));
        setTimeout(() => {
            if (sim.map) {
                sim.params.latitude = lat;
                sim.params.longitude = lon;
                sim.updateMarker({ lat, lng: lon });
                sim.updateCoordinatesDisplay({ lat, lng: lon });
                sim.map.setView([lat, lon], 5);
            }
        }, 800);
    }
    
    updateQuickPreview();
});

/* ── Keyboard Shortcuts ─────────────────────────────────── */
document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
    if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        document.getElementById('launch-button')?.click();
    }
    if (e.key === 'Escape') {
        document.getElementById('results-panel').style.display = 'none';
    }
});

/* ── Toast System ───────────────────────────────────────── */
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
}

/* ── Patch asteroid_simulator.js to call our callback ───── */
const origDisplayResults = AsteroidSimulator.prototype.displayResults;
AsteroidSimulator.prototype.displayResults = function(data) {
    if (typeof window.onSimulationComplete === 'function') {
        window.onSimulationComplete(data);
    }
    // Note: we handle results display ourselves in renderResults()
};

// Also patch loading states
const origShowLoading = AsteroidSimulator.prototype.showLoading;
AsteroidSimulator.prototype.showLoading = function() {
    const overlay = document.getElementById('simulation-loading');
    if (overlay) overlay.classList.add('active');
    const ps = document.getElementById('panel-status');
    if (ps) { ps.innerHTML = '<div class="status-dot"></div><span>Simulating...</span>'; ps.className = 'panel-status simulating'; }
    const fill = document.getElementById('progress-fill');
    if (fill) fill.style.width = '0%';
    // Hide previous results
    document.getElementById('results-panel').style.display = 'none';
};

const origHideLoading = AsteroidSimulator.prototype.hideLoading;
AsteroidSimulator.prototype.hideLoading = function() {
    const overlay = document.getElementById('simulation-loading');
    if (overlay) overlay.classList.remove('active');
    if (this._progressInterval) clearInterval(this._progressInterval);
    const ps = document.getElementById('panel-status');
    if (ps) { ps.innerHTML = '<div class="status-dot"></div><span>Ready</span>'; ps.className = 'panel-status'; }
};

// Patch animateProgress to use our step dots
const origAnimateProgress = AsteroidSimulator.prototype.animateProgress;
AsteroidSimulator.prototype.animateProgress = function() {
    let stepIdx = 0;
    const steps = [
        [15, 'Calculating impact physics...', 0],
        [35, 'Simulating atmospheric entry...', 1],
        [55, 'Analyzing blast effects...', 2],
        [75, 'Computing economic damage...', 3],
        [95, 'Running AI risk model...', 4]
    ];

    const fill = document.getElementById('progress-fill');
    const text = document.getElementById('loading-step-text');

    const interval = setInterval(() => {
        if (stepIdx < steps.length) {
            const [pct, msg, idx] = steps[stepIdx++];
            if (fill) fill.style.width = `${pct}%`;
            if (text) text.textContent = msg;
            // Update step dots
            document.querySelectorAll('.lstep').forEach((el, i) => {
                el.classList.remove('active', 'done');
                if (i < idx) el.classList.add('done');
                else if (i === idx) el.classList.add('active');
            });
        } else {
            clearInterval(interval);
        }
    }, 600);
    this._progressInterval = interval;
};

// Also patch showError
AsteroidSimulator.prototype.showError = function(message) {
    showToast('❌ ' + message, 'error');
    addAIMessage(`⚠️ Simulation error: ${message}. Try adjusting your parameters.`);
};

/* ── Update launch button to show params ────────────────── */
document.getElementById('launch-button')?.addEventListener('click', () => {
    const sim = window.asteroidSimulator;
    if (!sim) return;
    
    // Also send mitigation strategy
    const stratSelect = document.getElementById('mitigation-select');
    if (stratSelect) {
        sim.params.mitigationStrategy = stratSelect.value;
    }
});

function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
}
