# Auto-Redeem Persistence Fix

## Problem

Every time the bot restarts on Render, auto-redeem in `/manage` was being disabled and required manual re-enabling.

## Root Cause Analysis

1. **Missing MongoDB Adapter Method**: The `AutoRedeemSettingsAdapter` class in `db/mongo_adapters.py` was missing the `get_all_settings()` method, which prevented the bot from retrieving all guilds' auto-redeem settings on startup.

2. **No SQLite to MongoDB Sync**: When the bot enables auto-redeem via `/manage` → Configure Auto Redeem → Enable, the settings were being saved to both SQLite and MongoDB. However, on Render restart:
   - SQLite data is lost (ephemeral filesystem)
   - MongoDB data persists, but the code was falling back to empty SQLite

3. **No Startup Restoration**: There was no mechanism to restore auto-redeem enabled states from MongoDB on startup.

## Solution Applied

### 1. Added `get_all_settings()` to `AutoRedeemSettingsAdapter`

**File**: `db/mongo_adapters.py`

```python
@staticmethod
def get_all_settings() -> list:
    """Get all auto redeem settings for all guilds (used on startup to restore state)"""
    try:
        db = _get_db()
        docs = list(db[AutoRedeemSettingsAdapter.COLL].find({}))
        settings_list = []
        for doc in docs:
            settings = {
                'guild_id': int(doc.get('guild_id', doc.get('_id', 0))),
                'enabled': bool(doc.get('enabled', False)),
                'updated_by': int(doc.get('updated_by', 0)) if doc.get('updated_by') else 0,
                'updated_at': doc.get('updated_at')
            }
            settings_list.append(settings)
        logger.info(f'Retrieved {len(settings_list)} auto redeem settings from MongoDB')
        return settings_list
    except Exception as e:
        logger.error(f'Failed to get all auto redeem settings: {e}')
        return []
```

### 2. Added Startup Sync Function

**File**: `cogs/manage_giftcode.py`

Added `sync_auto_redeem_settings_to_mongo()` function that runs before the API check task:

- Reads enabled guilds from SQLite
- Syncs them to MongoDB if not already present
- Reports the sync status in logs

This ensures that on the first startup after implementing this fix, any existing SQLite settings get migrated to MongoDB.

### 3. Updated `before_api_check()` Hook

The startup sequence now:
1. Waits for bot ready
2. **Syncs SQLite settings to MongoDB** (new)
3. Processes existing unprocessed codes

## How It Works Now

### On Enable (via /manage → Configure Auto Redeem → Enable):
1. Settings saved to MongoDB ✅
2. Settings saved to SQLite (backup) ✅
3. Logs confirm MongoDB persistence

### On Bot Startup:
1. Bot connects to Discord
2. `sync_auto_redeem_settings_to_mongo()` runs:
   - Reads any enabled guilds from SQLite
   - Saves them to MongoDB if not already present
   - Reports enabled guild count from MongoDB
3. `trigger_auto_redeem_for_new_codes()` queries MongoDB for enabled guilds
4. Auto-redeem works correctly for all enabled guilds

### On Render Restart:
1. SQLite is reset (ephemeral) 
2. MongoDB persists all settings ✅
3. Bot starts and loads settings from MongoDB ✅
4. Auto-redeem continues working without manual intervention ✅

## Files Modified

1. `db/mongo_adapters.py` - Added `get_all_settings()` method
2. `cogs/manage_giftcode.py` - Added sync function and updated startup hook

## Verification

After deploying:
1. Enable auto-redeem via `/manage` → Gift Code Management → Auto Redeem → Configure → Enable
2. Check logs for "MongoDB: Successfully saved auto-redeem ENABLED"
3. Restart bot on Render
4. Check logs for "MongoDB already has X enabled guilds"
5. Auto-redeem should work without re-enabling

## Technical Details

- MongoDB Collection: `auto_redeem_settings`
- Document Structure:
  ```json
  {
    "_id": "guild_id_string",
    "guild_id": 123456789,
    "enabled": true,
    "updated_by": 987654321,
    "updated_at": "2024-12-26T12:00:00.000Z",
    "created_at": "2024-12-26T10:00:00.000Z"
  }
  ```
