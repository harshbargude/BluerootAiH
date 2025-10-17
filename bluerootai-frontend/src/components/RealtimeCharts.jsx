import React, { useEffect, useMemo, useRef, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';
import { getSensors } from '../api/client';

const HISTORY_LIMIT = 300; // about 10 minutes @ 2s polling

function formatTime(ts) {
  const d = new Date(ts);
  return d.toLocaleTimeString();
}

export default function RealtimeCharts({ pollMs = 2000 }) {
  const [history, setHistory] = useState([]);
  const timerRef = useRef(null);

  useEffect(() => {
    let cancelled = false;
    async function tick() {
      try {
        const s = await getSensors();
        if (cancelled) return;
        const point = {
          ts: Date.now(),
          ph: s.ph ?? null,
          tds: s.tds ?? null,
          turb: s.turb ?? null,
          temp: s.temp ?? null,
        };
        setHistory(prev => {
          const next = [...prev, point];
          if (next.length > HISTORY_LIMIT) next.shift();
          return next;
        });
      } catch (_) {
        // ignore transient errors
      }
    }
    // immediate fetch then interval
    tick();
    timerRef.current = setInterval(tick, pollMs);
    return () => {
      cancelled = true;
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [pollMs]);

  const data = useMemo(
    () => history.map(p => ({
      time: formatTime(p.ts),
      ph: p.ph,
      tds: p.tds,
      turbidity: p.turb,
      temperature: p.temp,
    })),
    [history]
  );

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <ChartCard title="pH" yLabel="pH" dataKey="ph" data={data} stroke="#3b82f6" />
      <ChartCard title="TDS" yLabel="ppm" dataKey="tds" data={data} stroke="#22c55e" />
      <ChartCard title="Turbidity" yLabel="NTU" dataKey="turbidity" data={data} stroke="#f59e0b" />
      <ChartCard title="Temperature" yLabel="°C" dataKey="temperature" data={data} stroke="#ef4444" />
    </div>
  );
}

function ChartCard({ title, yLabel, dataKey, data, stroke }) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 shadow-sm bg-white">
      <div className="mb-2 font-semibold">{title}</div>
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 16, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" minTickGap={24} />
            <YAxis width={48} domain={['auto', 'auto']} label={{ value: yLabel, angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dot={false} isAnimationActive={false} dataKey={dataKey} stroke={stroke} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}


