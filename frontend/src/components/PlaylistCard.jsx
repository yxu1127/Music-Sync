import { useState } from 'react';

export default function PlaylistCard({ playlist, index, onSync, onToggle, onRemove }) {
  const [updating, setUpdating] = useState(false);
  const [removing, setRemoving] = useState(false);
  const [imgError, setImgError] = useState(false);
  const artColors = ['art-color-1', 'art-color-2', 'art-color-3'];
  const artColor = artColors[index % artColors.length];
  const paused = playlist.paused ?? false;
  const showThumbnail = playlist.thumbnail && !imgError;

  const handleToggle = async () => {
    setUpdating(true);
    try {
      if (paused) {
        await onToggle?.(playlist.id, false);
        await onSync?.(playlist.id);
      } else {
        await onToggle?.(playlist.id, true);
      }
    } finally {
      setUpdating(false);
    }
  };

  const handleRemove = async () => {
    if (!confirm(`Remove "${playlist.name}" from sync?`)) return;
    setRemoving(true);
    try {
      await onRemove?.(playlist.id);
    } finally {
      setRemoving(false);
    }
  };

  return (
    <div className="playlist-card">
      <div className={`card-art ${artColor} ${showThumbnail ? 'card-art-img' : ''}`}>
        {showThumbnail ? (
          <img
            src={playlist.thumbnail}
            alt=""
            className="card-art-image"
            onError={() => setImgError(true)}
          />
        ) : (
          <span className="card-art-initial">{(playlist.name || 'P')[0].toUpperCase()}</span>
        )}
        <div className={`card-badge ${paused ? '' : 'badge-active'}`}>
          {paused ? 'PAUSED' : 'SYNCING'}
        </div>
      </div>
      <div className="card-header">
        <div>
          <h3 className="card-title">{playlist.name}</h3>
          <span className="card-meta">{paused ? 'Sync stopped' : 'Active'}</span>
        </div>
        <div className="card-actions">
          <button
            type="button"
            className="btn-text"
            onClick={handleToggle}
            disabled={updating}
          >
            {updating ? '…' : paused ? 'Resume' : 'Stop'}
          </button>
          <button
            type="button"
            className="btn-icon btn-trash"
            onClick={handleRemove}
            disabled={removing}
            title="Remove playlist"
            aria-label="Remove playlist"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="3 6 5 6 21 6" />
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
              <line x1="10" y1="11" x2="10" y2="17" />
              <line x1="14" y1="11" x2="14" y2="17" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
