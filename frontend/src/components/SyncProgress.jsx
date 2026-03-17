import { useState, useEffect } from 'react';
import { fetchSyncStatus } from '../api';

export default function SyncProgress({ syncing }) {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    if (!syncing) {
      setStatus(null);
      return;
    }
    const interval = setInterval(async () => {
      try {
        const s = await fetchSyncStatus();
        setStatus(s);
      } catch {
        // ignore
      }
    }, 500);
    return () => clearInterval(interval);
  }, [syncing]);

  if (!syncing) return null;

  if (!status?.current) {
    return (
      <div className="sync-progress-bar sync-progress-indeterminate">
        <span className="sync-progress-icon">↓</span>
        <span className="sync-progress-label">
          {status?.running ? 'Checking for new tracks…' : 'Syncing…'}
        </span>
      </div>
    );
  }

  const { title, artist, progress = 0 } = status.current;
  const label = artist ? `${artist} – ${title}` : title;

  return (
    <div className="sync-progress-bar">
      <div className="sync-progress-label">
        <span className="sync-progress-icon">↓</span>
        Downloading: {label}
      </div>
      <div className="sync-progress-track">
        <div
          className="sync-progress-fill"
          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
        />
      </div>
      <span className="sync-progress-pct">{Math.round(progress)}%</span>
    </div>
  );
}
