# 🎵 Music Bot Features

Your Discord bot now includes comprehensive music playback capabilities!

## ✨ Features

- 🎵 **Multi-Source Support** - YouTube, Spotify, SoundCloud, and more
- 🎮 **15+ Commands** - Complete playback control
- 🎨 **Interactive UI** - Buttons, embeds, and progress bars
- 📋 **Queue Management** - Add, remove, shuffle, and view tracks
- 🔁 **Loop Modes** - Loop track, queue, or disable
- 🔊 **Volume Control** - Adjust from 0-100%
- ⏩ **Seek & Skip** - Jump to any position or skip tracks
- 🎯 **Auto-Disconnect** - Saves resources when inactive
- 🌐 **Multi-Server** - Independent players per server

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Lavalink
Add to your `.env` file:
```env
LAVALINK_HOST=lavalink.devamop.in
LAVALINK_PORT=443
LAVALINK_PASSWORD=DevamOP
LAVALINK_SECURE=true

MUSIC_DEFAULT_VOLUME=50
MUSIC_MAX_QUEUE_SIZE=100
MUSIC_DISCONNECT_TIMEOUT=300
```

### 3. Start Bot
```bash
python app.py
```

### 4. Test
Join a voice channel and use:
```
/play never gonna give you up
```

## 📖 Documentation

- **[Quick Start Guide](MUSIC_QUICKSTART.md)** - Get started in 5 minutes
- **[Setup Guide](MUSIC_SETUP.md)** - Detailed setup instructions
- **[Walkthrough](../brain/walkthrough.md)** - Complete implementation details

## 🎮 Commands

### Basic Playback
- `/play <query>` - Play music
- `/pause` - Pause playback
- `/resume` - Resume playback
- `/stop` - Stop and disconnect
- `/skip [amount]` - Skip tracks
- `/nowplaying` - Show current track

### Queue Management
- `/queue [page]` - View queue
- `/shuffle` - Shuffle queue
- `/clear` - Clear queue
- `/remove <position>` - Remove track

### Controls
- `/volume <0-100>` - Set volume
- `/loop <mode>` - Set loop mode
- `/seek <seconds>` - Seek position

## 🎯 Supported Sources

✅ YouTube (videos, playlists, live streams)  
✅ Spotify (tracks, albums, playlists)  
✅ SoundCloud (tracks, sets)  
✅ Direct URLs (MP3, M4A, WAV, etc.)  
✅ Twitch (live streams)  
✅ Bandcamp (tracks, albums)  

## 🎨 Interactive Controls

Every "now playing" message includes buttons:
- ⏯️ Play/Pause
- ⏭️ Skip
- ⏹️ Stop
- 🔁 Loop
- 🔀 Shuffle

## 🔧 Troubleshooting

### Music features disabled?
1. Check `.env` has Lavalink configuration
2. Verify Lavalink server is online
3. See [MUSIC_SETUP.md](MUSIC_SETUP.md) for help

### Bot doesn't join voice?
- Ensure you're in a voice channel
- Check bot has "Connect" and "Speak" permissions

### No tracks found?
- Try a more specific search query
- Use direct URLs for exact tracks

## 📚 Learn More

For detailed setup, troubleshooting, and advanced features:
- Read [MUSIC_SETUP.md](MUSIC_SETUP.md)
- Check [MUSIC_QUICKSTART.md](MUSIC_QUICKSTART.md)

---

**Enjoy your music bot! 🎵**
