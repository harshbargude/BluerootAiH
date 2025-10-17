import React, { useEffect, useState } from 'react';
import { getControlState, setPump, setValve } from '../api/client';

export default function Controls() {
  const [pump, setPumpState] = useState(false);
  const [valve, setValveState] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const s = await getControlState();
        if (!cancelled) {
          setPumpState(Boolean(s.pump));
          setValveState(Boolean(s.valve));
        }
      } catch (_) {}
    })();
    return () => { cancelled = true; };
  }, []);

  async function togglePump() {
    setLoading(true);
    try {
      const res = await setPump(!pump);
      setPumpState(Boolean(res.pump));
    } catch (_) {}
    setLoading(false);
  }

  async function toggleValve() {
    setLoading(true);
    try {
      const res = await setValve(!valve);
      setValveState(Boolean(res.valve));
    } catch (_) {}
    setLoading(false);
  }

  return (
    <div className="rounded-lg border border-gray-200 p-4 shadow-sm bg-white flex gap-4 items-center justify-between">
      <div>
        <div className="font-semibold">Controls</div>
        <div className="text-sm text-gray-600">Pump and valve</div>
      </div>
      <div className="flex gap-3">
        <button onClick={togglePump} disabled={loading} className={`px-3 py-2 rounded text-white ${pump ? 'bg-green-600' : 'bg-gray-600'}`}>
          Pump: {pump ? 'ON' : 'OFF'}
        </button>
        <button onClick={toggleValve} disabled={loading} className={`px-3 py-2 rounded text-white ${valve ? 'bg-blue-600' : 'bg-gray-600'}`}>
          Valve: {valve ? 'OPEN' : 'CLOSED'}
        </button>
      </div>
    </div>
  );
}


