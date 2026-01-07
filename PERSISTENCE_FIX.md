# Persistence Fix for Render Deployment

## Problem Summary
Music playlists and welcome images are not persistent on Render because:

1. **Welcome Images** - ✅ **ALREADY FIXED** - Stores image URLs in MongoDB via `WelcomeChannelAdapter`
2. **Music Playlists** - ✅ **ALREADY FIXED** - Stores playlists in MongoDB via `playlist_storage.py`
3. **Music State** (queue, current track) - ❌ **NOT FIXED** - Uses local SQLite (`data/music_states.db`)

## Root Cause
The `music_state_storage.py` module currently uses **SQLite** for storing:
- Current playing track
- Queue state
- Volume settings
- Loop mode
- Playlist name

On Render's ephemeral filesystem, this SQLite database is **wiped on every restart**.

## Solution
Migrate `music_state_storage.py` to use MongoDB (like playlist_storage.py does), with automatic fallback to SQLite for local development.

## Implementation Status
- [x] Identified the issue
- [ ] Create MongoDB-backed MusicStateStorage class
- [ ] Test locally with MongoDB
- [ ] Deploy to Render
- [ ] Verify persistence after restart

## Files to Modify
1. `music_state_storage.py` - Add MongoDB support with SQLite fallback
2. Ensure `MONGO_URI` is set in Render environment variables

## Environment Variables Required
- `MONGO_URI` - Must be set in Render dashboard (appears to already be configured based on render.yaml)
- `MONGO_DB_NAME` - Database name (defaults to 'discord_bot')

## Testing Checklist
After deployment:
- [ ] Play music and add tracks to queue
- [ ] Stop the bot on Render
- [ ] Restart the bot
- [ ] Verify music state is restored
- [ ] Test playlist saving/loading
- [ ] Test welcome images persist across restarts
