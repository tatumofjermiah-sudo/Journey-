import { useState } from 'react';
import { useCycleStore } from './store/cycleStore';
import IsometricMap from './components/IsometricMap';
import ActiveCyclePanel from './components/ActiveCyclePanel';
import StartCycleModal from './components/StartCycleModal';
import IdentityPanel from './components/IdentityPanel';
import './index.css';

export default function App() {
  const {
    districts,
    activeCycle,
    lastMaterialized,
    startCycle,
    completeCycle,
    abandonCycle,
  } = useCycleStore();

  const [showStartModal, setShowStartModal] = useState(false);
  const [showIdentity, setShowIdentity] = useState(false);

  function handleDistrictClick() {
    if (activeCycle) return;
    setShowStartModal(true);
  }

  function handleStart(levelId) {
    startCycle(levelId);
    setShowStartModal(false);
  }

  function handleComplete() {
    if (activeCycle) completeCycle(activeCycle.levelId);
  }

  return (
    <div
      className="min-h-screen flex flex-col"
      style={{ background: '#0a0c14', color: '#e2e8f0' }}
    >
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
        <div>
          <h1 className="text-lg font-mono font-bold tracking-[0.15em] text-white">JOURNEY</h1>
          <p className="text-xs font-mono text-gray-600 tracking-widest">A world built through cycles.</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowIdentity((v) => !v)}
            className="px-3 py-1.5 rounded-lg border border-gray-700 text-xs font-mono text-gray-400 hover:text-gray-200 hover:border-gray-500 transition-all"
          >
            {showIdentity ? 'Map' : 'Identity'}
          </button>
          {!activeCycle && (
            <button
              onClick={() => setShowStartModal(true)}
              className="px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all bg-white text-black hover:bg-gray-200"
            >
              + New Cycle
            </button>
          )}
        </div>
      </header>

      {/* System description */}
      <div className="px-6 py-3 border-b border-gray-900 bg-gray-950">
        <p className="text-xs font-mono text-gray-600 text-center leading-relaxed">
          Choose a duration. Complete it. That is one cycle.
          Repeat it. The world grows with every return.
          <span className="text-gray-700"> · 3–6–9 progression · Third Gate · Sixth Path · Ninth Seal</span>
        </p>
      </div>

      {/* Main content */}
      <main className={`flex-1 overflow-auto ${activeCycle ? 'pb-48' : 'pb-8'}`}>
        {showIdentity ? (
          <div className="max-w-md mx-auto mt-8">
            <IdentityPanel districts={districts} />
          </div>
        ) : (
          <div className="pt-8">
            <IsometricMap
              districts={districts}
              activeCycle={activeCycle}
              lastMaterialized={lastMaterialized}
              onDistrictClick={handleDistrictClick}
            />
          </div>
        )}
      </main>

      {/* Active cycle bottom bar */}
      {activeCycle && (
        <ActiveCyclePanel
          activeCycle={activeCycle}
          onComplete={handleComplete}
          onAbandon={abandonCycle}
        />
      )}

      {/* Start modal */}
      {showStartModal && (
        <StartCycleModal
          onStart={handleStart}
          onClose={() => setShowStartModal(false)}
          disabledLevelId={activeCycle?.levelId}
        />
      )}
    </div>
  );
}
