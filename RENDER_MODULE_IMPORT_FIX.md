# Render Deployment Fix - Module Import Error

## Problem
The bot was failing to deploy on Render with the error:
```
ModuleNotFoundError: No module named 'db'
```

## Root Cause
When Render deploys with `rootDir: DISCORD_BOT_CLEAN` in `render.yaml`, the directory structure becomes:
- `/opt/render/project/src/` - contains the contents of `DISCORD_BOT_CLEAN`

The `PYTHONPATH` was incorrectly set to `/opt/render/project`, which meant Python couldn't find the `db` module that exists in `/opt/render/project/src/db/`.

## Solution
Updated `render.yaml` to set the correct `PYTHONPATH`:

```yaml
- key: PYTHONPATH
  value: "/opt/render/project/src"
```

This ensures that when Python tries to import `db.mongo_adapters`, it looks in the correct directory (`/opt/render/project/src/db/`).

## Files Modified
1. **f:/STARK-whiteout survival bot/render.yaml**
   - Changed `PYTHONPATH` from `/opt/render/project` to `/opt/render/project/src`

## Next Steps
1. Commit and push the updated `render.yaml` to GitHub
2. Render will automatically redeploy with the new configuration
3. The bot should now start successfully

## Verification
After deployment, check the Render logs for:
- ✅ `[SETUP] Dependencies installed successfully`
- ✅ `[SETUP] Bot initialization complete`
- ✅ Bot successfully connects to Discord

If you still see import errors, verify that:
1. The `rootDir` in `render.yaml` is set to `DISCORD_BOT_CLEAN`
2. The `PYTHONPATH` is set to `/opt/render/project/src`
3. All required files exist in the `DISCORD_BOT_CLEAN` directory
