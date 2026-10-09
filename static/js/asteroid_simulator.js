class AsteroidSimulator {
    constructor() {
        this.params = {
            asteroid_type: 'stone',
            diameter: 100,
            speed: 17,
            angle: 45,
            latitude: 40.7128,
            longitude: -74.0060
        };
        this.circles = [];
        this.init();
    }
    
    init() {
        this.initMap();
        this.bindControls();
        this.bindLaunch();
    }
    
    initMap() {
        this.map = L.map('impact-map').setView([this.params.latitude, this.params.longitude], 3);
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
            maxZoom: 16
        }).addTo(this.map);
        
        this.marker = L.marker([this.params.latitude, this.params.longitude]).addTo(this.map);
        
        this.map.on('click', e => {
            this.params.latitude = e.latlng.lat;
            this.params.longitude = e.latlng.lng;
            this.updateMarker(e.latlng);
            this.updateCoordinatesDisplay(e.latlng);
        });
    }
    
    updateMarker(latlng) {
        if (this.marker) {
            this.map.removeLayer(this.marker);
        }
        this.marker = L.marker([latlng.lat, latlng.lng]).addTo(this.map);
    }
    
    updateCoordinatesDisplay(latlng) {
        const coordElem = document.getElementById('current-coordinates');
        if (coordElem) {
            const latDir = latlng.lat >= 0 ? 'N' : 'S';
            const lonDir = latlng.lng >= 0 ? 'E' : 'W';
            coordElem.textContent = `${Math.abs(latlng.lat).toFixed(4)}°${latDir}, ${Math.abs(latlng.lng).toFixed(4)}°${lonDir}`;
        }
    }
    
    bindControls() {
        // Asteroid type selection
        document.querySelectorAll('.asteroid-card').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.asteroid-card').forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                this.params.asteroid_type = card.dataset.type;
            });
        });
        
        // Sliders
        this.setupSlider('diameter-slider', 'diameter', 'diameter-value', 'm');
        this.setupSlider('speed-slider', 'speed', 'speed-value', ' km/s');
        this.setupSlider('angle-slider', 'angle', 'angle-value', '°');
    }
    
    setupSlider(id, key, displayId, unit) {
        const slider = document.getElementById(id);
        const display = document.getElementById(displayId);
        
        if (slider && display) {
            slider.addEventListener('input', e => {
                this.params[key] = Number(e.target.value);
                display.textContent = e.target.value + unit;
            });
        }
    }
    
    bindLaunch() {
        const btn = document.getElementById('launch-button');
        if (btn) {
            btn.addEventListener('click', async () => {
                const mitSelect = document.getElementById('mitigation-select');
                if (mitSelect) {
                    this.params.mitigationStrategy = mitSelect.value;
                    this.params.mitigation_strategy = mitSelect.value;
                }
                this.showLoading();
                this.animateProgress();
                try {
                    const response = await fetch('/api/launch', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(this.params)
                    });
                    
                    if (!response.ok) {
                        const errData = await response.json();
                        throw new Error(errData.error || `HTTP ${response.status}`);
                    }
                    
                    const data = await response.json();
                    this.displayResults(data);
                } catch (error) {
                    console.error('Simulation failed:', error);
                    this.showError(`Simulation failed: ${error.message}`);
                } finally {
                    this.hideLoading();
                }
            });
        }
    }
    
    animateProgress() {
        let progress = 0;
        const fill = document.getElementById('progress-fill');
        const text = document.getElementById('progress-text');
        const steps = [
            [20, 'Calculating impact physics...'],
            [40, 'Simulating atmospheric entry...'],
            [60, 'Analyzing blast effects...'],
            [80, 'Calculating economic impact...'],
            [95, 'Finalizing results...']
        ];
        
        let stepIdx = 0;
        const interval = setInterval(() => {
            if (stepIdx < steps.length) {
                const [pct, msg] = steps[stepIdx++];
                if (fill) fill.style.width = `${pct}%`;
                if (text) text.textContent = msg;
            } else {
                clearInterval(interval);
            }
        }, 600);
        
        this._progressInterval = interval;
    }
    
    showLoading() {
        const overlay = document.getElementById('simulation-loading');
        if (overlay) overlay.classList.add('active');
        const fill = document.getElementById('progress-fill');
        if (fill) fill.style.width = '0%';
    }
    
    hideLoading() {
        const overlay = document.getElementById('simulation-loading');
        if (overlay) overlay.classList.remove('active');
        if (this._progressInterval) clearInterval(this._progressInterval);
    }
    
    formatNumber(n) {
        if (n === undefined || n === null) return '0';
        return Number(n).toLocaleString(undefined, { maximumFractionDigits: 2 });
    }
    
    formatCurrency(n) {
        if (!n) return '$0';
        if (n >= 1e12) return `$${(n/1e12).toFixed(2)}T`;
        if (n >= 1e9) return `$${(n/1e9).toFixed(2)}B`;
        if (n >= 1e6) return `$${(n/1e6).toFixed(2)}M`;
        return `$${n.toLocaleString()}`;
    }
    
    displayResults(data) {
        const section = document.getElementById('results-section') || document.getElementById('results-panel');
        const content = document.getElementById('results-content');
        
        if (!content) return;
        if (section) {
            section.classList.add('active');
            section.style.display = 'flex';
        }
        
        const energy = data.impact_basic?.energy_megatons || 0;
        const craterDiam = data.crater?.diameter_km || 0;
        const fireballR = data.fireball?.radius_km || 0;
        const blastRange = data.shockwave?.max_range_km || 0;
        const windSpeed = data.winds?.max_speed_kmh || 0;
        const magnitude = data.earthquake?.magnitude || 0;
        
        const totalDeaths = (data.crater?.people_killed || 0)
            + (data.fireball?.deaths || 0)
            + (data.shockwave?.deaths || 0)
            + (data.winds?.deaths || 0)
            + (data.earthquake?.deaths || 0);
        
        const hiroshima = energy > 0 ? (energy / 0.015).toFixed(0) : 0;
        
        // Economic data
        const econ = data.economic_impact || {};
        const totalEcon = econ.total_economic_impact_usd || 0;
        const econClass = econ.summary?.impact_classification || 'Unknown';
        const recoveryYears = econ.summary?.recovery_timeline_years?.toFixed(1) || 'N/A';
        const directDamage = econ.direct_damage?.direct_damage_usd || 0;
        
        // Mitigation options
        const mitigations = data.mitigation_options || [];
        
        // Atmospheric
        const atmo = data.atmospheric_entry || {};
        const energyRetained = atmo.energy_retention ? `${(atmo.energy_retention * 100).toFixed(1)}%` : 'N/A';
        const maxTemp = atmo.max_temperature ? `${Math.round(atmo.max_temperature).toLocaleString()}K` : 'N/A';
        const survived = atmo.survived !== undefined ? (atmo.survived ? '✅ Ground Impact' : '💥 Airburst') : 'N/A';
        
        content.innerHTML = `
            <!-- KEY STATS GRID -->
            <div class="results-grid">
                <div class="result-card">
                    <h4><i class="fas fa-bolt"></i> Impact Energy</h4>
                    <div class="result-value">${this.formatNumber(energy)} MT</div>
                    <p>${Number(hiroshima).toLocaleString()} Hiroshima bombs</p>
                </div>
                <div class="result-card">
                    <h4><i class="fas fa-circle"></i> Crater Diameter</h4>
                    <div class="result-value">${craterDiam.toFixed(2)} km</div>
                    <p>Complete destruction zone</p>
                </div>
                <div class="result-card">
                    <h4><i class="fas fa-fire"></i> Fireball Radius</h4>
                    <div class="result-value">${fireballR.toFixed(2)} km</div>
                    <p>Thermal radiation zone</p>
                </div>
                <div class="result-card">
                    <h4><i class="fas fa-skull"></i> Total Deaths</h4>
                    <div class="result-value">${this.formatNumber(totalDeaths)}</div>
                    <p>All effects combined</p>
                </div>
            </div>

            <!-- DAMAGE BREAKDOWN -->
            <div class="damage-breakdown">
                <h3><i class="fas fa-radiation"></i> Damage Breakdown</h3>
                <div class="damage-list">
                    <div class="damage-item">
                        <span>🕳️ Crater Zone</span>
                        <span>${this.formatNumber(data.crater?.people_killed || 0)} deaths</span>
                    </div>
                    <div class="damage-item">
                        <span>🔥 Fireball</span>
                        <span>${this.formatNumber(data.fireball?.deaths || 0)} deaths</span>
                    </div>
                    <div class="damage-item">
                        <span>💥 Blast Wave</span>
                        <span>${this.formatNumber(data.shockwave?.deaths || 0)} deaths</span>
                    </div>
                    <div class="damage-item">
                        <span>💨 Wind Blast</span>
                        <span>${this.formatNumber(data.winds?.deaths || 0)} deaths</span>
                    </div>
                    <div class="damage-item">
                        <span>📏 Blast Range</span>
                        <span>${blastRange.toFixed(2)} km</span>
                    </div>
                    <div class="damage-item">
                        <span>🌪️ Max Wind Speed</span>
                        <span>${windSpeed.toFixed(0)} km/h</span>
                    </div>
                    <div class="damage-item">
                        <span>🌍 Earthquake</span>
                        <span>M${magnitude.toFixed(1)}</span>
                    </div>
                    <div class="damage-item">
                        <span>🛰️ Atmospheric</span>
                        <span>${survived}</span>
                    </div>
                    <div class="damage-item">
                        <span>🌡️ Peak Temp</span>
                        <span>${maxTemp}</span>
                    </div>
                    <div class="damage-item">
                        <span>⚡ Energy Retained</span>
                        <span>${energyRetained}</span>
                    </div>
                </div>
            </div>

            <!-- ECONOMIC IMPACT -->
            ${totalEcon > 0 ? `
            <div class="economic-section">
                <h3><i class="fas fa-dollar-sign"></i> Economic Impact — <span style="color:var(--warning-color)">${econClass}</span></h3>
                <div class="economic-grid">
                    <div class="economic-item">
                        <div class="eco-label">Total Damage</div>
                        <div class="eco-value">${this.formatCurrency(totalEcon)}</div>
                    </div>
                    <div class="economic-item">
                        <div class="eco-label">Direct Damage</div>
                        <div class="eco-value">${this.formatCurrency(directDamage)}</div>
                    </div>
                    <div class="economic-item">
                        <div class="eco-label">% of World GDP</div>
                        <div class="eco-value">${econ.summary?.percent_global_gdp?.toFixed(3) || '0'}%</div>
                    </div>
                    <div class="economic-item">
                        <div class="eco-label">Recovery Time</div>
                        <div class="eco-value">${recoveryYears} years</div>
                    </div>
                </div>
            </div>` : ''}

            <!-- MITIGATION OPTIONS -->
            ${mitigations.length > 0 ? `
            <div class="mitigation-section">
                <h3><i class="fas fa-shield-alt"></i> Planetary Defense Options</h3>
                <div class="mitigation-list">
                    ${mitigations.map(m => `
                        <div class="mitigation-item">
                            <div>
                                <div class="strategy-name">🛡️ ${m.strategy}</div>
                                <div class="strategy-desc">${m.description}</div>
                            </div>
                            <span class="feasibility-badge ${m.feasibility || m.effectiveness}">${m.feasibility || m.effectiveness}</span>
                        </div>
                    `).join('')}
                </div>
            </div>` : ''}
        `;
        
        // Draw damage zones on map and fit to extent
        this.drawDamageZones(data);
        
        // Notify UI controller and ARIA AI assistant
        if (typeof window.onSimulationComplete === 'function') {
            window.onSimulationComplete(data);
        }
        
        // Bind close button
        const closeBtn = document.getElementById('btn-close-results') || document.getElementById('close-results');
        if (closeBtn) {
            closeBtn.onclick = () => {
                if (section) {
                    section.classList.remove('active');
                    section.style.display = 'none';
                }
                this.clearMap();
            };
        }
    }
    
    drawDamageZones(data) {
        this.clearMap();
        
        const lat = this.params.latitude;
        const lon = this.params.longitude;
        
        // Re-add marker
        this.marker = L.marker([lat, lon]).addTo(this.map);
        
        if (data.visualization_data && data.visualization_data.damage_zones) {
            const allBounds = [];
            
            data.visualization_data.damage_zones.forEach(zone => {
                if (zone.radius_km <= 0) return;
                
                const circle = L.circle(zone.center, {
                    radius: zone.radius_km * 1000,
                    color: zone.color,
                    fillColor: zone.color,
                    fillOpacity: zone.opacity || 0.25,
                    weight: 2
                }).addTo(this.map).bindPopup(`
                    <strong>${zone.label}</strong><br>
                    Radius: ${zone.radius_km.toFixed(2)} km
                `);
                
                this.circles.push(circle);
                
                // Compute bounding box corners
                const R = zone.radius_km / 111; // approx degrees
                allBounds.push([zone.center[0] - R, zone.center[1] - R]);
                allBounds.push([zone.center[0] + R, zone.center[1] + R]);
            });
            
            if (allBounds.length > 0) {
                this.map.fitBounds(allBounds, { padding: [40, 40] });
            }
        }
    }
    
    clearMap() {
        if (this.circles) {
            this.circles.forEach(c => this.map.removeLayer(c));
            this.circles = [];
        }
    }
    
    showError(message) {
        const section = document.getElementById('results-section') || document.getElementById('results-panel');
        const content = document.getElementById('results-content');
        if (content) {
            content.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Simulation Error</h3>
                    <p>${message}</p>
                </div>
            `;
            if (section) {
                section.classList.add('active');
                section.style.display = 'flex';
            }
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.asteroidSimulator = new AsteroidSimulator();
});
