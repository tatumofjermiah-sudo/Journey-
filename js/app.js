/**
 * app.js — Main application logic
 * Handles: navigation active state, scroll reveals, symbol hover effects,
 *          section entrance animations, footer year, mood-select preview.
 */
(function () {
  'use strict';

  // ── Footer year ────────────────────────────────────────────────
  const yearEl = document.getElementById('footer-year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // ── Active nav link on scroll ──────────────────────────────────
  const navLinks = Array.from(document.querySelectorAll('.nav-link'));
  const sections = Array.from(document.querySelectorAll('section[id], header[id]'));

  function updateActiveNav() {
    let current = '';
    sections.forEach(sec => {
      const top = sec.getBoundingClientRect().top;
      if (top <= window.innerHeight * 0.45) current = sec.id;
    });
    navLinks.forEach(link => {
      const href = link.getAttribute('href').replace('#', '');
      link.classList.toggle('active', href === current);
    });
  }

  // ── Reveal on scroll (section titles, value items, etc.) ───────
  function setupRevealObserver() {
    const revealEls = document.querySelectorAll(
      '.section-title, .section-intro, .value-item, .about-card, .tattoo-card, .daily-form-wrap, .journal-form-wrap, .mood-display'
    );

    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('reveal', 'visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });

    revealEls.forEach(el => {
      el.classList.add('reveal');
      io.observe(el);
    });
  }

  // ── Tattoo card keyboard/hover polish ─────────────────────────
  function setupTattooCards() {
    document.querySelectorAll('.tattoo-card').forEach(card => {
      card.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          card.classList.toggle('active-reveal');
        }
      });
    });
  }

  // ── Mood select preview — change body mood on select change ───
  function setupMoodSelectPreview() {
    const moodSelect = document.getElementById('mood-select');
    if (!moodSelect) return;

    let previewTimer;
    moodSelect.addEventListener('change', () => {
      clearTimeout(previewTimer);
      const selected = moodSelect.value;

      // Temporarily preview mood colour on body
      if (window.JourneyMood) window.JourneyMood.apply(selected);

      // Revert to last-saved mood after 4 s if entry not yet submitted
      previewTimer = setTimeout(() => {
        const last = getLastSavedMood();
        if (window.JourneyMood) window.JourneyMood.apply(last);
      }, 4000);
    });
  }

  function getLastSavedMood() {
    try {
      const entries = JSON.parse(localStorage.getItem('journey_journal_entries')) || [];
      if (entries.length > 0) return entries[entries.length - 1].mood;
    } catch (_) {}
    return 'neutral';
  }

  // ── Ambient symbol subtle parallax on mouse move ───────────────
  function setupParallax() {
    const syms = document.querySelectorAll('.sym');
    if (!syms.length) return;

    let tX = 0, tY = 0;
    let cX = 0, cY = 0;
    let afId;

    document.addEventListener('mousemove', e => {
      tX = (e.clientX / window.innerWidth  - 0.5) * 18;
      tY = (e.clientY / window.innerHeight - 0.5) * 18;
    });

    function loop() {
      cX += (tX - cX) * 0.04;
      cY += (tY - cY) * 0.04;
      syms.forEach((sym, i) => {
        const depth = 0.4 + (i % 3) * 0.3;
        sym.style.transform = `translate(${cX * depth}px, ${cY * depth}px)`;
      });
      afId = requestAnimationFrame(loop);
    }
    loop();
  }

  // ── Nav smooth highlight (CSS active class) ────────────────────
  function setupNavHighlight() {
    navLinks.forEach(link => {
      link.style.cssText += '; transition: color 0.4s ease;';
    });
  }

  // ── Scroll listener (throttled) ────────────────────────────────
  let scrollScheduled = false;
  window.addEventListener('scroll', () => {
    if (!scrollScheduled) {
      scrollScheduled = true;
      requestAnimationFrame(() => {
        updateActiveNav();
        scrollScheduled = false;
      });
    }
  }, { passive: true });

  // ── Init ───────────────────────────────────────────────────────
  function init() {
    setupRevealObserver();
    setupTattooCards();
    setupMoodSelectPreview();
    setupParallax();
    setupNavHighlight();
    updateActiveNav();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

}());
