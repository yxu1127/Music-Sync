-- Run this in Supabase SQL Editor to create the playlists table
-- Dashboard: https://supabase.com/dashboard → Your Project → SQL Editor

create table if not exists playlists (
  id text primary key,
  name text not null default 'Unknown Playlist',
  paused boolean not null default false,
  thumbnail text
);

-- Enable RLS (Row Level Security) - optional, we use service_role key which bypasses RLS
-- alter table playlists enable row level security;
