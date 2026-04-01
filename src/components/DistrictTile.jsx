import { useMemo } from 'react';
import { getProgressionStage, getProgressionLabel, PROGRESSION_THRESHOLDS } from '../constants/levels';

// Isometric building shapes rendered as SVG
function IsoBuilding({ stage, color, darkColor, glowColor, isActive, levelLabel }) {
  const w = 120;
  const h = 120;

  if (stage === 'empty') {
    return (
      <svg width={w} height={h} viewBox="0 0 120 120" className="opacity-20">
        {/* Empty fog ground tile */}
        <polygon points="60,30 100,50 60,70 20,50" fill="#1a1f2e" stroke="#2a2f3e" strokeWidth="1" />
      </svg>
    );
  }

  if (stage === 'unproven') {
    return (
      <svg width={w} height={h} viewBox="0 0 120 120" className="animate-flicker">
        {/* Ground tile */}
        <polygon points="60,40 100,60 60,80 20,60" fill={darkColor} stroke={color} strokeWidth="0.5" opacity="0.5" />
        {/* Faint pillar */}
        <rect x="52" y="20" width="16" height="30" fill={color} opacity="0.25" />
        <polygon points="52,20 68,20 76,14 60,10 44,14" fill={color} opacity="0.2" />
        {/* Ground sides */}
        <polygon points="20,60 60,80 60,90 20,70" fill={darkColor} opacity="0.4" />
        <polygon points="100,60 60,80 60,90 100,70" fill={darkColor} opacity="0.3" />
      </svg>
    );
  }

  if (stage === 'third-gate') {
    return (
      <svg width={w} height={h} viewBox="0 0 120 120" className={isActive ? 'animate-pulse-glow' : 'animate-materialize'}>
        {/* Ground tile */}
        <polygon points="60,50 100,68 60,86 20,68" fill={darkColor} stroke={color} strokeWidth="1" />
        <polygon points="20,68 60,86 60,96 20,78" fill={darkColor} opacity="0.7" />
        <polygon points="100,68 60,86 60,96 100,78" fill={darkColor} opacity="0.5" />
        {/* Gate arch */}
        <rect x="48" y="20" width="10" height="38" fill={color} opacity="0.8" />
        <rect x="62" y="20" width="10" height="38" fill={color} opacity="0.8" />
        <rect x="44" y="18" width="32" height="8" fill={color} opacity="0.9" />
        {/* Glow */}
        <ellipse cx="60" cy="68" rx="30" ry="8" fill={glowColor} opacity="0.4" />
        {/* Label */}
        <text x="60" y="74" textAnchor="middle" fill={color} fontSize="8" fontFamily="monospace" opacity="0.9">
          {levelLabel}h · GATE
        </text>
      </svg>
    );
  }

  if (stage === 'sixth-path') {
    return (
      <svg width={w} height={h} viewBox="0 0 120 120" className={isActive ? 'animate-pulse-glow' : ''}>
        {/* Expanded ground */}
        <polygon points="60,44 104,65 60,86 16,65" fill={darkColor} stroke={color} strokeWidth="1" />
        <polygon points="16,65 60,86 60,98 16,77" fill={darkColor} opacity="0.7" />
        <polygon points="104,65 60,86 60,98 104,77" fill={darkColor} opacity="0.5" />
        {/* Path lines from gate */}
        <line x1="16" y1="65" x2="60" y2="65" stroke={color} strokeWidth="1.5" opacity="0.5" strokeDasharray="4 2" />
        <line x1="104" y1="65" x2="60" y2="65" stroke={color} strokeWidth="1.5" opacity="0.5" strokeDasharray="4 2" />
        {/* Tower */}
        <rect x="46" y="14" width="28" height="42" fill={darkColor} stroke={color} strokeWidth="1" />
        <rect x="50" y="18" width="8" height="12" fill={color} opacity="0.5" />
        <rect x="62" y="18" width="8" height="12" fill={color} opacity="0.5" />
        {/* Roof / top */}
        <polygon points="46,14 74,14 60,4" fill={color} opacity="0.8" />
        {/* Glow */}
        <ellipse cx="60" cy="65" rx="36" ry="10" fill={glowColor} opacity="0.35" />
        <text x="60" y="71" textAnchor="middle" fill={color} fontSize="8" fontFamily="monospace" opacity="0.9">
          {levelLabel}h · PATH
        </text>
      </svg>
    );
  }

  // ninth-seal
  return (
    <svg width={w} height={h} viewBox="0 0 120 120">
      {/* Full domain ground */}
      <polygon points="60,40 108,63 60,86 12,63" fill={darkColor} stroke={color} strokeWidth="1.5" />
      <polygon points="12,63 60,86 60,100 12,77" fill={darkColor} opacity="0.8" />
      <polygon points="108,63 60,86 60,100 108,77" fill={darkColor} opacity="0.6" />
      {/* Roads out */}
      <line x1="12" y1="63" x2="0" y2="63" stroke={color} strokeWidth="2" opacity="0.6" />
      <line x1="108" y1="63" x2="120" y2="63" stroke={color} strokeWidth="2" opacity="0.6" />
      {/* Grand fortress */}
      <rect x="42" y="8" width="36" height="48" fill={darkColor} stroke={color} strokeWidth="1.5" />
      {/* Corner towers */}
      <rect x="38" y="12" width="10" height="16" fill={darkColor} stroke={color} strokeWidth="1" />
      <rect x="72" y="12" width="10" height="16" fill={darkColor} stroke={color} strokeWidth="1" />
      {/* Windows */}
      <rect x="52" y="16" width="7" height="9" fill={color} opacity="0.6" />
      <rect x="61" y="16" width="7" height="9" fill={color} opacity="0.6" />
      <rect x="48" y="30" width="5" height="7" fill={color} opacity="0.5" />
      <rect x="67" y="30" width="5" height="7" fill={color} opacity="0.5" />
      {/* Gate door */}
      <rect x="54" y="44" width="12" height="12" fill={color} opacity="0.7" rx="2" />
      {/* Crown at top */}
      <polygon points="42,8 52,2 60,8 68,2 78,8" fill={color} opacity="0.9" />
      {/* Seal glow */}
      <ellipse cx="60" cy="63" rx="42" ry="12" fill={glowColor} opacity="0.45" />
      <text x="60" y="70" textAnchor="middle" fill={color} fontSize="8" fontFamily="monospace" fontWeight="bold">
        {levelLabel}h · SEAL
      </text>
    </svg>
  );
}

export default function DistrictTile({ level, completedCycles, isActive, isLastMaterialized, onClick }) {
  const stage = useMemo(() => getProgressionStage(completedCycles), [completedCycles]);
  const progressLabel = getProgressionLabel(completedCycles);
  const nextThreshold = useMemo(() => {
    if (completedCycles < PROGRESSION_THRESHOLDS.THIRD_GATE) return PROGRESSION_THRESHOLDS.THIRD_GATE;
    if (completedCycles < PROGRESSION_THRESHOLDS.SIXTH_PATH) return PROGRESSION_THRESHOLDS.SIXTH_PATH;
    if (completedCycles < PROGRESSION_THRESHOLDS.NINTH_SEAL) return PROGRESSION_THRESHOLDS.NINTH_SEAL;
    return null;
  }, [completedCycles]);

  const fogOpacity = stage === 'empty' ? 0.85 : stage === 'unproven' ? 0.4 : 0;

  return (
    <div
      className={`relative flex flex-col items-center cursor-pointer select-none group`}
      onClick={() => onClick(level.id)}
    >
      {/* Fog overlay */}
      {fogOpacity > 0 && (
        <div
          className="absolute inset-0 z-10 pointer-events-none rounded-lg transition-all duration-700"
          style={{ background: `rgba(10,12,20,${fogOpacity})` }}
        />
      )}

      {/* Active cycle pulse ring */}
      {isActive && (
        <div
          className="absolute inset-0 z-20 rounded-lg pointer-events-none animate-pulse-glow"
          style={{ boxShadow: `0 0 30px 8px ${level.glowColor}` }}
        />
      )}

      {/* District card */}
      <div
        className={`
          relative z-5 flex flex-col items-center p-3 rounded-xl border transition-all duration-300
          ${isActive ? 'border-opacity-100 shadow-lg' : 'border-opacity-30 hover:border-opacity-70'}
          ${stage === 'ninth-seal' ? 'scale-105' : ''}
          ${isLastMaterialized ? 'animate-materialize' : ''}
        `}
        style={{
          borderColor: level.color,
          background: `linear-gradient(135deg, #0f1117 0%, ${level.darkColor}88 100%)`,
          minWidth: '140px',
        }}
      >
        {/* District name */}
        <div className="text-xs font-mono mb-1 tracking-wider" style={{ color: level.color }}>
          {level.name}
        </div>

        {/* Isometric building */}
        <div className="relative">
          <IsoBuilding
            stage={stage}
            color={level.color}
            darkColor={level.darkColor}
            glowColor={level.glowColor}
            isActive={isActive}
            levelLabel={level.label}
          />
        </div>

        {/* Cycle count */}
        <div className="mt-1 text-center">
          <span className="text-2xl font-bold font-mono" style={{ color: level.color }}>
            {completedCycles}
          </span>
          <span className="text-xs font-mono ml-1" style={{ color: level.color, opacity: 0.6 }}>
            cycles
          </span>
        </div>

        {/* Progression label */}
        {progressLabel && (
          <div
            className="mt-1 text-xs font-mono tracking-widest uppercase px-2 py-0.5 rounded"
            style={{ color: level.color, background: `${level.darkColor}99`, border: `1px solid ${level.color}44` }}
          >
            {progressLabel}
          </div>
        )}

        {/* Next threshold indicator */}
        {nextThreshold && (
          <div className="mt-2 w-full">
            <div className="h-1 rounded-full overflow-hidden" style={{ background: `${level.darkColor}` }}>
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{
                  width: `${(completedCycles / nextThreshold) * 100}%`,
                  background: level.color,
                }}
              />
            </div>
            <div className="text-xs font-mono mt-0.5 text-center" style={{ color: level.color, opacity: 0.5 }}>
              {completedCycles}/{nextThreshold} → next seal
            </div>
          </div>
        )}

        {/* Active indicator */}
        {isActive && (
          <div
            className="mt-2 text-xs font-mono tracking-widest px-2 py-0.5 rounded animate-pulse-glow"
            style={{ color: '#000', background: level.color }}
          >
            ACTIVE
          </div>
        )}
      </div>
    </div>
  );
}
