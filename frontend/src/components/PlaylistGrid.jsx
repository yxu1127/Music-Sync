import PlaylistCard from './PlaylistCard';

export default function PlaylistGrid({ playlists, onSyncPlaylist, onTogglePause, onRemovePlaylist }) {
  if (!playlists?.length) {
    return (
      <div className="playlist-grid playlist-empty">
        <p className="empty-message">No playlists configured. Add playlists in config.yaml</p>
      </div>
    );
  }

  return (
    <div className="playlist-grid">
      {playlists.map((p, i) => (
        <PlaylistCard
          key={p.id}
          playlist={p}
          index={i}
          onSync={onSyncPlaylist}
          onToggle={onTogglePause}
          onRemove={onRemovePlaylist}
        />
      ))}
    </div>
  );
}
