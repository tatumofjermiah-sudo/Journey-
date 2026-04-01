import { useState } from 'react';
import { LEVELS } from '../constants/levels';

export default function StartCycleModal({ onStart, onClose, disabledLevelId }) {
  const [selected, setSelected] = useState(null);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(0,0,0,0.85)' }}>
      <div
        className="w-full max-w-md rounded-2xl border p-6"
        style={{ background: '#0f1117', borderColor: '#2a2f3e' }}
      >
        <div className="mb-6 text-center">
          <div className="text-xs font-mono tracking-[0.3em] uppercase text-gray-500 mb-1">Choose Your Trial</div>
          <div className="text-sm font-mono text-gray-400">
            Select a duration. Complete it once. That is one cycle.
          </div>
        </div>

        <div className="space-y-3 mb-6">
          {LEVELS.map((level) => {
            const isDisabled = disabledLevelId === level.id;
            const isSelected = selected === level.id;
            return (
              <button
                key={level.id}
                onClick={() => !isDisabled && setSelected(level.id)}
                disabled={isDisabled}
                className={`w-full p-3 rounded-xl border text-left transition-all duration-200 ${
                  isDisabled ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer hover:scale-[1.01]'
                }`}
                style={{
                  borderColor: isSelected ? level.color : `${level.color}33`,
                  background: isSelected ? `${level.darkColor}66` : 'transparent',
                  boxShadow: isSelected ? `0 0 12px ${level.glowColor}` : 'none',
                }}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <span className="font-mono font-bold text-white">{level.hours}h</span>
                    <span className="font-mono text-sm ml-2" style={{ color: level.color }}>
                      {level.name}
                    </span>
                  </div>
                  <div className="text-xs font-mono text-gray-500">{level.description}</div>
                </div>
              </button>
            );
          })}
        </div>

        <div className="flex gap-3">
          <button
            onClick={() => selected && onStart(selected)}
            disabled={!selected}
            className="flex-1 py-2 px-4 rounded-lg font-mono font-bold text-sm transition-all duration-200"
            style={{
              background: selected ? LEVELS.find((l) => l.id === selected)?.color : '#2a2f3e',
              color: selected ? '#000' : '#555',
              cursor: selected ? 'pointer' : 'not-allowed',
            }}
          >
            Begin Cycle
          </button>
          <button
            onClick={onClose}
            className="py-2 px-4 rounded-lg font-mono text-sm border border-gray-700 text-gray-500 hover:text-gray-300 hover:border-gray-500 transition-all duration-200"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
