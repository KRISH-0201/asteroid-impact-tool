class ParticleSystem {
    constructor() {
        this.canvas = document.getElementById('particle-canvas');
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.animationId = null;
        
        this.init();
        this.animate();
        this.bindEvents();
    }
    
    init() {
        this.resize();
        this.createParticles();
    }
    
    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    
    createParticles() {
        const numParticles = Math.floor((this.canvas.width * this.canvas.height) / 15000);
        
        for (let i = 0; i < numParticles; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                size: Math.random() * 2 + 0.5,
                speedX: (Math.random() - 0.5) * 0.5,
                speedY: (Math.random() - 0.5) * 0.5,
                opacity: Math.random() * 0.5 + 0.2,
                twinkle: Math.random() * 0.02 + 0.005
            });
        }
    }
    
    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.particles.forEach(particle => {
            // Update position
            particle.x += particle.speedX;
            particle.y += particle.speedY;
            
            // Wrap around screen
            if (particle.x > this.canvas.width) particle.x = 0;
            if (particle.x < 0) particle.x = this.canvas.width;
            if (particle.y > this.canvas.height) particle.y = 0;
            if (particle.y < 0) particle.y = this.canvas.height;
            
            // Twinkle effect
            particle.opacity += Math.sin(Date.now() * particle.twinkle) * 0.01;
            particle.opacity = Math.max(0.1, Math.min(0.8, particle.opacity));
            
            // Draw particle
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fillStyle = `rgba(255, 255, 255, ${particle.opacity})`;
            this.ctx.fill();
            
            // Add glow effect for larger particles
            if (particle.size > 1.5) {
                this.ctx.beginPath();
                this.ctx.arc(particle.x, particle.y, particle.size * 2, 0, Math.PI * 2);
                this.ctx.fillStyle = `rgba(0, 102, 255, ${particle.opacity * 0.1})`;
                this.ctx.fill();
            }
        });
        
        this.animationId = requestAnimationFrame(() => this.animate());
    }
    
    bindEvents() {
        window.addEventListener('resize', () => {
            this.resize();
            this.particles = [];
            this.createParticles();
        });
        
        // Mouse interaction
        let mouseX = 0;
        let mouseY = 0;
        
        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
            
            // Create ripple effect near mouse
            this.particles.forEach(particle => {
                const dx = mouseX - particle.x;
                const dy = mouseY - particle.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 100) {
                    const force = (100 - distance) / 100;
                    particle.speedX += (dx / distance) * force * 0.01;
                    particle.speedY += (dy / distance) * force * 0.01;
                    particle.opacity = Math.min(1, particle.opacity + force * 0.1);
                }
            });
        });
    }
    
    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }
}

// Shooting stars effect
class ShootingStars {
    constructor() {
        this.canvas = document.getElementById('particle-canvas');
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.shootingStars = [];
        
        this.createShootingStars();
    }
    
    createShootingStars() {
        setInterval(() => {
            if (Math.random() < 0.1) { // 10% chance every interval
                this.shootingStars.push({
                    x: Math.random() * this.canvas.width,
                    y: 0,
                    speedX: (Math.random() - 0.5) * 4,
                    speedY: Math.random() * 2 + 2,
                    length: Math.random() * 80 + 20,
                    opacity: 1,
                    life: 100
                });
            }
            
            // Update and draw shooting stars
            this.shootingStars = this.shootingStars.filter(star => {
                star.x += star.speedX;
                star.y += star.speedY;
                star.life--;
                star.opacity = star.life / 100;
                
                if (star.life > 0) {
                    // Draw shooting star
                    const gradient = this.ctx.createLinearGradient(
                        star.x, star.y,
                        star.x - star.speedX * star.length,
                        star.y - star.speedY * star.length
                    );
                    gradient.addColorStop(0, `rgba(255, 255, 255, ${star.opacity})`);
                    gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
                    
                    this.ctx.beginPath();
                    this.ctx.moveTo(star.x, star.y);
                    this.ctx.lineTo(
                        star.x - star.speedX * star.length,
                        star.y - star.speedY * star.length
                    );
                    this.ctx.strokeStyle = gradient;
                    this.ctx.lineWidth = 2;
                    this.ctx.stroke();
                    
                    return true;
                }
                return false;
            });
        }, 2000); // Check every 2 seconds
    }
}

// Initialize particle system when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('particle-canvas')) {
        window.particleSystem = new ParticleSystem();
        window.shootingStars = new ShootingStars();
    }
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (window.particleSystem) {
        window.particleSystem.destroy();
    }
});
