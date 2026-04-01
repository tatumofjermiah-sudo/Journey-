import { useMemo } from 'react';
import { LEVELS, getIdentityTitle } from '../constants/levels';

export default function IdentityPanel({ districts }) {
  const identities = useMemo(() => {
    return LEVELS.map((level) => {
      const cycles = districts[level.id]?.completedCycles ?? 0;
      const title = getIdentityTitle(level.id, cycles);
      return { level, cycles, title };
    }).filter((e) => e.title);
  }, [districts]);

  const highestSeal = useMemo(() => {
    return identities.reduce((best, curr) => {
      if (!best) return curr;
      if (curr.cycles > best.cycles) return curr;
      return best;
    }, null);
  }, [identities]);

  if (identities.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-xs font-mono text-gray-600 tracking-widest uppercase">Identity</div>
        <div className="mt-2 text-sm font-mono text-gray-700 italic">
          Complete 3 cycles of any level to receive your first seal.
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 py-4">
      <div className="text-xs font-mono text-gray-500 tracking-[0.3em] uppercase mb-4 text-center">
        Your Identity
      </div>

      {/* Primary identity — highest seal */}
      {highestSeal && (
        <div
          className="mb-4 p-4 rounded-xl border text-center"
          style={{
            borderColor: highestSeal.level.color,
            background: `linear-gradient(135deg, #0f1117 0%, ${highestSeal.level.darkColor}66 100%)`,
            boxShadow: `0 0 20px ${highestSeal.level.glowColor}`,
          }}
        >
          <div className="text-xs font-mono text-gray-500 mb-1 tracking-widest">Primary Seal</div>
          <div
            className="text-xl font-mono font-bold tracking-widest"
            style={{ color: highestSeal.level.color }}
          >
            I hold the {highestSeal.title}
          </div>
          <div className="text-xs font-mono mt-1 text-gray-500">
            {highestSeal.cycles} completed {highestSeal.level.hours}h cycles
          </div>
        </div>
      )}

      {/* All seals */}
      <div className="space-y-2">
        {identities.map(({ level, cycles, title }) => (
          <div
            key={level.id}
            className="flex items-center justify-between px-3 py-2 rounded-lg border"
            style={{
              borderColor: `${level.color}44`,
              background: `${level.darkColor}33`,
            }}
          >
            <span className="font-mono text-sm font-bold" style={{ color: level.color }}>
              {title}
            </span>
            <span className="font-mono text-xs text-gray-600">{cycles} cycles</span>
          </div>
        ))}
      </div>

      <div className="mt-4 text-center text-xs font-mono text-gray-700 italic">
        "The map is a mirror. What you complete becomes territory."
      </div>
    </div>
  );
}
