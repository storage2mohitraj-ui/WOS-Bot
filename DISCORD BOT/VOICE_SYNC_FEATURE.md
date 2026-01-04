# Voice Channel Syncing Feature

## Overview
The `/syncdata` command has been enhanced to support **voice channel recording** in addition to text message extraction. When you select a voice channel, the bot will connect to it and record audio from all active participants.

## How It Works

### For Text Channels (Original Behavior)
1. Run `/syncdata`
2. Select a server
3. Select a text channel
4. Choose format (JSON, TXT, CSV, or BEST)
5. Choose message limit (50, 100, 500, or custom)
6. Receive extracted messages as a file

### For Voice Channels (New Feature)
1. Run `/syncdata`
2. Select a server
3. Select a **voice channel** (marked with 🔊)
4. Choose recording format (currently MP3)
5. Choose recording duration in seconds:
   - **50s** - Quick sample
   - **100s** - Short recording (~1.5 minutes)
   - **500s** - Extended recording (~8 minutes)
   - **Max Duration** - Maximum allowed (300s / 5 minutes)
   - **Custom** - Enter your own duration
6. Receive recorded audio files (one per participant)

## Features

### ✅ What's Supported
- **Multi-user recording**: Records each participant separately
- **MP3 format**: High-quality audio in widely compatible format
- **Automatic file naming**: Files include guild ID, channel ID, username, and timestamp
- **Duration control**: Maximum 300 seconds (5 minutes) per recording
- **Real-time status**: Shows recording progress and participant count
- **Error handling**: Clear messages for permission issues or connection problems

### 🎙️ Recording Process
1. Bot connects to the voice channel
2. Starts recording all active speakers
3. Records for the specified duration
4. Disconnects and processes audio
5. Sends separate MP3 files for each participant

### ⚠️ Important Notes
- **Permissions Required**: Bot needs `CONNECT` and `USE_VOICE_ACTIVITY` permissions
- **Admin Access**: Only Global Administrators can use `/syncdata`
- **User Consent**: Ensure you have permission to record users (Discord ToS compliance)
- **Duration Limits**: Maximum 300 seconds (5 minutes) per recording session
- **No Audio Detection**: If no one speaks during recording, you'll receive a notification with no files

## Technical Requirements

### Dependencies
The voice recording feature requires:
- `py-cord[voice]` - Discord library with voice support
- `discord.sinks` - Audio recording sinks
- FFmpeg - Audio processing

If voice dependencies are not installed, the bot will show an error message and suggest installation.

### Installation
If voice recording doesn't work, the bot administrator needs to install:
```bash
pip install py-cord[voice]
```

## UI Enhancements

### Voice Channel Indicators
- Voice channels are marked with 🔊 emoji in selection menus
- Different configuration screens for voice vs text channels
- Duration-based buttons (seconds) instead of message counts for voice
- Red-themed embeds for voice recording vs blue for text extraction

### Button Labels
For voice channels:
- `50s` - 50 seconds
- `1m 40s` - 100 seconds  
- `8m 20s` - 500 seconds
- `Max Duration` - 5 minutes (300s)
- Custom option with seconds input

## Privacy & Legal Considerations

⚠️ **IMPORTANT**: Recording voice conversations has legal and ethical implications:

1. **User Consent**: Always inform users they're being recorded
2. **Discord ToS**: Comply with Discord's Terms of Service
3. **Local Laws**: Some jurisdictions require all-party consent for recording
4. **Data Storage**: Handle recorded audio securely and delete when no longer needed
5. **Server Rules**: Get server owner approval before recording

## Example Use Cases

### 1. Meeting Recording
Record team meetings or discussions for later review:
```
/syncdata → Select Server → Select Voice Channel → MP3 → 500s
```

### 2. Quick Voice Sample
Capture a brief voice sample for testing:
```
/syncdata → Select Server → Select Voice Channel → MP3 → 50s
```

### 3. Extended Session
Record a longer conversation (up to 5 minutes):
```/syncdata → Select Server → Select Voice Channel → MP3 → Max Duration
```

## Error Messages

| Message | Meaning | Solution |
|---------|---------|----------|
| "Voice Recording Not Available" | py-cord[voice] not installed | Install voice dependencies |
| "Access Denied" | Bot lacks voice permissions | Grant CONNECT permission |
| "Voice Connection Error" | Can't connect to channel | Check bot permissions and channel status |
| "No Audio Detected" | No one spoke during recording | Ensure participants are unmuted and speaking |

## Security Features

- ✅ **Admin-only access**: Restricted to Global Administrators
- ✅ **Permission checks**: Verifies bot can connect before attempting
- ✅ **Ephemeral responses**: All messages are private to the user
- ✅ **Auto-disconnect**: Bot leaves channel after recording
- ✅ **Individual files**: Separate audio per user for privacy

## Future Enhancements

Potential future improvements:
- [ ] Multiple format support (WAV, FLAC, OGG)
- [ ] Automatic transcription of recorded audio
- [ ] Mixing all participants into single file option
- [ ] Scheduled recording sessions
- [ ] Cloud storage integration
- [ ] Recording notifications sent to channel

## Changelog

### Version 1.0 (Current)
- ✅ Added voice channel recording to `/syncdata`
- ✅ MP3 format support
- ✅ Duration-based recording (up to 300s)
- ✅ Per-user audio file generation
- ✅ Voice channel detection in UI
- ✅ Customized embeds for voice channels
- ✅ Error handling and user feedback

---

**Note**: This feature complements the existing text message extraction functionality and maintains the same security model (Global Admin only).
