/**
 * particles.js — Canvas-based particle system
 * Renders drifting smoke / light particles across the background.
 * Adapts color based on body[data-mood].
 */
(function () {
  'use strict';

  const canvas = document.getElementById('particle-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');

  // ── Mood color maps ───────────────────────────────────────────
  const MOOD_PALETTES = {
    neutral:    ['rgba(20,30,60,',    'rgba(80,0,0,',      'rgba(30,30,50,'],
    reflective: ['rgba(20,20,80,',    'rgba(10,10,40,',    'rgba(60,60,120,'],
    intense:    ['rgba(100,0,0,',     'rgba(60,10,10,',    'rgba(140,20,20,'],
    peaceful:   ['rgba(0,40,50,',     'rgba(0,60,60,',     'rgba(10,30,40,'],
    raw:        ['rgba(80,40,0,',     'rgba(60,20,0,',     'rgba(100,50,10,'],
    grateful:   ['rgba(60,50,0,',     'rgba(40,30,0,',     'rgba(80,70,10,'],
    conflicted: ['rgba(50,0,80,',     'rgba(30,0,60,',     'rgba(70,10,100,'],
  };

  // ── Particle class ────────────────────────────────────────────
  class Particle {
    constructor(w, h) {
      this.reset(w, h, true);
    }

    reset(w, h, initial) {
      this.x     = Math.random() * w;
      this.y     = initial ? Math.random() * h : h + 10;
      this.r     = 0.5 + Math.random() * 2.5;
      this.vx    = (Math.random() - 0.5) * 0.3;
      this.vy    = -(0.15 + Math.random() * 0.35);
      this.life  = 0;
      this.maxL  = 180 + Math.random() * 200;
      this.drift = (Math.random() - 0.5) * 0.008;  // slow sine drift
      this.angle = Math.random() * Math.PI * 2;
    }

    update(w, h) {
      this.life++;
      this.angle += this.drift;
      this.x += this.vx + Math.sin(this.angle) * 0.15;
      this.y += this.vy;
      if (this.y < -10 || this.x < -10 || this.x > w + 10) {
        this.reset(w, h, false);
      }
    }

    alpha() {
      const half = this.maxL / 2;
      if (this.life < half) return (this.life / half) * 0.55;
      return ((this.maxL - this.life) / half) * 0.55;
    }

    draw(ctx, colours) {
      const col = colours[Math.floor(this.r * 10) % colours.length];
      const a   = this.alpha();
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
      ctx.fillStyle = col + a + ')';
      ctx.fill();
    }
  }

  // ── Setup ─────────────────────────────────────────────────────
  let particles = [];
  let W = 0, H = 0;
  let animId;

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function init() {
    resize();
    const count = Math.min(Math.floor((W * H) / 8000), 180);
    particles = Array.from({ length: count }, () => new Particle(W, H));
  }

  function getMoodPalette() {
    const mood = document.body.getAttribute('data-mood') || 'neutral';
    return MOOD_PALETTES[mood] || MOOD_PALETTES.neutral;
  }

  function render() {
    ctx.clearRect(0, 0, W, H);
    const colours = getMoodPalette();
    for (const p of particles) {
      p.update(W, H);
      p.draw(ctx, colours);
    }
    animId = requestAnimationFrame(render);
  }

  // ── Events ────────────────────────────────────────────────────
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      cancelAnimationFrame(animId);
      init();
      render();
    }, 200);
  });

  // Expose a function for app.js to call on mood change
  window.JourneyParticles = { reinit: init };

  init();
  render();
}());
