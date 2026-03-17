import { useState, useEffect, useCallback } from 'react';
import { fetchTracks, fetchPendingTracks, fetchSyncStatus } from '../api';

function shortName(name, max = 12) {
  return name.length > max ? name.slice(0, max) + '...' : name;
}

function formatDownloadedAt(iso) {
  if (!iso) return '—';
  try {
    // SQLite timestamps are UTC without timezone; treat as UTC for correct local conversion
    const utcStr = /[Z+-]\d{2}:?\d{2}$/.test(iso) ? iso : iso.replace(/\s/, 'T') + 'Z';
    const d = new Date(utcStr);
    return d.toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

export default function ListView({ refreshTrigger, syncing }) {
  const [downloaded, setDownloaded] = useState([]);
  const [pending, setPending] = useState([]);
  const [syncStatus, setSyncStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = useCallback(async () => {
    try {
      const tracks = await fetchTracks();
      setDownloaded(tracks);
      try {
        const pendingTracks = await fetchPendingTracks();
        setPending(pendingTracks);
      } catch {
        setPending([]);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setLoading(true);
    loadData();
  }, [refreshTrigger, loadData]);

  useEffect(() => {
    if (!syncing) return;
    const interval = setInterval(async () => {
      try {
        const status = await fetchSyncStatus();
        setSyncStatus(status);
        if (!status.running) {
          loadData();
        }
      } catch {
        // ignore
      }
    }, 800);
    return () => clearInterval(interval);
  }, [syncing, loadData]);

  useEffect(() => {
    if (!syncing) setSyncStatus(null);
  }, [syncing]);

  const currentDownload = syncStatus?.current;

  const downloadedRows = downloaded.map((row) => ({
    ...row,
    status: 'downloaded',
    progress: 100,
  }));

  const pendingRows = pending.map((row) => {
    const isCurrent = currentDownload?.video_id === row.video_id;
    return {
      ...row,
      status: isCurrent ? 'downloading' : 'queueing',
      progress: isCurrent ? (currentDownload?.progress ?? 0) : 0,
    };
  });

  const allRows = [...pendingRows, ...downloadedRows];

  if (error) {
    return <p className="list-error">{error}</p>;
  }

  if (loading && !allRows.length) {
    return <p className="list-loading">Loading tracks…</p>;
  }

  if (!allRows.length) {
    return (
      <div className="list-view list-empty">
        <p className="empty-message">No tracks yet. Add playlists and run a sync to get started.</p>
      </div>
    );
  }

  return (
    <div className="list-view">
      <table className="data-table">
        <thead>
          <tr>
            <th>Track Name</th>
            <th>Artist</th>
            <th>Playlist</th>
            <th>Status</th>
            <th>Downloaded</th>
          </tr>
        </thead>
        <tbody>
          {allRows.map((row) => {
            const plShort = shortName(row.playlist_name);
            return (
              <tr key={`${row.playlist_id}-${row.video_id}-${row.status}`}>
                <td className="cell-track">{row.title}</td>
                <td className="cell-artist">{row.artist || '—'}</td>
                <td className="cell-playlist">{plShort}</td>
                <td className="cell-status">
                  {row.status === 'downloaded' && <span className="status-badge status-downloaded">Downloaded</span>}
                  {row.status === 'queueing' && <span className="status-badge status-queueing">Queueing</span>}
                  {row.status === 'downloading' && (
                    <div className="status-progress">
                      <div className="progress-bar">
                        <div
                          className="progress-fill"
                          style={{ width: `${row.progress}%` }}
                        />
                      </div>
                      <span className="progress-pct">{Math.round(row.progress)}%</span>
                    </div>
                  )}
                </td>
                <td className="cell-downloaded">
                  {row.status === 'downloaded' && row.downloaded_at
                    ? formatDownloadedAt(row.downloaded_at)
                    : '—'}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
