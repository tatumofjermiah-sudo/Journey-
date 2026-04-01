import { useCycleTimer, formatDuration } from '../hooks/useCycleTimer';
import { LEVELS } from '../constants/levels';

export default function ActiveCyclePanel({ activeCycle, onComplete, onAbandon }) {
  const level = activeCycle ? LEVELS.find((l) => l.id === activeCycle.levelId) : null;
  const { progress, remaining, elapsed } = useCycleTimer(activeCycle, level?.hours ?? 0);

  if (!activeCycle || !level) return null;

  const pct = Math.round(progress * 100);
  const isComplete = progress >= 1;

  return (
    <div
      className="fixed bottom-0 left-0 right-0 z-50 p-4 border-t"
      style={{
        background: `linear-gradient(0deg, #0a0c14 0%, #0f1117ee 100%)`,
        borderColor: `${level.color}44`,
      }}
    >
      <div className="max-w-2xl mx-auto">
        {/* Level info */}
        <div className="flex items-center justify-between mb-2">
          <div>
            <span className="text-sm font-mono font-bold" style={{ color: level.color }}>
              {level.hours}h Cycle
            </span>
            <span className="text-xs font-mono ml-2 text-gray-500">{level.name}</span>
          </div>
          <div className="text-right">
            {isComplete ? (
              <span className="text-sm font-mono font-bold text-white animate-pulse-glow">
                COMPLETE — LOCK IT IN
              </span>
            ) : (
              <span className="text-sm font-mono" style={{ color: level.color }}>
                {formatDuration(remaining)} remaining
              </span>
            )}
          </div>
        </div>

        {/* Progress bar */}
        <div className="h-2 w-full rounded-full overflow-hidden mb-3" style={{ background: `${level.darkColor}88` }}>
          <div
            className="h-full rounded-full transition-all duration-1000"
            style={{
              width: `${pct}%`,
              background: isComplete
                ? `linear-gradient(90deg, ${level.color}, #fff)`
                : level.color,
              boxShadow: `0 0 8px ${level.glowColor}`,
            }}
          />
        </div>

        {/* Elapsed */}
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-mono text-gray-500">
            Elapsed: {formatDuration(elapsed)}
          </span>
          <span className="text-xs font-mono" style={{ color: level.color, opacity: 0.6 }}>
            {pct}% complete
          </span>
        </div>

        {/* Action buttons */}
        <div className="flex gap-3">
          <button
            onClick={onComplete}
            className={`flex-1 py-2 px-4 rounded-lg font-mono text-sm font-bold border transition-all duration-200 ${
              isComplete
                ? 'opacity-100 hover:scale-105'
                : 'opacity-50 cursor-not-allowed'
            }`}
            style={{
              color: isComplete ? '#000' : level.color,
              background: isComplete ? level.color : 'transparent',
              borderColor: level.color,
            }}
            disabled={!isComplete}
          >
            {isComplete ? 'COMPLETE CYCLE' : 'Cycle In Progress…'}
          </button>
          <button
            onClick={onAbandon}
            className="py-2 px-4 rounded-lg font-mono text-sm border border-gray-700 text-gray-500 hover:text-gray-300 hover:border-gray-500 transition-all duration-200"
          >
            Abandon
          </button>
        </div>

        {/* Flavor */}
        <div className="mt-2 text-center text-xs font-mono text-gray-700 italic">
          {isComplete
            ? 'The structure is ready. Claim it.'
            : 'Hold. The world is watching you repeat.'}
        </div>
      </div>
    </div>
  );
}
