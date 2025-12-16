# Lavalink Deployment Options for Production

## Option 1: Public Lavalink (Easiest)

### Working Public Servers (Updated Dec 2024)

Try these in order until one works:

**Server 1:**
```env
LAVALINK_HOST=lavalink.jirayu.net
LAVALINK_PORT=13592
LAVALINK_PASSWORD=youshallnotpass
LAVALINK_SECURE=false
```

**Server 2:**
```env
LAVALINK_HOST=lava.link
LAVALINK_PORT=80
LAVALINK_PASSWORD=anything
LAVALINK_SECURE=false
```

**Server 3:**
```env
LAVALINK_HOST=lavalink-repl.cloud
LAVALINK_PORT=443
LAVALINK_PASSWORD=youshallnotpass
LAVALINK_SECURE=false
```

---

## Option 2: Deploy Lavalink on Railway (Recommended)

### Why Railway?
- ✅ Free $5/month credit
- ✅ Easy Java support
- ✅ Better than Render for Lavalink
- ✅ Simple setup

### Steps:

1. **Create Railway Account**: https://railway.app/
2. **New Project** → **Deploy from GitHub**
3. **Use this template**: https://github.com/DarrenOfficial/lavalink-railway
4. **Set environment variables**:
   - `LAVALINK_SERVER_PASSWORD=your_password_here`
5. **Deploy** - Railway handles everything!
6. **Get your URL** from Railway dashboard
7. **Update bot's `.env`**:
   ```env
   LAVALINK_HOST=your-app.railway.app
   LAVALINK_PORT=443
   LAVALINK_PASSWORD=your_password_here
   LAVALINK_SECURE=true
   ```

---

## Option 3: Deploy Lavalink on Render (Advanced)

### Requirements:
- Separate web service
- Custom Dockerfile
- More complex setup

### Steps:

1. **Create `Dockerfile.lavalink`** in your repo:

```dockerfile
FROM openjdk:17-slim

WORKDIR /opt/Lavalink

# Download Lavalink
ADD https://github.com/lavalink-devs/Lavalink/releases/download/4.0.0/Lavalink.jar Lavalink.jar

# Copy config
COPY application.yml application.yml

# Expose port
EXPOSE 2333

# Run Lavalink
CMD ["java", "-jar", "Lavalink.jar"]
```

2. **Create `application.yml`** (same as local setup)

3. **Create new Web Service on Render**:
   - Docker
   - Point to your repo
   - Use `Dockerfile.lavalink`
   - Set port to 2333

4. **Update bot's `.env`**:
   ```env
   LAVALINK_HOST=your-lavalink.onrender.com
   LAVALINK_PORT=443
   LAVALINK_PASSWORD=youshallnotpass
   LAVALINK_SECURE=true
   ```

### Render Limitations:
- ⚠️ Free tier sleeps after 15 min inactivity
- ⚠️ Limited memory (512MB)
- ⚠️ Requires paid plan for 24/7 uptime

---

## Option 4: Fly.io (Good Alternative)

### Advantages:
- ✅ Better free tier
- ✅ No sleep on inactivity
- ✅ Easy Docker deployment

### Quick Deploy:

1. Install Fly CLI: `powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"`
2. Create `fly.toml`:

```toml
app = "your-lavalink"

[build]
  dockerfile = "Dockerfile.lavalink"

[[services]]
  internal_port = 2333
  protocol = "tcp"

  [[services.ports]]
    port = 443
```

3. Deploy:
```bash
fly launch
fly deploy
```

---

## 🎯 My Recommendation

**For your Render deployment:**

### Best Approach:
1. **Keep bot on Render** (as you have now)
2. **Deploy Lavalink on Railway** (free, reliable, easy)
3. **Connect them** via environment variables

### Why?
- ✅ Render is great for Python bots
- ✅ Railway is better for Java/Lavalink
- ✅ Both have free tiers
- ✅ Simple to maintain
- ✅ No sleep issues

### Alternative:
Use a reliable public Lavalink server (try Server 1-3 above) until you're ready to deploy your own.

---

## Quick Test Command

To test if a Lavalink server is working:

```bash
curl http://lavalink-host:port/version
```

Should return Lavalink version info.

---

## Summary

| Option | Difficulty | Cost | Reliability | Recommended |
|--------|-----------|------|-------------|-------------|
| Public Server | Easy | Free | Medium | ⭐ For testing |
| Railway | Easy | Free | High | ⭐⭐⭐ Best |
| Render | Hard | Free/Paid | Medium | ⭐ If already using |
| Fly.io | Medium | Free | High | ⭐⭐ Good alternative |
| Local | Easy | Free | High | ⭐⭐ Development only |

**My recommendation: Use Railway for Lavalink + Render for your bot**
