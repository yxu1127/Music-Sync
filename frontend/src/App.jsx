import { useState, useEffect, useCallback } from 'react';
import DecorativeBg from './components/DecorativeBg';
import Sidebar from './components/Sidebar';
import PlaylistGrid from './components/PlaylistGrid';
import ListView from './components/ListView';
import ViewToggle from './components/ViewToggle';
import UrlInput from './components/UrlInput';
import SyncProgress from './components/SyncProgress';
import { fetchPlaylists, triggerSync, fetchSyncStatus, togglePlaylistPause, removePlaylist } from './api';
import './App.css';

export default function App() {
  const [view, setView] = useState('playlist');
  const [playlists, setPlaylists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    fetchPlaylists()
      .then(setPlaylists)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!syncing) return;
    const interval = setInterval(async () => {
      try {
        const status = await fetchSyncStatus();
        if (!status.running) {
          setSyncing(false);
          setRefreshTrigger((r) => r + 1);
          fetchPlaylists().then(setPlaylists).catch(() => {});
        }
      } catch {
        // ignore
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [syncing]);

  const handleSyncComplete = useCallback(() => {
    setRefreshTrigger((r) => r + 1);
    fetchPlaylists().then(setPlaylists).catch(() => {});
  }, []);

  const startSync = useCallback((playlistId = null) => {
    setSyncing(true);
    triggerSync(playlistId).catch(() => {});
  }, []);

  const handleSyncPlaylist = (playlistId) => {
    startSync(playlistId);
  };

  const handleTogglePause = async (playlistId, paused) => {
    await togglePlaylistPause(playlistId, paused);
    await fetchPlaylists().then(setPlaylists).catch(() => {});
  };

  const handleRemovePlaylist = async (playlistId) => {
    await removePlaylist(playlistId);
    await fetchPlaylists().then(setPlaylists).catch(() => {});
  };

  return (
    <>
      <DecorativeBg />
      <div className="app-container">
        <Sidebar onSyncStart={() => startSync()} onSyncing={syncing} />
        <main className="main-content">
          <div className="top-bar">
            <div className="top-bar-left">
              <UrlInput
                onPlaylistAdded={(added) => {
                  fetchPlaylists().then(setPlaylists);
                  startSync(added.id);
                }}
              />
            </div>
            <div className="top-bar-row">
              <ViewToggle view={view} onViewChange={setView} />
            </div>
          </div>

          <SyncProgress syncing={syncing} />

          {error && (
            <div className="app-error-block">
              <p className="app-error">{error}</p>
              <p className="app-error-hint">Start the server: <code>./run.sh</code> or <code>python api.py</code></p>
              <button type="button" className="app-retry-btn" onClick={() => { setError(null); setLoading(true); fetchPlaylists().then(setPlaylists).catch((e) => setError(e.message)).finally(() => setLoading(false)); }}>
                Retry
              </button>
            </div>
          )}
          {loading && !error && <p className="app-loading">Loading…</p>}

          <div className="view-container">
            <div className={`view-section ${view === 'playlist' ? 'active' : ''}`} id="view-playlist">
              <PlaylistGrid
                playlists={playlists}
                onSyncPlaylist={handleSyncPlaylist}
                onTogglePause={handleTogglePause}
                onRemovePlaylist={handleRemovePlaylist}
              />
            </div>
            <div className={`view-section ${view === 'list' ? 'active' : ''}`} id="view-list">
              <ListView refreshTrigger={refreshTrigger} syncing={syncing} />
            </div>
          </div>
        </main>
      </div>
    </>
  );
}
