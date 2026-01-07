# 🎵 Music Bot Quick Start

Get your music bot up and running in 5 minutes!

## ⚡ Quick Setup (Using Public Lavalink)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Add these lines to your `.env` file:

```env
# Lavalink Configuration (Public Server)
LAVALINK_HOST=lavalink.devamop.in
LAVALINK_PORT=443
LAVALINK_PASSWORD=DevamOP
LAVALINK_SECURE=true

# Music Settings
MUSIC_DEFAULT_VOLUME=50
MUSIC_MAX_QUEUE_SIZE=100
MUSIC_DISCONNECT_TIMEOUT=300
```

### 3. Start Your Bot

```bash
python app.py
```

### 4. Test It!

1. Join a voice channel in your Discord server
2. Use the command: `/play never gonna give you up`
3. Enjoy the music! 🎵

---

## 🎮 Available Commands

### Basic Playback
- `/play <query>` - Play music (YouTube, Spotify, SoundCloud)
- `/pause` - Pause playback
- `/resume` - Resume playback
- `/stop` - Stop and disconnect
- `/skip [amount]` - Skip track(s)
- `/nowplaying` - Show current track with controls

### Queue Management
- `/queue [page]` - View queue with pagination
- `/shuffle` - Shuffle the queue
- `/clear` - Clear all queued tracks
- `/remove <position>` - Remove specific track

### Playback Controls
- `/volume <0-100>` - Adjust volume
- `/loop <mode>` - Set loop mode (off/track/queue)
- `/seek <seconds>` - Jump to position in track

### Interactive Buttons
Every "now playing" message includes:
- ⏯️ **Play/Pause** - Toggle playback
- ⏭️ **Skip** - Skip to next track
- ⏹️ **Stop** - Stop and disconnect
- 🔁 **Loop** - Cycle loop modes
- 🔀 **Shuffle** - Randomize queue

---

## 🎯 Usage Examples

### Play a song
```
/play despacito
/play https://www.youtube.com/watch?v=kJQP7kiw5Fk
/play spotify:track:3n3Ppam7vgaVa1iaRUc9Lp
```

### Manage queue
```
/queue          # View current queue
/skip 3         # Skip 3 tracks
/remove 5       # Remove track at position 5
/shuffle        # Randomize queue order
/clear          # Clear entire queue
```

### Control playback
```
/volume 75      # Set volume to 75%
/loop track     # Loop current track
/seek 120       # Jump to 2:00 in the song
```

---

## 🎨 Supported Sources

- ✅ **YouTube** - Videos, playlists, live streams
- ✅ **Spotify** - Tracks, albums, playlists
- ✅ **SoundCloud** - Tracks and sets
- ✅ **Direct URLs** - MP3, M4A, WAV, etc.
- ✅ **Search** - Natural language search

---

## 🔧 Troubleshooting

### "Music features disabled" message

**Solution**: The bot couldn't connect to Lavalink. Check:
1. Your `.env` file has the Lavalink configuration
2. The public Lavalink server is online
3. Try a different public server (see MUSIC_SETUP.md)

### "Nothing is playing" error

**Solution**: Make sure you're in a voice channel before using `/play`

### Bot doesn't join voice channel

**Solution**: Check bot permissions - it needs "Connect" and "Speak" permissions

---

## 📚 Full Documentation

For advanced setup options, self-hosting Lavalink, and troubleshooting:
- See [MUSIC_SETUP.md](MUSIC_SETUP.md) for complete documentation
- Check [implementation_plan.md](../brain/implementation_plan.md) for technical details

---

## 🎉 That's It!

Your music bot is ready to use! Join a voice channel and start playing music with `/play`.

**Pro Tip**: For better performance and reliability, consider [self-hosting Lavalink](MUSIC_SETUP.md#-self-hosted-lavalink-recommended-for-production).

Enjoy! 🎵
