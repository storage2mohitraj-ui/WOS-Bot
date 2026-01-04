# Render Deployment Troubleshooting

## Current Status
✅ py-cord-2.7.0 installed successfully  
❌ Application exiting early (crash on startup)

## Problem
Bot crashes immediately with "Application exited early" but logs don't show the actual error.

## Common Causes & Solutions

### 1. Missing Environment Variables
**Check Render Dashboard** → Your Service → Environment

Required variables:
```
DISCORD_TOKEN=your_bot_token_here
MONGO_URI=your_mongodb_connection_string  (if using MongoDB)
```

Optional but important:
```
DISCORD_BOT_TOKEN=your_token  (some code uses this name)
OPENROUTER_API_KEY=your_api_key
FEEDBACK_CHANNEL_ID=channel_id
```

**Fix**: Add missing env vars in Render dashboard

### 2. Startup Script Error
Check if the start command is correct in Render:

**Current**: `cd "DISCORD BOT" && export PYTHONPATH=... && python app.py`

**Should be**: Simple as possible
```
python app.py
```

**Fix**: Update "Start Command" in Render dashboard to just `python app.py`

### 3. View Actual Error Logs
Enable better logging to see the real error:

Add to the top of `app.py` (after imports):
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Your existing code
    pass
except Exception as e:
    logger.error(f"FATAL ERROR: {e}", exc_info=True)
    raise
```

### 4. Check File Paths
Render might have different working directory. Update file paths:

**Bad**:
```python
STATE_FILE = "giftcode_state.json"
```

**Good**:
```python
STATE_FILE = os.path.join(os.path.dirname(__file__), "giftcode_state.json")
```

### 5. Missing Dependencies (Check Render Logs)
Look for:
```
ModuleNotFoundError: No module named 'xyz'
```

If found, add to `requirements.txt`

## Debugging Steps

### Step 1: Add Debug Logging
Create `debug_start.py`:
```python
import sys
import os

print("=== DEBUG START ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

try:
    import discord
    print(f"✅ Discord version: {discord.__version__}")
    print(f"✅ Has sinks: {hasattr(discord, 'sinks')}")
except Exception as e:
    print(f"❌ Discord import error: {e}")

try:
    import app
    print("✅ App imported successfully")
except Exception as e:
    print(f"❌ App import error: {e}")
    import traceback
    traceback.print_exc()

print("=== DEBUG END ===")
```

Change Render start command temporarily to:
```
python debug_start.py
```

### Step 2: Check Environment
Create `check_env.py`:
```python
import os

print("=== ENVIRONMENT VARIABLES ===")
required = ["DISCORD_TOKEN", "DISCORD_BOT_TOKEN"]
for var in required:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: {value[:10]}...")
    else:
        print(f"❌ {var}: NOT SET")
        
print(f"MONGO_URI: {'SET' if os.getenv('MONGO_URI') else 'NOT SET'}")
print("=== END ===")
```

### Step 3: Simplified Start
Create minimal `test_start.py`:
```python
#!/usr/bin/env python3
import discord
import os
import logging

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv('DISCORD_TOKEN') or os.getenv('DISCORD_BOT_TOKEN')

if not TOKEN:
    print("❌ ERROR: No DISCORD_TOKEN found!")
    exit(1)

print(f"✅ Token found: {TOKEN[:10]}...")
print(f"✅ Discord version: {discord.__version__}")

# Create minimal bot
bot = discord.Bot() if hasattr(discord, 'Bot') else discord.Client(intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f"✅ Bot logged in as {bot.user}")
    print(f"✅ In {len(bot.guilds)} guilds")

print("🚀 Starting bot...")
bot.run(TOKEN)
```

Change start command to:
```
python test_start.py
```

If this works, the issue is in `app.py`

## Quick Fixes to Try

### Fix 1: Update Start Command
Render Dashboard → Settings → Start Command:
```
cd DISCORD\ BOT && python app.py
```
OR simpler:
```
python app.py
```

### Fix 2: Check Token
Render Dashboard → Environment → Add:
```
DISCORD_TOKEN=YOUR_ACTUAL_TOKEN_HERE
```

### Fix 3: Enable Debug Mode
Add to `app.py` at the very top:
```python
import sys
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    stream=sys.stdout
)

print("🚀 Bot starting up...")
print(f"Python: {sys.version}")
print(f"CWD: {os.getcwd()}")
```

### Fix 4: Catch All Errors
Wrap the bot.run() in try-except:
```python
try:
    bot.run(TOKEN)
except Exception as e:
    logging.error(f"FATAL: {e}", exc_info=True)
    raise
```

## Expected Working Logs

When it works, you should see:
```
✅ Successfully installed py-cord-2.7.0
[SETUP] Bot initialization complete
[INFO] Loading event_tips.py
...
[INFO] Logged in as BotName#1234
[INFO] Bot is ready
```

## Still Not Working?

1. **Check Render Logs** for the actual error (scroll up)
2. **Increase log verbosity** with DEBUG level
3. **Use the debug scripts** above to isolate the issue
4. **Check Discord Developer Portal** - bot token might be invalid/regenerated
5. **Try deploy history** - roll back to last working version

## Deploy Checklist

Before deploying:
- [ ] `requirements.txt` has `py-cord[voice]>=2.7.0` ✅
- [ ] `DISCORD_TOKEN` set in Render environment
- [ ] `MONGO_URI` set (if using MongoDB)
- [ ] Start command is correct
- [ ] All cogs have proper `async def setup(bot)` function
- [ ] No syntax errors (test locally first)
- [ ] Git pushed all changes

## Commands to Run Now

```bash
# 1. Check what's actually deployed
git log -1 --oneline

# 2. Make sure everything is committed
git status

# 3. Deploy the debug version
git add .
git commit -m "Add debug logging for Render troubleshooting"
git push

# 4. Watch Render logs closely
# Look for the ACTUAL error message
```

## Most Likely Issue

Based on the logs, the most likely issues are:

1. **Missing DISCORD_TOKEN** (80% chance)
2. **Import error** in app.py or a cog (15% chance)
3. **File path issue** on Render's filesystem (5% chance)

**Recommendation**: Check Render Environment variables FIRST!
