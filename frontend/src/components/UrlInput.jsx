import { useState } from 'react';
import { addPlaylist } from '../api';

export default function UrlInput({ onPlaylistAdded }) {
  const [url, setUrl] = useState('');
  const [message, setMessage] = useState(null);
  const [adding, setAdding] = useState(false);

  const handleAdd = async () => {
    const trimmed = url.trim();
    if (!trimmed) return;

    setAdding(true);
    setMessage(null);
    try {
      const added = await addPlaylist(trimmed);
      setMessage(`Added "${added.name}". Syncing now…`);
      setUrl('');
      onPlaylistAdded?.(added);
    } catch (e) {
      setMessage(e.message || 'Failed to add playlist');
    } finally {
      setAdding(false);
    }
  };

  return (
    <div className="url-input-group">
      <div className="url-input-wrapper">
        <span className="url-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
          </svg>
        </span>
        <input
          type="text"
          className="url-input"
          placeholder="Paste YouTube Playlist URL to add..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
        />
        <button type="button" className="btn-add" onClick={handleAdd} disabled={adding || !url.trim()}>
          {adding ? 'Adding…' : 'Add'}
        </button>
      </div>
      {message && (
        <div className={`url-message ${message.startsWith('Added') ? 'url-message-success' : ''}`} role="status">{message}</div>
      )}
    </div>
  );
}
