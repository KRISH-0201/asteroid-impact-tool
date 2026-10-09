// InteractiveMap - helper for the tracking dashboard map only
// The simulator page uses AsteroidSimulator which manages its own Leaflet map.

class InteractiveMap {
    constructor(mapElementId, options = {}) {
        this.mapElementId = mapElementId;
        this.map = null;
        this.marker = null;
        this.currentPosition = {
            lat: options.lat || 40.7128,
            lng: options.lng || -74.0060
        };
        this.initMap(options);
        this.bindMapClick();
        this.bindLocationButtons();
    }

    initMap(options) {
        const el = document.getElementById(this.mapElementId);
        if (!el) return;

        this.map = L.map(this.mapElementId, {
            center: [this.currentPosition.lat, this.currentPosition.lng],
            zoom: options.zoom || 3,
            zoomControl: options.zoomControl !== false
        });

        // Use Esri dark canvas tiles for aesthetic consistency with zero watermark
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
            maxZoom: 16
        }).addTo(this.map);

        this.marker = L.marker([this.currentPosition.lat, this.currentPosition.lng]).addTo(this.map);
    }

    bindMapClick() {
        if (!this.map) return;
        this.map.on('click', (e) => {
            this.currentPosition = e.latlng;
            this.updateMarker(this.currentPosition);
            this.updateCoordinatesDisplay(this.currentPosition);
            
            // Update simulator params if available (only for impact-map context)
            if (window.asteroidSimulator && this.mapElementId === 'impact-map') {
                window.asteroidSimulator.params.latitude = e.latlng.lat;
                window.asteroidSimulator.params.longitude = e.latlng.lng;
            }
        });
    }

    updateMarker(latlng) {
        if (this.marker) {
            this.marker.setLatLng(latlng);
        } else if (this.map) {
            this.marker = L.marker(latlng).addTo(this.map);
        }
    }

    updateCoordinatesDisplay(latlng) {
        const coordElem = document.getElementById('current-coordinates');
        if (coordElem) {
            const latDir = latlng.lat >= 0 ? 'N' : 'S';
            const lonDir = latlng.lng >= 0 ? 'E' : 'W';
            coordElem.textContent = `${Math.abs(latlng.lat).toFixed(4)}°${latDir}, ${Math.abs(latlng.lng).toFixed(4)}°${lonDir}`;
        }
    }

    bindLocationButtons() {
        const buttons = document.querySelectorAll('.location-btn');
        buttons.forEach(button => {
            button.addEventListener('click', () => {
                const lat = parseFloat(button.getAttribute('data-lat'));
                const lng = parseFloat(button.getAttribute('data-lon'));
                this.setLocation(lat, lng);
            });
        });
    }

    setLocation(lat, lng) {
        this.currentPosition = { lat, lng };
        if (this.map) this.map.setView([lat, lng], 6);
        this.updateMarker(this.currentPosition);
        this.updateCoordinatesDisplay(this.currentPosition);
        
        if (window.asteroidSimulator) {
            window.asteroidSimulator.params.latitude = lat;
            window.asteroidSimulator.params.longitude = lng;
        }
    }
}

// Global helper for location-btn elements used on the simulator page
window.setImpactLocation = function(lat, lng) {
    if (window.asteroidSimulator) {
        window.asteroidSimulator.params.latitude = lat;
        window.asteroidSimulator.params.longitude = lng;
        window.asteroidSimulator.map.setView([lat, lng], 6);
        window.asteroidSimulator.updateMarker({ lat, lng });
        window.asteroidSimulator.updateCoordinatesDisplay({ lat, lng });
    }
};

// Initialize on DOM ready - only for tracking-map (dashboard page)
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize for dashboard tracking map – simulator manages its own
    const trackingEl = document.getElementById('tracking-map');
    if (trackingEl && !window.trackingMap) {
        window.interactiveMap = new InteractiveMap('tracking-map', { zoom: 2, zoomControl: false });
        window.trackingMap = window.interactiveMap.map;
    }
});
