import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'journey-state-v1';

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    // Ignore parse/read errors and return null to fall back to initial state
    return null;
  }
}

function saveState(state) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Ignore write errors (e.g., storage quota exceeded or private browsing)
  }
}

function buildInitialState() {
  return {
    // map of levelId -> { completedCycles: number }
    districts: {
      '12h': { completedCycles: 0 },
      '24h': { completedCycles: 0 },
      '48h': { completedCycles: 0 },
      '72h': { completedCycles: 0 },
      '144h': { completedCycles: 0 },
    },
    // active cycle info or null
    activeCycle: null,
    // last materialized district (for animation)
    lastMaterialized: null,
  };
}

export function useCycleStore() {
  const [state, setState] = useState(() => {
    const saved = loadState();
    return saved || buildInitialState();
  });

  useEffect(() => {
    saveState(state);
  }, [state]);

  const startCycle = useCallback((levelId) => {
    setState((prev) => ({
      ...prev,
      activeCycle: {
        levelId,
        startedAt: Date.now(),
      },
      lastMaterialized: null,
    }));
  }, []);

  const completeCycle = useCallback((levelId) => {
    setState((prev) => {
      const current = prev.districts[levelId]?.completedCycles ?? 0;
      return {
        ...prev,
        activeCycle: null,
        lastMaterialized: levelId,
        districts: {
          ...prev.districts,
          [levelId]: { completedCycles: current + 1 },
        },
      };
    });
  }, []);

  const abandonCycle = useCallback(() => {
    setState((prev) => ({ ...prev, activeCycle: null }));
  }, []);

  const resetDistrict = useCallback((levelId) => {
    setState((prev) => ({
      ...prev,
      districts: {
        ...prev.districts,
        [levelId]: { completedCycles: 0 },
      },
    }));
  }, []);

  return {
    districts: state.districts,
    activeCycle: state.activeCycle,
    lastMaterialized: state.lastMaterialized,
    startCycle,
    completeCycle,
    abandonCycle,
    resetDistrict,
  };
}
