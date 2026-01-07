# Auto-Redeem Startup Fix

## Problem
The auto-redeem system was not working automatically on Render after bot restarts. Users had to manually run `!test <code>` to trigger auto-redeem every time the bot restarted.

## Root Cause
The bot's auto-redeem system had two triggers:
1. **API Check Task** - Runs every 60 seconds to fetch new codes from the API
2. **Manual Test Command** - The `!test` command for testing

However, there was **no startup check** for existing unprocessed codes in the database. When the bot restarted on Render:
- Codes already in the database with `auto_redeem_processed = 0` were ignored
- The API check task only processed *new* codes detected after startup
- Existing unprocessed codes required manual intervention via `!test`

## Solution
Added a new method `process_existing_codes_on_startup()` that:

1. **Runs on Bot Startup** - Executes before the first API check task iteration
2. **Checks for Unprocessed Codes** - Queries the database for codes with `auto_redeem_processed = 0`
3. **Triggers Auto-Redeem** - Automatically processes all unprocessed codes for enabled guilds
4. **MongoDB Support** - Works with both MongoDB (Render) and SQLite (local dev)

### Changes Made

#### 1. Enhanced `before_api_check()` Method
```python
@api_check_task.before_loop
async def before_api_check(self):
    """Wait for bot to be ready before starting API checks"""
    await self.bot.wait_until_ready()
    self.logger.info("Gift code API check task started")
    
    # Process any existing unprocessed codes on startup
    await self.process_existing_codes_on_startup()
```

#### 2. Added `process_existing_codes_on_startup()` Method
- Checks MongoDB first for unprocessed codes (Render deployment)
- Falls back to SQLite if MongoDB is unavailable (local development)
- Triggers auto-redeem for all unprocessed codes
- Logs detailed information for debugging

#### 3. Enhanced `trigger_auto_redeem_for_new_codes()` Method
- Added MongoDB support for checking auto_redeem_settings
- Added MongoDB support for marking codes as processed
- Maintains SQLite fallback for backward compatibility
- Logs source of data (MongoDB vs SQLite) for debugging

## Testing
After deploying this fix:
1. Bot will automatically process unprocessed codes on startup
2. No manual intervention (`!test`) required after restarts
3. Auto-redeem will work immediately for codes already in the database
4. The system will work on both Render (MongoDB) and local (SQLite)

## Logs to Watch
Look for these log messages to confirm it's working:
```
Gift code API check task started
Checking for existing unprocessed gift codes on startup...
Found X unprocessed codes in MongoDB/SQLite
Found X total unprocessed codes on startup, triggering auto-redeem...
Started auto-redeem for guild XXXXX with code XXXXX
Startup auto-redeem triggered for X codes
```

## Benefits
✅ Auto-redeem works immediately after bot restart on Render  
✅ No manual intervention required  
✅ Supports both MongoDB (production) and SQLite (development)  
✅ Backward compatible with existing code  
✅ Detailed logging for monitoring and debugging  
