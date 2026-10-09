class RealTimeDataManager {
    constructor() {
        this.updateInterval = 300000; // 5 minutes
        this.isUpdating = false;
        this.lastUpdate = null;
        this.asteroidData = [];
        this.sentryData = [];
        this.init();
    }
    
    async init() {
        await this.fetchAllData();
        this.updateStats();
        this.startAutoUpdate();
    }
    
    async fetchAllData() {
        if (this.isUpdating) return;
        
        this.isUpdating = true;
        this.setRefreshAnimation(true);
        
        try {
            const [asteroidsRes, statsRes, sentryRes] = await Promise.all([
                fetch('/api/nasa/live-feed'),
                fetch('/api/stats/global'),
                fetch('/api/nasa/sentry')
            ]);
            
            if (asteroidsRes.ok) {
                const asteroidData = await asteroidsRes.json();
                this.asteroidData = asteroidData.asteroids || [];
                this.updateAsteroidList();
            }
            
            if (statsRes.ok) {
                const statsData = await statsRes.json();
                this.updateGlobalStats(statsData);
            }
            
            if (sentryRes.ok) {
                const sentryData = await sentryRes.json();
                this.sentryData = sentryData.sentry_objects || [];
                this.renderSentryObjects();
            }
            
            this.lastUpdate = new Date();
            this.updateLastUpdateTime();
            
        } catch (error) {
            console.error('Failed to fetch data:', error);
            this.loadFallbackData();
        } finally {
            this.isUpdating = false;
            this.setRefreshAnimation(false);
        }
    }
    
    updateStats() {
        // Update counter animations with initial values
        this.animateCounter('total-tracked', 28915);
        this.animateCounter('potentially-hazardous', 2);
        this.animateCounter('approaching-today', 3);
        this.animateCounter('tracked-asteroids', 28915);
        this.animateCounter('simulations-run', 1247);
        this.animateCounter('impact-energy', 15.2);
    }
    
    setRefreshAnimation(active) {
        const btn = document.getElementById('refresh-data');
        if (!btn) return;
        if (active) {
            btn.style.animation = 'spin 0.8s linear infinite';
        } else {
            btn.style.animation = '';
        }
    }
    
    updateLastUpdateTime() {
        const el = document.getElementById('last-update-time');
        if (el && this.lastUpdate) {
            el.textContent = this.lastUpdate.toLocaleTimeString();
        }
    }
    
    renderSentryObjects() {
        const container = document.getElementById('risk-objects');
        if (!container) return;
        
        if (!this.sentryData || this.sentryData.length === 0) {
            container.innerHTML = '<div class="no-data">No high-risk objects found</div>';
            return;
        }
        
        container.innerHTML = this.sentryData.map(obj => `
            <div class="risk-item">
                <div class="risk-name">
                    🌑 ${obj.designation}
                    ${obj.threat_level ? `<span class="risk-level ${obj.threat_level}">${obj.threat_level}</span>` : ''}
                </div>
                <div class="risk-details">
                    <span>⚡ Impact Prob: ${obj.impact_probability || 'N/A'}</span>
                    <span>📅 Max Year: ${obj.year_range_max || 'N/A'}</span>
                    <span>📏 Diameter: ${obj.estimated_diameter || 'N/A'}m</span>
                    <span>🏆 Torino Scale: ${obj.torino_scale || '0'}</span>
                    ${obj.potential_impacts ? `<span>☄️ Impacts: ${obj.potential_impacts}</span>` : ''}
                    <span>📊 Palermo: ${obj.palermo_scale_max || 'N/A'}</span>
                </div>
            </div>
        `).join('');
    }
    
    updateAsteroidList() {
        const container = document.getElementById('approaching-list');
        if (!container) return;
        
        if (this.asteroidData.length === 0) {
            container.innerHTML = '<div class="no-data">No asteroids approaching today</div>';
            return;
        }
        
        container.innerHTML = '';
        
        // Sort by closest approach
        const sortedAsteroids = this.asteroidData
            .slice(0, 10) // Show top 10
            .map((asteroid, index) => this.createAsteroidElement(asteroid, index));
        
        sortedAsteroids.forEach(element => container.appendChild(element));
        
        // Update preview list for landing page
        const previewList = document.getElementById('preview-asteroids');
        if (previewList && this.asteroidData.length > 0) {
            previewList.innerHTML = this.asteroidData.slice(0, 3).map(asteroid => `
                <div class="preview-asteroid">
                    <div class="asteroid-info">
                        <strong>${asteroid.name || asteroid.designation}</strong>
                        <span>${((asteroid.diameter_min_m + asteroid.diameter_max_m) / 2).toFixed(0)}m • ${asteroid.velocity_km_s.toFixed(1)} km/s</span>
                    </div>
                    ${asteroid.is_hazardous ? '<span class="hazard-badge">⚠️</span>' : ''}
                </div>
            `).join('');
        }
    }
    
    createAsteroidElement(asteroid, index) {
        const element = document.createElement('div');
        element.className = 'asteroid-item data-item';
        element.style.animationDelay = `${index * 0.1}s`;
        
        const isHazardous = asteroid.is_hazardous;
        const dMin = Number(asteroid.diameter_min_m) || 0;
        const dMax = Number(asteroid.diameter_max_m) || 0;
        const diameter = ((dMin + dMax) / 2).toFixed(0);
        const missKm = Number(asteroid.miss_distance_km) || 0;
        const missDistance = (missKm / 384400).toFixed(2); // Lunar distances
        const velKms = Number(asteroid.velocity_km_s) || 0;

        element.innerHTML = `
            <div class="asteroid-header">
                <div class="asteroid-name">
                    ${asteroid.name || asteroid.designation}
                    ${isHazardous ? '<span class="hazard-badge">⚠️ PHA</span>' : ''}
                </div>
                <div class="asteroid-size">${diameter}m</div>
            </div>
            
            <div class="asteroid-details">
                <div class="detail-row">
                    <span class="label">Speed:</span>
                    <span class="value">${velKms.toFixed(1)} km/s</span>
                </div>
                <div class="detail-row">
                    <span class="label">Miss Distance:</span>
                    <span class="value">${missDistance} LD</span>
                </div>
                <div class="detail-row">
                    <span class="label">Approach:</span>
                    <span class="value">${asteroid.approach_date}</span>
                </div>
            </div>
            
            <div class="asteroid-actions">
                <button class="action-btn simulate-btn" onclick="window.simulateAsteroid('${asteroid.id}')">
                    <i class="fas fa-rocket"></i> Simulate
                </button>
            </div>
        `;
        
        return element;
    }
    
    updateGlobalStats(data) {
        if (!data || !data.tracking_stats) return;
        
        const stats = data.tracking_stats;
        this.animateCounter('total-tracked', stats.total_tracked || 0);
        this.animateCounter('potentially-hazardous', stats.hazardous_count || 0);
        this.animateCounter('approaching-today', stats.today_count || 0);
        
        // Update last update time
        const lastUpdateEl = document.getElementById('last-update-time');
        if (lastUpdateEl) {
            lastUpdateEl.textContent = new Date(stats.last_update).toLocaleTimeString();
        }
    }
    
    animateCounter(elementId, targetValue, duration = 2000) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const startValue = parseFloat(element.textContent.replace(/[^0-9.]/g, '')) || 0;
        const startTime = Date.now();
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentValue = startValue + (targetValue - startValue) * easeOut;
            
            if (targetValue % 1 === 0) {
                element.textContent = Math.floor(currentValue).toLocaleString();
            } else {
                element.textContent = currentValue.toFixed(1);
            }
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        animate();
    }
    
    loadFallbackData() {
        // Load static fallback data when API is unavailable
        this.asteroidData = [
            {
                id: 'fallback_1',
                name: '(2025 AA) Demo',
                designation: '2025 AA',
                is_hazardous: false,
                diameter_min_m: 80,
                diameter_max_m: 120,
                velocity_km_s: 17.2,
                miss_distance_km: 450000,
                approach_date: new Date().toISOString().split('T')[0],
                fallback: true
            },
            {
                id: 'fallback_2',
                name: '(2025 BB) Demo Large',
                designation: '2025 BB',
                is_hazardous: true,
                diameter_min_m: 200,
                diameter_max_m: 300,
                velocity_km_s: 22.5,
                miss_distance_km: 750000,
                approach_date: new Date().toISOString().split('T')[0],
                fallback: true
            },
            {
                id: 'fallback_3',
                name: '(2025 CC) Demo Fast',
                designation: '2025 CC',
                is_hazardous: false,
                diameter_min_m: 50,
                diameter_max_m: 80,
                velocity_km_s: 35.1,
                miss_distance_km: 1200000,
                approach_date: new Date().toISOString().split('T')[0],
                fallback: true
            }
        ];
        
        this.updateAsteroidList();
    }
    
    startAutoUpdate() {
        this.stopAutoUpdate(); // Clear any existing interval
        this.updateIntervalId = setInterval(() => {
            this.fetchAllData();
        }, this.updateInterval);
    }
    
    stopAutoUpdate() {
        if (this.updateIntervalId) {
            clearInterval(this.updateIntervalId);
            this.updateIntervalId = null;
        }
    }
}

// Global functions for asteroid interaction
window.simulateAsteroid = function(asteroidId) {
    const asteroid = window.realTimeData.asteroidData.find(a => a.id === asteroidId);
    if (!asteroid) return;
    
    // Set parameters in simulator
    if (window.asteroidSimulator) {
        const avgDiameter = (asteroid.diameter_min_m + asteroid.diameter_max_m) / 2;
        
        window.asteroidSimulator.params.diameter = avgDiameter;
        window.asteroidSimulator.params.speed = asteroid.velocity_km_s;
        window.asteroidSimulator.params.asteroid_type = 'stone'; // Default
        
        // Update UI sliders
        const diameterSlider = document.getElementById('diameter-slider');
        const speedSlider = document.getElementById('speed-slider');
        const diameterValue = document.getElementById('diameter-value');
        const speedValue = document.getElementById('speed-value');
        
        if (diameterSlider) diameterSlider.value = avgDiameter;
        if (speedSlider) speedSlider.value = asteroid.velocity_km_s;
        if (diameterValue) diameterValue.textContent = `${avgDiameter.toFixed(0)}m`;
        if (speedValue) speedValue.textContent = `${asteroid.velocity_km_s.toFixed(1)} km/s`;
        
        // Switch to simulator page
        if (window.location.pathname !== '/simulator') {
            window.location.href = '/simulator';
        }
        
        // Show notification
        window.showNotification(`Loaded asteroid ${asteroid.name} into simulator`, 'success');
    }
};

window.showNotification = function(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-info-circle"></i>
        <span>${message}</span>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--panel-bg);
        color: var(--text-primary);
        padding: 15px 20px;
        border-radius: 8px;
        border-left: 4px solid var(--primary-color);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 10px;
        backdrop-filter: blur(10px);
        animation: slideInFromRight 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideInFromRight 0.3s ease-out reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.realTimeData = new RealTimeDataManager();
});
