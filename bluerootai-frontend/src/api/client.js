// Lightweight API client for Flask backend
import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:5000';

export const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

export async function getSensors() {
  const { data } = await api.get('/api/sensors');
  // Fallback: if temp is null in aggregated endpoint, try dedicated temperature endpoint
  if (data && (data.temp === null || typeof data.temp === 'undefined')) {
    try {
      const t = await api.get('/api/temperature');
      if (t?.data && typeof t.data.temperature === 'number') {
        return { ...data, temp: t.data.temperature };
      }
    } catch (_) {
      // swallow and return original data
    }
  }
git  // Fallback: if any other sensor missing, fetch dedicated endpoints
  const result = { ...data };
  try {
    if (result.ph === null || typeof result.ph === 'undefined') {
      const r = await api.get('/api/ph');
      if (r?.data && typeof r.data.ph === 'number') result.ph = r.data.ph;
    }
  } catch (_) {}
  try {
    if (result.tds === null || typeof result.tds === 'undefined') {
      const r = await api.get('/api/tds');
      if (r?.data && typeof r.data.tds === 'number') result.tds = r.data.tds;
    }
  } catch (_) {}
  try {
    // backend uses key 'turb' in state; dedicated endpoint returns 'turbidity'
    if (result.turb === null || typeof result.turb === 'undefined') {
      const r = await api.get('/api/turbidity');
      if (r?.data && typeof r.data.turbidity === 'number') result.turb = r.data.turbidity;
    }
  } catch (_) {}
  return result;
}

export async function getControlState() {
  const { data } = await api.get('/api/control/state');
  return data;
}

export async function setPump(on) {
  const { data } = await api.post('/api/control/pump', { on: Boolean(on) });
  return data;
}

export async function setValve(on) {
  const { data } = await api.post('/api/control/valve', { on: Boolean(on) });
  return data;
}


