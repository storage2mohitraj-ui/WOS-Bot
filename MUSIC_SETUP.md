# Music System Setup Guide

This guide will help you set up the music features for your Discord bot using Lavalink and Wavelink.

## 🎵 Overview

The music system uses:
- **Wavelink** - Python library for Lavalink integration
- **Lavalink** - Standalone audio server (handles the heavy lifting)
- **Discord.py** - Your bot framework

## 📋 Prerequisites

- Python 3.10 or higher ✅ (You already have this)
- Java 13 or higher (for Lavalink server)
- Discord bot with proper intents enabled

---

## 🚀 Quick Start (Public Lavalink)

The easiest way to get started is using a public Lavalink server:

### Step 1: Update Environment Variables

Add these to your `.env` file:

```env
# Lavalink Configuration (Public Server Example)
LAVALINK_HOST=lavalink.devamop.in
LAVALINK_PORT=443
LAVALINK_PASSWORD=DevamOP
LAVALINK_SECURE=true

# Music Bot Settings
MUSIC_DEFAULT_VOLUME=50
MUSIC_MAX_QUEUE_SIZE=100
MUSIC_DISCONNECT_TIMEOUT=300
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Load the Music Cog

The music cog is already configured to load automatically. Just restart your bot!

### Step 4: Test It

Join a voice channel and try:
```
/play never gonna give you up
```

---

## 🏠 Self-Hosted Lavalink (Recommended for Production)

For better performance and reliability, host your own Lavalink server:

### Step 1: Install Java

**Windows:**
1. Download Java 17+ from [Adoptium](https://adoptium.net/)
2. Install and verify: `java -version`

**Linux:**
```bash
sudo apt update
sudo apt install openjdk-17-jre-headless
```

### Step 2: Download Lavalink

1. Download the latest Lavalink.jar from:
   - https://github.com/lavalink-devs/Lavalink/releases

2. Create a folder for Lavalink:
```bash
mkdir lavalink
cd lavalink
```

3. Move the downloaded `Lavalink.jar` to this folder

### Step 3: Create Configuration File

Create `application.yml` in the same folder as `Lavalink.jar`:

```yaml
server:
  port: 2333
  address: 0.0.0.0

lavalink:
  server:
    password: "youshallnotpass"
    sources:
      youtube: true
      bandcamp: true
      soundcloud: true
      twitch: true
      vimeo: true
      http: true
      local: false
    bufferDurationMs: 400
    frameBufferDurationMs: 5000
    youtubePlaylistLoadLimit: 6
    playerUpdateInterval: 5
    youtubeSearchEnabled: true
    soundcloudSearchEnabled: true
    gc-warnings: true

metrics:
  prometheus:
    enabled: false
    endpoint: /metrics

sentry:
  dsn: ""
  environment: ""

logging:
  file:
    max-history: 30
    max-size: 1GB
  path: ./logs/

  level:
    root: INFO
    lavalink: INFO
```

### Step 4: Run Lavalink

**Windows:**
```bash
java -jar Lavalink.jar
```

**Linux (Background):**
```bash
nohup java -jar Lavalink.jar > lavalink.log 2>&1 &
```

**Using Screen (Recommended):**
```bash
screen -S lavalink
java -jar Lavalink.jar
# Press Ctrl+A then D to detach
```

### Step 5: Configure Bot

Update your `.env` file:

```env
# Lavalink Configuration (Self-Hosted)
LAVALINK_HOST=localhost
LAVALINK_PORT=2333
LAVALINK_PASSWORD=youshallnotpass
LAVALINK_SECURE=false

# Music Bot Settings
MUSIC_DEFAULT_VOLUME=50
MUSIC_MAX_QUEUE_SIZE=100
MUSIC_DISCONNECT_TIMEOUT=300
```

### Step 6: Restart Your Bot

The bot will automatically connect to your Lavalink server on startup.

---

## 🎵 Spotify Support (Optional)

To enable Spotify playlist and track support, you need to configure the Spotify plugin for Lavalink.

### Why Spotify Needs Special Configuration

Spotify doesn't allow direct audio streaming. Instead, Lavalink:
1. Fetches track metadata from Spotify API
2. Searches for the same track on YouTube
3. Plays the YouTube version

This requires Spotify API credentials.

### Step 1: Get Spotify API Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account (free account works)
3. Click **"Create App"**
4. Fill in:
   - **App Name**: `Lavalink Music Bot` (or any name)
   - **App Description**: `Music bot for Discord`
   - **Redirect URI**: `http://localhost` (required but not used)
5. Accept terms and click **"Create"**
6. Click **"Settings"** on your new app
7. Copy your **Client ID** and **Client Secret**

### Step 2: Update Lavalink Configuration

Add the Spotify plugin to your `application.yml`:

```yaml
server:
  port: 2333
  address: 0.0.0.0

lavalink:
  plugins:
    - dependency: "com.github.topi314.lavasrc:lavasrc-plugin:4.0.1"
      repository: "https://maven.topi.wtf/releases"
  server:
    password: "youshallnotpass"
    sources:
      youtube: true
      bandcamp: true
      soundcloud: true
      twitch: true
      vimeo: true
      http: true
      local: false
      spotify: true  # Enable Spotify
    bufferDurationMs: 400
    frameBufferDurationMs: 5000
    youtubePlaylistLoadLimit: 6
    playerUpdateInterval: 5
    youtubeSearchEnabled: true
    soundcloudSearchEnabled: true
    gc-warnings: true

plugins:
  lavasrc:
    providers:
      - "ytsearch:\"%ISRC%\""
      - "ytsearch:%QUERY%"
    sources:
      spotify: true
      applemusic: false
      deezer: false
      yandexmusic: false
    spotify:
      clientId: "YOUR_SPOTIFY_CLIENT_ID"
      clientSecret: "YOUR_SPOTIFY_CLIENT_SECRET"
      countryCode: "US"  # Change to your country code
      playlistLoadLimit: 50
      albumLoadLimit: 50

metrics:
  prometheus:
    enabled: false
    endpoint: /metrics

sentry:
  dsn: ""
  environment: ""

logging:
  file:
    max-history: 30
    max-size: 1GB
  path: ./logs/

  level:
    root: INFO
    lavalink: INFO
```

### Step 3: Restart Lavalink

After updating the configuration, restart your Lavalink server:

```bash
# Stop the current process (Ctrl+C if running in foreground)
# Then start again
java -jar Lavalink.jar
```

### Step 4: Test Spotify Support

Try playing a Spotify track or playlist:

```
/play https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT
/play https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
```

### Troubleshooting Spotify

**"Failed to Load Tracks" Error:**
- Verify your Spotify Client ID and Secret are correct
- Check that the plugin is properly loaded in Lavalink logs
- Ensure the playlist/track is public (not private)
- Try a different country code in the configuration

**Tracks Not Found:**
- The bot searches YouTube for Spotify tracks
- Some tracks may not be available on YouTube
- Try enabling more search providers in the configuration

**Rate Limiting:**
- Spotify API has rate limits
- For heavy usage, consider creating multiple Spotify apps
- Rotate credentials if you hit limits

---

## 🐳 Docker Setup (Advanced)

### Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  lavalink:
    image: fredboat/lavalink:latest
    container_name: lavalink
    restart: unless-stopped
    ports:
      - "2333:2333"
    volumes:
      - ./lavalink/application.yml:/opt/Lavalink/application.yml
    networks:
      - bot-network

  discord-bot:
    build: .
    container_name: discord-bot
    restart: unless-stopped
    depends_on:
      - lavalink
    environment:
      - LAVALINK_HOST=lavalink
      - LAVALINK_PORT=2333
      - LAVALINK_PASSWORD=youshallnotpass
    networks:
      - bot-network

networks:
  bot-network:
    driver: bridge
```

Run with:
```bash
docker-compose up -d
```

---

## 🌐 Public Lavalink Servers

Here are some reliable public Lavalink servers you can use:

### Option 1: DevamOP (Recommended)
```env
LAVALINK_HOST=lavalink.devamop.in
LAVALINK_PORT=443
LAVALINK_PASSWORD=DevamOP
LAVALINK_SECURE=true
```

### Option 2: Cog.red
```env
LAVALINK_HOST=lavalink.cog.red
LAVALINK_PORT=2333
LAVALINK_PASSWORD=youshallnotpass
LAVALINK_SECURE=false
```

### Option 3: Oops.wtf
```env
LAVALINK_HOST=lavalink.oops.wtf
LAVALINK_PORT=443
LAVALINK_PASSWORD=www.freelavalink.ga
LAVALINK_SECURE=true
```

> **⚠️ Warning**: Public servers may have rate limits, downtime, or restricted features. For production bots, self-hosting is recommended.

---

## 🎮 Available Commands

Once set up, users can use these commands:

### Basic Playback
- `/play <query>` - Play a song or add to queue
- `/pause` - Pause current track
- `/resume` - Resume playback
- `/stop` - Stop and disconnect
- `/skip [amount]` - Skip track(s)
- `/nowplaying` - Show current track

### Queue Management
- `/queue [page]` - View queue
- `/shuffle` - Shuffle queue
- `/clear` - Clear queue
- `/remove <position>` - Remove track from queue

### Controls
- `/volume <0-100>` - Set volume
- `/seek <seconds>` - Seek to position
- `/loop <mode>` - Set loop mode (off/track/queue)

### Interactive Controls
Each "now playing" message includes buttons for:
- ⏯️ Play/Pause
- ⏭️ Skip
- ⏹️ Stop
- 🔁 Loop
- 🔀 Shuffle

---

## 🔧 Troubleshooting

### Bot says "Music features disabled"

**Problem**: Lavalink connection failed

**Solutions**:
1. Verify Lavalink server is running:
   ```bash
   curl http://localhost:2333
   ```
2. Check `.env` configuration matches your Lavalink setup
3. Check Lavalink logs for errors
4. Ensure firewall allows port 2333

### "No tracks found" error

**Problem**: Search isn't working

**Solutions**:
1. Check if YouTube search is enabled in `application.yml`
2. Try a direct URL instead of search query
3. Check Lavalink logs for API errors

### Bot disconnects immediately

**Problem**: Auto-disconnect timeout too short

**Solution**: Increase `MUSIC_DISCONNECT_TIMEOUT` in `.env`:
```env
MUSIC_DISCONNECT_TIMEOUT=600  # 10 minutes
```

### Audio is choppy or laggy

**Problem**: Network or server performance issues

**Solutions**:
1. Use a closer Lavalink server
2. Increase buffer in `application.yml`:
   ```yaml
   bufferDurationMs: 800
   ```
3. Check your server's CPU/RAM usage

### "Already connected to voice" error

**Problem**: Bot stuck in voice channel

**Solution**: Use `/stop` command or restart the bot

---

## 📊 Performance Tips

### For Self-Hosted Lavalink

**Minimum Requirements:**
- 512MB RAM
- 1 CPU core
- 10GB disk space

**Recommended:**
- 1GB+ RAM
- 2+ CPU cores
- 20GB+ disk space

**Optimization:**
```yaml
# In application.yml
lavalink:
  server:
    bufferDurationMs: 400  # Lower for less latency
    frameBufferDurationMs: 1000  # Lower for less memory
    youtubePlaylistLoadLimit: 10  # Limit playlist size
```

### For Bot

**Environment Variables:**
```env
MUSIC_MAX_QUEUE_SIZE=50  # Limit queue size
MUSIC_DISCONNECT_TIMEOUT=180  # Disconnect faster
```

---

## 🔐 Security Notes

### For Public Bots

1. **Change default password** in `application.yml`
2. **Use firewall** to restrict Lavalink access:
   ```bash
   # Allow only localhost
   sudo ufw allow from 127.0.0.1 to any port 2333
   ```
3. **Use SSL/TLS** for production (set `LAVALINK_SECURE=true`)

### For Private Bots

- Keep Lavalink on localhost
- Don't expose port 2333 to internet
- Use strong passwords

---

## 📝 Additional Resources

- [Lavalink GitHub](https://github.com/lavalink-devs/Lavalink)
- [Wavelink Documentation](https://wavelink.dev/)
- [Public Lavalink List](https://lavalink-list.darrennathanael.com/)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Lavalink server is running
- [ ] Bot connects to Lavalink on startup (check logs)
- [ ] `/play` command works with YouTube URLs
- [ ] `/play` command works with search queries
- [ ] Queue system works (add multiple songs)
- [ ] Playback controls work (pause/resume/skip)
- [ ] Volume control works
- [ ] Interactive buttons work
- [ ] Bot disconnects after timeout

---

## 🆘 Getting Help

If you encounter issues:

1. Check Lavalink logs: `./logs/` folder
2. Check bot logs for connection errors
3. Verify `.env` configuration
4. Try a different Lavalink server
5. Check [Lavalink Discord](https://discord.gg/ZW4s47Ppw4) for support

---

## 🎉 You're All Set!

Your music bot is ready to rock! Join a voice channel and start playing music with `/play`.

Enjoy! 🎵
