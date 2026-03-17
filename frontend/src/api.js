const API_BASE = '/api';

function fetchWithTimeout(url, options = {}, timeout = 15000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  return fetch(url, { ...options, signal: controller.signal })
    .finally(() => clearTimeout(id));
}

export async function removePlaylist(playlistId) {
  const res = await fetch(`${API_BASE}/playlists/${playlistId}`, { method: 'DELETE' });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to remove');
  }
}

export async function togglePlaylistPause(playlistId, paused) {
  const res = await fetch(`${API_BASE}/playlists/${playlistId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ paused }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to update');
  }
  return res.json();
}

export async function addPlaylist(urlOrId, name = null) {
  const body = urlOrId.includes('list=') || urlOrId.includes('youtube')
    ? { url: urlOrId }
    : { playlist_id: urlOrId };
  if (name) body.name = name;
  const res = await fetch(`${API_BASE}/playlists`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to add playlist');
  }
  return res.json();
}

export async function fetchPlaylists() {
  let res;
  try {
    res = await fetchWithTimeout(`${API_BASE}/playlists`);
  } catch (e) {
    if (e.name === 'AbortError') {
      throw new Error('Request timed out. Is the server running?');
    }
    throw new Error('Cannot connect to server. Start it with: ./run.sh');
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to fetch playlists (${res.status})`);
  }
  return res.json();
}

export async function updateSchedule(intervalMinutes) {
  const res = await fetch(`${API_BASE}/config/schedule`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ interval_minutes: intervalMinutes }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to update');
  }
  return res.json();
}

export async function updateFormat(format) {
  const res = await fetch(`${API_BASE}/config/format`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ format }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to update');
  }
  return res.json();
}

export async function fetchConfig() {
  const res = await fetch(`${API_BASE}/config`);
  if (!res.ok) throw new Error('Failed to fetch config');
  return res.json();
}

export async function fetchPendingTracks() {
  const res = await fetch(`${API_BASE}/tracks/pending`);
  if (!res.ok) throw new Error('Failed to fetch pending tracks');
  return res.json();
}

export async function fetchSyncStatus() {
  const res = await fetch(`${API_BASE}/sync/status`);
  if (!res.ok) throw new Error('Failed to fetch sync status');
  return res.json();
}

export async function fetchTracks(limit = 100) {
  const res = await fetch(`${API_BASE}/tracks?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch tracks');
  return res.json();
}

export async function triggerSync(playlistId = null) {
  const res = await fetch(`${API_BASE}/sync`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ playlist_id: playlistId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Sync failed');
  }
  return res.json();
}
