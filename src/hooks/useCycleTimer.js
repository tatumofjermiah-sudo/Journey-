import { useState, useEffect } from 'react';

export function useCycleTimer(activeCycle, levelHours) {
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    if (!activeCycle) return;
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, [activeCycle]);

  const elapsed = activeCycle ? Math.floor((now - activeCycle.startedAt) / 1000) : 0;
  const totalSeconds = levelHours * 3600;
  const progress = totalSeconds > 0 ? Math.min(elapsed / totalSeconds, 1) : 0;
  const remaining = Math.max(totalSeconds - elapsed, 0);

  return { elapsed, progress, remaining };
}

export function formatDuration(seconds) {
  if (seconds <= 0) return '0h 0m 0s';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}h ${m}m ${s}s`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}
