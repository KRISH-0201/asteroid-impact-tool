// ============================================================
// AsteroidIQ — Landing Page JavaScript
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    initNav();
    initStarfield();
    initLiveData();
    handlePresets();
    initCounterAnimations();
});

// ── Nav Scroll Effect ────────────────────────────────────────
function initNav() {
    const nav = document.getElementById('top-nav');
    window.addEventListener('scroll', () => {
        nav.classList.toggle('scrolled', window.scrollY > 50);
    }, { passive: true });
}

// ── Starfield Canvas Background ──────────────────────────────
function initStarfield() {
    const canvas = document.getElementById('space-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let W, H, stars = [], animFrame;

    function resize() {
        W = canvas.width = window.innerWidth;
        H = canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize, { passive: true });

    // Generate stars
    for (let i = 0; i < 280; i++) {
        stars.push({
            x: Math.random() * W,
            y: Math.random() * H,
            r: Math.random() * 1.5 + 0.2,
            alpha: Math.random(),
            speed: Math.random() * 0.3 + 0.05,
            drift: (Math.random() - 0.5) * 0.05
        });
    }

    // Shooting stars
    const shooters = [];
    function addShooter() {
        if (shooters.length < 3) {
            shooters.push({
                x: Math.random() * W,
                y: Math.random() * H * 0.5,
                vx: 3 + Math.random() * 5,
                vy: 1 + Math.random() * 2,
                len: 80 + Math.random() * 120,
                alpha: 1,
                life: 1
            });
        }
        setTimeout(addShooter, 3000 + Math.random() * 5000);
    }
    addShooter();

    function draw(t) {
        ctx.clearRect(0, 0, W, H);

        // Stars
        stars.forEach(s => {
            const twinkle = 0.4 + 0.6 * (0.5 + 0.5 * Math.sin(t / 1000 * s.speed + s.alpha * 10));
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255,255,255,${twinkle * 0.7})`;
            ctx.fill();
        });

        // Shooting stars
        for (let i = shooters.length - 1; i >= 0; i--) {
            const s = shooters[i];
            s.life -= 0.012;
            if (s.life <= 0) { shooters.splice(i, 1); continue; }
            
            const alpha = Math.min(s.life, 0.8);
            const grd = ctx.createLinearGradient(s.x - s.vx * s.len / 10, s.y - s.vy * s.len / 10, s.x, s.y);
            grd.addColorStop(0, `rgba(0, 200, 255, 0)`);
            grd.addColorStop(1, `rgba(255, 255, 255, ${alpha})`);
            
            ctx.beginPath();
            ctx.moveTo(s.x - s.vx * s.len / 10, s.y - s.vy * s.len / 10);
            ctx.lineTo(s.x, s.y);
            ctx.strokeStyle = grd;
            ctx.lineWidth = 1.5;
            ctx.stroke();
            
            s.x += s.vx;
            s.y += s.vy;
        }

        animFrame = requestAnimationFrame(draw);
    }

    animFrame = requestAnimationFrame(draw);
}

// ── Live Data Feed ───────────────────────────────────────────
async function initLiveData() {
    try {
        const res = await fetch('/api/nasa/live-feed');
        if (!res.ok) throw new Error('fetch failed');
        
        const data = await res.json();
        renderAsteroidFeed(data.asteroids || []);
        
        // Update stat
        const stats = data.stats;
        if (stats && stats.today_count !== undefined) {
            animateNumber('stat-today', stats.today_count);
        }
        
    } catch (e) {
        console.warn('Live feed fallback:', e.message);
        renderFallbackFeed();
    }
}

function renderAsteroidFeed(asteroids) {
    const container = document.getElementById('live-asteroid-feed');
    if (!container) return;

    if (!asteroids.length) {
        container.innerHTML = '<div style="padding:2rem; text-align:center; color: rgba(255,255,255,0.4);">No asteroids in current window</div>';
        return;
    }

    const rows = asteroids.slice(0, 8).map(a => {
        const name = a.name || 'Unknown';
        const diam = a.estimated_diameter_max ? `${(a.estimated_diameter_max / 1000).toFixed(3)} km` : 'N/A';
        const speed = a.velocity_km_s ? `${parseFloat(a.velocity_km_s).toFixed(1)} km/s` : 'N/A';
        const miss = a.miss_distance_km ? formatDistance(a.miss_distance_km) : 'N/A';
        const hazard = a.is_hazardous 
            ? `<span class="hazard-yes">⚠ Yes</span>`
            : `<span class="hazard-no">✓ No</span>`;
        
        return `
            <div class="asteroid-feed-row" onclick="window.location='/simulator?lat=0&lon=0&diameter=${a.estimated_diameter_max||100}&speed=${a.velocity_km_s||17}'" style="cursor:pointer;" title="Simulate this asteroid">
                <span style="font-weight:500;">${name}</span>
                <span style="color:rgba(255,255,255,0.7)">${diam}</span>
                <span style="color:rgba(255,255,255,0.7)">${speed}</span>
                <span style="color:rgba(255,255,255,0.7)">${miss}</span>
                <span>${hazard}</span>
            </div>
        `;
    }).join('');

    container.innerHTML = rows;
}

function renderFallbackFeed() {
    const container = document.getElementById('live-asteroid-feed');
    if (!container) return;
    
    const fallback = [
        { name: '2024 YR4', diam: '0.055 km', speed: '16.2 km/s', miss: '4.2M km', hazard: false },
        { name: '(2021 AF8)', diam: '0.18 km', speed: '14.8 km/s', miss: '2.1M km', hazard: true },
        { name: '455176 (1999)', diam: '0.42 km', speed: '22.1 km/s', miss: '6.8M km', hazard: true },
        { name: '2023 DZ2', diam: '0.042 km', speed: '9.4 km/s', miss: '8.4M km', hazard: false },
        { name: '(2020 NK1)', diam: '0.12 km', speed: '18.7 km/s', miss: '11.2M km', hazard: false },
    ];

    container.innerHTML = fallback.map(a => `
        <div class="asteroid-feed-row">
            <span style="font-weight:500;">${a.name}</span>
            <span style="color:rgba(255,255,255,0.7)">${a.diam}</span>
            <span style="color:rgba(255,255,255,0.7)">${a.speed}</span>
            <span style="color:rgba(255,255,255,0.7)">${a.miss}</span>
            <span>${a.hazard ? '<span class="hazard-yes">⚠ Yes</span>' : '<span class="hazard-no">✓ No</span>'}</span>
        </div>
    `).join('');
}

function formatDistance(km) {
    const n = parseFloat(km);
    if (n >= 1e6) return `${(n / 1e6).toFixed(2)}M km`;
    if (n >= 1e3) return `${(n / 1e3).toFixed(0)}K km`;
    return `${n.toFixed(0)} km`;
}

// ── Counter Animations ───────────────────────────────────────
function initCounterAnimations() {
    animateNumber('stat-tracked', 28915);
    animateNumber('stat-hazardous', 2350);
}

function animateNumber(id, target) {
    const el = document.getElementById(id);
    if (!el) return;
    
    let current = 0;
    const duration = 2000;
    const start = performance.now();
    const isFloat = target % 1 !== 0;

    function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        current = eased * target;
        
        if (isFloat) {
            el.textContent = current.toFixed(1);
        } else if (target >= 1000) {
            el.textContent = Math.round(current).toLocaleString();
        } else {
            el.textContent = Math.round(current);
        }
        
        if (progress < 1) requestAnimationFrame(update);
    }
    
    // Start when element is in view
    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
            requestAnimationFrame(update);
            observer.disconnect();
        }
    }, { threshold: 0.1 });
    observer.observe(el);
}

// ── Preset Handling ──────────────────────────────────────────
function handlePresets() {
    // Check if navigated with preset param (from historical cards)
    const cards = document.querySelectorAll('.historical-card');
    cards.forEach(card => {
        card.addEventListener('click', function(e) {
            e.preventDefault();
            // The onclick already handles navigation
        });
    });
}

// ── Intersection Observer Animations ────────────────────────
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });

document.querySelectorAll('.feature-card, .step-card, .historical-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});
