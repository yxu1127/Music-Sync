export default function ViewToggle({ view, onViewChange }) {
  return (
    <div className="view-toggle" data-view={view}>
      <div className="toggle-bg" data-active={view} />
      <button
        type="button"
        className={`toggle-btn ${view === 'list' ? 'active' : ''}`}
        onClick={() => onViewChange('list')}
      >
        Tracks
      </button>
      <button
        type="button"
        className={`toggle-btn ${view === 'playlist' ? 'active' : ''}`}
        onClick={() => onViewChange('playlist')}
      >
        Playlist
      </button>
    </div>
  );
}
