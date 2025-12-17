# Render Deployment Fix - Module Import Error

## Problem
The bot was failing to deploy on Render with the error:
```
ModuleNotFoundError: No module named 'db'
```

The error showed:
```
File "/opt/render/project/src/DISCORD_BOT_CLEAN/cogs/shared_views.py", line 11, in <module>
    from db.mongo_adapters import AlliancesAdapter
ModuleNotFoundError: No module named 'db'
```

## Root Cause
The issue was with how Render handles the `rootDir` configuration. When `rootDir: DISCORD_BOT_CLEAN` was set, Render was creating a confusing directory structure where:
- The repository was cloned to `/opt/render/project/src/`
- But the `rootDir` setting wasn't properly changing the working directory
- Python couldn't find the `db` module because it was looking in the wrong location

## Solution
Instead of using `rootDir`, we now explicitly navigate to the correct directory in both the build and start commands:

### Changes Made to `render.yaml`:

1. **Removed `rootDir` line** - This was causing the directory confusion

2. **Updated `buildCommand`**:
   ```yaml
   buildCommand: pip install -r DISCORD_BOT_CLEAN/requirements.txt
   ```

3. **Updated `startCommand`**:
   ```yaml
   startCommand: cd DISCORD_BOT_CLEAN && python app.py
   ```

4. **Updated `PYTHONPATH`**:
   ```yaml
   - key: PYTHONPATH
     value: "."
   ```
   Since we `cd` into `DISCORD_BOT_CLEAN` before running, the current directory (`.`) is the correct path.

## Files Modified
1. **f:/STARK-whiteout survival bot/render.yaml**
   - Removed `rootDir: DISCORD_BOT_CLEAN`
   - Updated `buildCommand` to `pip install -r DISCORD_BOT_CLEAN/requirements.txt`
   - Updated `startCommand` to `cd DISCORD_BOT_CLEAN && python app.py`
   - Updated `PYTHONPATH` to `.`

## How It Works Now
1. Render clones the repository to `/opt/render/project/src/`
2. During build, pip installs from `/opt/render/project/src/DISCORD_BOT_CLEAN/requirements.txt`
3. When starting, the command changes directory to `DISCORD_BOT_CLEAN` first
4. Then runs `python app.py` from within that directory
5. Python can now find all modules (`db`, `cogs`, etc.) because they're in the current directory

## Next Steps
1. Commit and push the updated `render.yaml` to GitHub
2. Render will automatically redeploy with the new configuration
3. The bot should now start successfully

## Verification
After deployment, check the Render logs for:
- ✅ `[SETUP] Dependencies installed successfully`
- ✅ `[SETUP] Bot initialization complete`
- ✅ Bot successfully connects to Discord
- ✅ No `ModuleNotFoundError` errors

