# Quick Lavalink Local Setup

## Download and Run Lavalink (5 minutes)

### Step 1: Download Lavalink

Download the latest Lavalink.jar from:
https://github.com/lavalink-devs/Lavalink/releases/latest

Save it to: `f:\STARK-whiteout survival bot\DISCORD BOT\lavalink\`

### Step 2: Create Configuration

Create `application.yml` in the same folder with this content:

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

sentry:
  dsn: ""

logging:
  file:
    path: ./logs/
  level:
    root: INFO
    lavalink: INFO
```

### Step 3: Run Lavalink

Open a NEW terminal and run:

```powershell
cd "f:\STARK-whiteout survival bot\DISCORD BOT\lavalink"
java -jar Lavalink.jar
```

Keep this terminal open!

### Step 4: Update Bot Configuration

In your `.env` file:

```env
LAVALINK_HOST=localhost
LAVALINK_PORT=2333
LAVALINK_PASSWORD=youshallnotpass
LAVALINK_SECURE=false
```

### Step 5: Restart Bot

```powershell
python app.py
```

## Quick Test

Once both are running:
1. Join a voice channel
2. Use `/play never gonna give you up`
3. Enjoy! 🎵

---

## Troubleshooting

**"Java not found"**
- Install Java 17+: https://adoptium.net/
- Restart terminal after installing

**"Port 2333 already in use"**
- Change port in `application.yml` and `.env`

**Bot still can't connect**
- Make sure Lavalink terminal shows "Lavalink is ready to accept connections"
- Check firewall isn't blocking port 2333
