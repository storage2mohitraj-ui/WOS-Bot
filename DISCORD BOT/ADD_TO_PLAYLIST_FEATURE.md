# Add to Playlist Feature

## Overview
Added a new "**Add to Playlist**" button to the music player controls that allows users to add the currently playing track to a playlist.

## User Flow

### When Music is Playing
1. User plays a song using `/play` or any other music command
2. The now playing message appears with player controls
3. A new green button "**➕ Add to Playlist**" is now visible on row 2

### Adding to Playlist
When user clicks the "Add to Playlist" button:

#### Option 1: User has existing playlists
- A selection menu appears showing all user's playlists (up to 25)
- User can select a playlist from the dropdown to add the current track
- **OR** user can click "**➕ Create New Playlist**" button
- Track is added to the selected/new playlist
- Success confirmation message appears

#### Option 2: User has no playlists
- A message indicates no playlists exist yet
- User clicks "**➕ Create New Playlist**" button
- A modal appears asking for playlist name
- User enters name and submits
- New playlist is created with the current track
- Success confirmation message appears

## Technical Implementation

### Files Modified
1. **`cogs/music.py`**
   - Added `add_to_playlist_button()` method to `PlayerControlView` class
   - Updated imports to include `AddToPlaylistView`
   - Button placed on row 2 of the player controls

2. **`cogs/playlist_ui.py`**
   - Added `AddToPlaylistView` class - Main view for selecting/creating playlists
   - Added `AddTrackToPlaylistModal` class - Modal for entering playlist name
   - Handles both adding to existing playlists and creating new ones

### Key Features
- **Smart Detection**: Automatically detects if playlist name already exists
  - If exists: Adds track to existing playlist
  - If new: Creates new playlist with this track
- **User-Friendly UI**: 
  - Dropdown select for existing playlists
  - Button to create new playlist
  - Cancel button to dismiss
- **Validation**: Checks if music is playing before showing the UI
- **Ephemeral Messages**: All interactions are private to the user

## Database
Uses the existing `playlist_storage` module which supports:
- MongoDB (for production/Render deployment)
- SQLite (for local development)

## Button Layout
The player control view now has 3 rows:
- **Row 0**: Previous, Skip, Pause/Play, Loop, Shuffle
- **Row 1**: Volume Down, Volume Up, Seek, Effects, Search
- **Row 2**: **Add to Playlist** ⭐ (NEW)

## Usage Example
```
User: /play Shape of You
Bot: [Now Playing embed with controls]
User: *clicks "➕ Add to Playlist"*
Bot: [Shows playlist selection UI]
User: *selects "My Favorites" from dropdown*
Bot: "✅ Added Shape of You to playlist My Favorites!"
```

## Error Handling
- Validates track is currently playing
- Handles database errors gracefully
- Shows user-friendly error messages
- Timeout protection (180 seconds)

## Benefits
- **Quick action**: Add songs on the fly while listening
- **Playlist building**: Build playlists naturally as you discover music
- **Convenience**: No need to remember song names to add later
- **Seamless**: Works with any music source (YouTube, Spotify, etc.)
