export const LEVELS = [
  {
    id: '12h',
    hours: 12,
    label: '12',
    name: 'Foundation District',
    color: '#4ade80',
    darkColor: '#166534',
    glowColor: 'rgba(74, 222, 128, 0.4)',
    description: 'First proof of control.',
    gridX: 0,
    gridY: 0,
  },
  {
    id: '24h',
    hours: 24,
    label: '24',
    name: 'Control District',
    color: '#60a5fa',
    darkColor: '#1e3a5f',
    glowColor: 'rgba(96, 165, 250, 0.4)',
    description: 'A full cycle of time.',
    gridX: 1,
    gridY: 0,
  },
  {
    id: '48h',
    hours: 48,
    label: '48',
    name: 'Endurance District',
    color: '#f59e0b',
    darkColor: '#78350f',
    glowColor: 'rgba(245, 158, 11, 0.4)',
    description: 'Where most stop. You return.',
    gridX: 2,
    gridY: 0,
  },
  {
    id: '72h',
    hours: 72,
    label: '72',
    name: 'Threshold District',
    color: '#c084fc',
    darkColor: '#4c1d95',
    glowColor: 'rgba(192, 132, 252, 0.4)',
    description: 'Beyond comfort. Into territory.',
    gridX: 3,
    gridY: 0,
  },
  {
    id: '144h',
    hours: 144,
    label: '144',
    name: 'Apex District',
    color: '#f87171',
    darkColor: '#7f1d1d',
    glowColor: 'rgba(248, 113, 113, 0.4)',
    description: 'The peak. The seal of dominion.',
    gridX: 4,
    gridY: 0,
  },
];

export const PROGRESSION_THRESHOLDS = {
  THIRD_GATE: 3,
  SIXTH_PATH: 6,
  NINTH_SEAL: 9,
};

export function getProgressionStage(cycles) {
  if (cycles >= PROGRESSION_THRESHOLDS.NINTH_SEAL) return 'ninth-seal';
  if (cycles >= PROGRESSION_THRESHOLDS.SIXTH_PATH) return 'sixth-path';
  if (cycles >= PROGRESSION_THRESHOLDS.THIRD_GATE) return 'third-gate';
  if (cycles >= 1) return 'unproven';
  return 'empty';
}

export function getProgressionLabel(cycles) {
  if (cycles >= PROGRESSION_THRESHOLDS.NINTH_SEAL) return 'Ninth Seal';
  if (cycles >= PROGRESSION_THRESHOLDS.SIXTH_PATH) return 'Sixth Path';
  if (cycles >= PROGRESSION_THRESHOLDS.THIRD_GATE) return 'Third Gate';
  if (cycles >= 1) return 'Unproven';
  return null;
}

export function getIdentityTitle(levelId, cycles) {
  const label = getProgressionLabel(cycles);
  const level = LEVELS.find((l) => l.id === levelId);
  if (!label || !level) return null;
  return `${label} of ${level.label}`;
}
