import { useState, useEffect, useCallback } from 'react';
import { fetchConfig, triggerSync, updateSchedule, updateFormat } from '../api';

export default function Sidebar({ onSyncStart, onSyncing }) {
  const [freq, setFreq] = useState(30);
  const [format, setFormat] = useState('wav');
  const [autoDownload, setAutoDownload] = useState(true);
  const [config, setConfig] = useState(null);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [savingFormat, setSavingFormat] = useState(false);
  const syncing = onSyncing ?? false;

  useEffect(() => {
    fetchConfig()
      .then((c) => {
        setConfig(c);
        setFreq(c.schedule_interval_minutes ?? 30);
        setFormat(c.download_format ?? 'wav');
      })
      .catch(() => setConfig(null));
  }, []);

  const handleSync = () => {
    setError(null);
    onSyncStart?.();
  };

  const handleFreqChange = useCallback((e) => {
    const val = Number(e.target.value);
    setFreq(val);
  }, []);

  const handleFreqCommit = useCallback(() => {
    const val = freq;
    if (val < 15 || val > 1440) return;
    setSaving(true);
    setError(null);
    updateSchedule(val)
      .catch((e) => setError(e.message))
      .finally(() => setSaving(false));
  }, [freq]);

  const handleFormatChange = useCallback((newFormat) => {
    if (newFormat === format) return;
    setSavingFormat(true);
    setError(null);
    updateFormat(newFormat)
      .then(() => setFormat(newFormat))
      .catch((e) => setError(e.message))
      .finally(() => setSavingFormat(false));
  }, [format]);

  const freqDisplay = freq >= 60 ? `${Math.round(freq / 60)} hrs` : `${freq} min`;

  return (
    <aside className="sidebar">
      <div className="logo">
        <div className="logo-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 18V5l12-2v13" />
            <circle cx="6" cy="18" r="3" />
            <circle cx="18" cy="16" r="3" />
          </svg>
        </div>
        MusicSync
      </div>

      <div className="sidebar-section">
        <div className="section-title">Sync Configuration</div>
        <div className="sync-control">
          <div className="knob-container">
            <span className="knob-label">Frequency</span>
            <span className="knob-value">{saving ? 'Saving…' : freqDisplay}</span>
          </div>
          <input
            type="range"
            min="15"
            max="1440"
            step="15"
            value={freq}
            onChange={handleFreqChange}
            onMouseUp={handleFreqCommit}
            onTouchEnd={handleFreqCommit}
            title="Drag to adjust sync frequency (15 min – 24 hrs)"
          />
          <div className="sync-row">
            <span className="sync-label">Format</span>
            <div className="format-selector">
              <button
                type="button"
                className={`format-btn ${format === 'wav' ? 'active' : ''}`}
                onClick={() => handleFormatChange('wav')}
                disabled={savingFormat}
              >
                WAV
              </button>
              <button
                type="button"
                className={`format-btn ${format === 'mp3' ? 'active' : ''}`}
                onClick={() => handleFormatChange('mp3')}
                disabled={savingFormat}
              >
                MP3
              </button>
            </div>
          </div>
          <div className="sync-row">
            <span className="sync-label">Auto-download</span>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={autoDownload}
                onChange={(e) => setAutoDownload(e.target.checked)}
              />
              <span className="toggle-slider" />
            </label>
          </div>
          <button
            className="btn-sync-now"
            onClick={handleSync}
            disabled={syncing}
          >
            {syncing ? 'Syncing…' : 'Sync now'}
          </button>
          {error && <p className="sync-error">{error}</p>}
        </div>
      </div>
    </aside>
  );
}
