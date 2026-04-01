import { useMemo } from 'react';
import { LEVELS } from '../constants/levels';
import DistrictTile from './DistrictTile';

export default function IsometricMap({ districts, activeCycle, lastMaterialized, onDistrictClick }) {
  const totalCycles = useMemo(
    () => Object.values(districts).reduce((s, d) => s + d.completedCycles, 0),
    [districts]
  );

  return (
    <div className="relative w-full flex flex-col items-center">
      {/* World title */}
      <div className="mb-6 text-center">
        <div className="text-xs font-mono tracking-[0.3em] uppercase text-gray-500 mb-1">The Cycle Map</div>
        <div className="text-xs font-mono text-gray-600">
          {totalCycles === 0
            ? 'Your territory awaits. Complete a cycle to begin.'
            : `${totalCycles} cycle${totalCycles !== 1 ? 's' : ''} forged into the world.`}
        </div>
      </div>

      {/* District grid — isometric-inspired row with stagger */}
      <div className="flex flex-wrap justify-center gap-4 px-4">
        {LEVELS.map((level, i) => {
          const districtState = districts[level.id] ?? { completedCycles: 0 };
          const isActive = activeCycle?.levelId === level.id;
          const isLast = lastMaterialized === level.id;
          return (
            <div
              key={level.id}
              style={{
                marginTop: i % 2 === 1 ? '28px' : '0px',
                transition: 'margin 0.3s',
              }}
            >
              <DistrictTile
                level={level}
                completedCycles={districtState.completedCycles}
                isActive={isActive}
                isLastMaterialized={isLast}
                onClick={onDistrictClick}
              />
            </div>
          );
        })}
      </div>

      {/* Connection lines between districts (decorative) */}
      <div className="mt-4 w-full max-w-3xl flex items-center justify-center gap-2 px-8 opacity-20">
        {LEVELS.map((level, i) => (
          <div key={level.id} className="flex items-center gap-2 flex-1">
            <div className="h-px flex-1" style={{ background: level.color }} />
            {i < LEVELS.length - 1 && (
              <div className="w-1 h-1 rounded-full" style={{ background: level.color }} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
