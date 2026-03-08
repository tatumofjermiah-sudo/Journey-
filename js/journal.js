/**
 * journal.js — Journal & Daily-Life entry management
 * Handles localStorage persistence, mood tracking, AI-style insights.
 */
(function () {
  'use strict';

  // ── Storage keys ───────────────────────────────────────────────
  const KEY_JOURNAL = 'journey_journal_entries';
  const KEY_DAILY   = 'journey_daily_moments';

  // ── Mood metadata ──────────────────────────────────────────────
  const MOOD_META = {
    neutral:    { label: 'Neutral',      color: '#c0c0c0', intensity: 30 },
    reflective: { label: 'Reflective',   color: '#7b9cdc', intensity: 55 },
    intense:    { label: 'Intense',      color: '#c0392b', intensity: 90 },
    peaceful:   { label: 'Peaceful',     color: '#2ecc71', intensity: 40 },
    raw:        { label: 'Raw / Honest', color: '#e67e22', intensity: 75 },
    grateful:   { label: 'Grateful',     color: '#f1c40f', intensity: 60 },
    conflicted: { label: 'Conflicted',   color: '#9b59b6', intensity: 70 },
  };

  // Insight messages keyed by mood
  const MOOD_INSIGHTS_MAP = {
    reflective: 'You\'ve been sitting with reflection lately. That space between stimulus and response—you\'re living in it. Something is being processed.',
    intense:    'Intensity is your home state. This fire isn\'t destruction—it\'s transformation. Watch what you\'re forging.',
    peaceful:   'Rare stillness. You\'ve been finding it more lately. This is the foundation the rest is built on.',
    raw:        'You\'re choosing honesty over comfort. That\'s harder than most people know. Keep going.',
    grateful:   'Gratitude showing up in your entries. Beneath the weight, there is something you\'re holding onto. That matters.',
    conflicted: 'Tension without resolution—but you\'re naming it. The war inside you is looking for words. You\'re finding them.',
    neutral:    'Steady. Building. This is the quiet between the meaningful moments.',
  };

  // ── Helpers ────────────────────────────────────────────────────
  function loadJSON(key, fallback) {
    try {
      return JSON.parse(localStorage.getItem(key)) || fallback;
    } catch (_) {
      return fallback;
    }
  }

  function saveJSON(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (_) { /* storage full / private mode */ }
  }

  function formatDate(ts) {
    return new Date(ts).toLocaleDateString('en-US', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
    });
  }

  function formatTime(ts) {
    return new Date(ts).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  }

  function escapeHTML(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // ── State ──────────────────────────────────────────────────────
  let journalEntries = loadJSON(KEY_JOURNAL, []);
  let dailyMoments   = loadJSON(KEY_DAILY,   []);

  // ── Mood analysis (simple frequency-based "AI") ────────────────
  function analyseMoods() {
    if (journalEntries.length === 0) return null;

    // Count moods over last 20 entries
    const recent = journalEntries.slice(-20);
    const counts = {};
    recent.forEach(e => {
      counts[e.mood] = (counts[e.mood] || 0) + 1;
    });

    const dominant = Object.entries(counts)
      .sort((a, b) => b[1] - a[1])[0][0];

    const percentage = Math.round((counts[dominant] / recent.length) * 100);
    return { dominant, counts, percentage, total: recent.length };
  }

  function buildInsightsHTML(analysis) {
    if (!analysis) return '';
    const { dominant, counts, percentage, total } = analysis;
    const insight = MOOD_INSIGHTS_MAP[dominant] || MOOD_INSIGHTS_MAP.neutral;
    const meta    = MOOD_META[dominant] || MOOD_META.neutral;

    const moodLines = Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .map(([mood, count]) => {
        const m = MOOD_META[mood] || MOOD_META.neutral;
        const pct = Math.round((count / total) * 100);
        return `<p><span style="color:${m.color}">${m.label}</span> — ${pct}% of recent entries</p>`;
      })
      .join('');

    return `
      <p style="color:${meta.color};font-style:italic;margin-bottom:1rem;">"${insight}"</p>
      <p style="margin-bottom:0.8rem;font-size:0.82rem;color:#6a6a7a;letter-spacing:0.05em;">PATTERNS IN LAST ${total} ENTRIES</p>
      ${moodLines}
    `;
  }

  function updateInsights() {
    const panel   = document.getElementById('mood-insights');
    const content = document.getElementById('insights-content');
    if (!panel || !content) return;

    const analysis = analyseMoods();
    if (!analysis || journalEntries.length < 3) {
      panel.classList.add('hidden');
      return;
    }

    content.innerHTML = buildInsightsHTML(analysis);
    panel.classList.remove('hidden');
  }

  // ── Mood display (current / last entry) ───────────────────────
  function updateMoodDisplay(mood) {
    const moodText = document.getElementById('mood-text');
    const moodFill = document.getElementById('mood-fill');
    if (!moodText || !moodFill) return;

    const meta = MOOD_META[mood] || MOOD_META.neutral;
    moodText.textContent  = meta.label;
    moodText.style.color  = meta.color;
    moodFill.style.width  = meta.intensity + '%';
    moodFill.style.background = meta.color;
  }

  // ── Render journal entries ─────────────────────────────────────
  function renderJournalEntries() {
    const container = document.getElementById('journal-entries');
    if (!container) return;

    if (journalEntries.length === 0) {
      container.innerHTML = '<p class="empty-state">No entries yet. Begin your journey above.</p>';
      return;
    }

    container.innerHTML = [...journalEntries]
      .reverse()
      .map(entry => {
        const meta  = MOOD_META[entry.mood] || MOOD_META.neutral;
        const title = entry.title ? escapeHTML(entry.title) : 'Untitled';
        const body  = escapeHTML(entry.content);
        return `
          <article class="journal-entry reveal" data-mood="${escapeHTML(entry.mood)}" data-id="${entry.id}">
            <div class="entry-header">
              <h3 class="entry-title-text">${title}</h3>
              <div class="entry-meta">
                <span class="entry-mood-badge" style="border-color:${meta.color};color:${meta.color}">${meta.label}</span>
                <time class="entry-timestamp" datetime="${new Date(entry.ts).toISOString()}">
                  ${formatDate(entry.ts)} · ${formatTime(entry.ts)}
                </time>
              </div>
            </div>
            <p class="entry-body">${body}</p>
            <button class="entry-delete-btn" data-id="${entry.id}" aria-label="Delete entry" title="Delete">✕</button>
          </article>`;
      })
      .join('');

    // Re-observe newly rendered entries
    observeReveal(container.querySelectorAll('.reveal'));
  }

  // ── Render daily moments ───────────────────────────────────────
  function renderDailyMoments() {
    const container = document.getElementById('daily-entries');
    if (!container) return;

    if (dailyMoments.length === 0) {
      container.innerHTML = '<p class="empty-state">No moments recorded yet. Add one below.</p>';
      return;
    }

    container.innerHTML = [...dailyMoments]
      .reverse()
      .slice(0, 12)   // show latest 12
      .map(m => `
        <div class="daily-entry reveal" data-id="${m.id}">
          <span class="entry-date">${formatDate(m.ts)}</span>
          <p>${escapeHTML(m.text)}</p>
          <button class="entry-delete" data-id="${m.id}" aria-label="Delete moment" title="Delete">✕</button>
        </div>`)
      .join('');

    observeReveal(container.querySelectorAll('.reveal'));
  }

  // ── Intersection observer for reveal animations ────────────────
  let observer;
  function observeReveal(elements) {
    if (!observer) {
      observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1 });
    }
    elements.forEach(el => observer.observe(el));
  }

  // ── Journal form submit ────────────────────────────────────────
  function initJournalForm() {
    const form    = document.getElementById('journal-form');
    const titleEl = document.getElementById('journal-title');
    const bodyEl  = document.getElementById('journal-content');
    const moodEl  = document.getElementById('mood-select');
    if (!form) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const content = bodyEl.value.trim();
      if (!content) return;

      const entry = {
        id:      Date.now(),
        ts:      Date.now(),
        title:   titleEl.value.trim(),
        content,
        mood:    moodEl.value,
      };

      journalEntries.push(entry);
      saveJSON(KEY_JOURNAL, journalEntries);

      // Update mood-driven visuals
      applyMoodToPage(entry.mood);
      updateMoodDisplay(entry.mood);
      updateInsights();
      renderJournalEntries();

      // Reset form
      titleEl.value = '';
      bodyEl.value  = '';
      moodEl.value  = 'neutral';

      // Scroll to entries
      document.getElementById('journal-entries')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });

    // Delete buttons (event delegation)
    const container = document.getElementById('journal-entries');
    if (container) {
      container.addEventListener('click', (e) => {
        const btn = e.target.closest('.entry-delete-btn');
        if (!btn) return;
        const id = Number(btn.dataset.id);
        journalEntries = journalEntries.filter(en => en.id !== id);
        saveJSON(KEY_JOURNAL, journalEntries);
        updateInsights();
        renderJournalEntries();
        // Recalculate dominant mood
        const last = journalEntries[journalEntries.length - 1];
        if (last) { applyMoodToPage(last.mood); updateMoodDisplay(last.mood); }
        else       { applyMoodToPage('neutral'); updateMoodDisplay('neutral'); }
      });
    }
  }

  // ── Daily form submit ──────────────────────────────────────────
  function initDailyForm() {
    const form  = document.getElementById('daily-form');
    const input = document.getElementById('daily-input');
    if (!form) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;

      dailyMoments.push({ id: Date.now(), ts: Date.now(), text });
      saveJSON(KEY_DAILY, dailyMoments);
      renderDailyMoments();
      input.value = '';
    });

    // Delete buttons
    const container = document.getElementById('daily-entries');
    if (container) {
      container.addEventListener('click', (e) => {
        const btn = e.target.closest('.entry-delete');
        if (!btn) return;
        const id = Number(btn.dataset.id);
        dailyMoments = dailyMoments.filter(m => m.id !== id);
        saveJSON(KEY_DAILY, dailyMoments);
        renderDailyMoments();
      });
    }
  }

  // ── Apply mood to page ─────────────────────────────────────────
  // (also called from app.js — exposed on window)
  function applyMoodToPage(mood) {
    document.body.setAttribute('data-mood', mood || 'neutral');
  }
  window.JourneyMood = { apply: applyMoodToPage };

  // ── Init ───────────────────────────────────────────────────────
  function init() {
    renderJournalEntries();
    renderDailyMoments();
    initJournalForm();
    initDailyForm();
    updateInsights();

    // Restore mood from last journal entry
    const last = journalEntries[journalEntries.length - 1];
    if (last) {
      applyMoodToPage(last.mood);
      updateMoodDisplay(last.mood);
    } else {
      updateMoodDisplay('neutral');
    }

    // Observe already-rendered reveal elements
    document.querySelectorAll('.reveal').forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight) el.classList.add('visible');
    });
    observeReveal(document.querySelectorAll('.reveal:not(.visible)'));
  }

  // Run after DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

}());
