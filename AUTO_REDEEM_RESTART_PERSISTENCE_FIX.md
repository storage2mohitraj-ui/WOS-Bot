# Auto-Redeem Restart Persistence Fix

## Problem
When the bot restarts, auto-redeem was being triggered again for codes that had already been redeemed. This happened because:

1. New gift codes detected from API were only saved to **SQLite** with `auto_redeem_processed = 0`
2. After auto-redeem completed, the code was marked as processed in both SQLite AND MongoDB
3. On bot restart, the startup check fetched codes from **MongoDB** (via `GiftCodesAdapter.get_all_with_status()`)
4. Since the code was never initially inserted into MongoDB, it didn't exist there
5. Therefore, the startup check didn't find it, and auto-redeem was triggered again

## Root Cause
**Missing MongoDB insertion when new codes are detected from API** (line 1372 in `manage_giftcode.py`)

The code was:
```python
# Only inserted into SQLite
self.cursor.execute(
    "INSERT OR IGNORE INTO gift_codes (giftcode, date, validation_status, added_at, auto_redeem_processed) VALUES (?, ?, ?, ?, ?)",
    (code, date, "validated", datetime.now(), 0)
)
```

But it should also insert into MongoDB immediately.

## Solution
Modified `api_check_task()` in `cogs/manage_giftcode.py` to **insert new codes into both SQLite AND MongoDB** when they are first detected from the API.

### Changes Made

#### 1. Updated MongoDB adapter imports (Line 15)
**Before:**
```python
from db.mongo_adapters import mongo_enabled, GiftCodesAdapter, AutoRedeemSettingsAdapter, AutoRedeemChannelsAdapter, GiftCodeRedemptionAdapter, AutoRedeemMembersAdapter, AutoRedeemedCodesAdapter
```

**After:**
```python
from db.mongo_adapters import mongo_enabled, GiftCodesAdapter, AutoRedeemSettingsAdapter, AutoRedeemChannelsAdapter, GiftCodeRedemptionAdapter, AutoRedeemMembersAdapter, AutoRedeemedCodesAdapter, _get_db
```

#### 2. Added fallback for _get_db (Line 23)
```python
_get_db = lambda: None
```

#### 3. Modified Code Insertion Logic (Lines 1370-1403)
**After:**
```python
for code, date in new_codes:
    try:
        # Insert into SQLite
        self.cursor.execute(
            "INSERT OR IGNORE INTO gift_codes (giftcode, date, validation_status, added_at, auto_redeem_processed) VALUES (?, ?, ?, ?, ?)",
            (code, date, "validated", datetime.now(), 0)
        )
        self.logger.info(f"Added new code to SQLite: {code}")
        
        # CRITICAL: Also insert into MongoDB if enabled
        if mongo_enabled() and GiftCodesAdapter and _get_db:
            try:
                # Insert the code with auto_redeem_processed = False
                db = _get_db()
                if db:
                    db[GiftCodesAdapter.COLL].update_one(
                        {'_id': code},
                        {
                            '$set': {
                                'date': date,
                                'validation_status': 'validated',
                                'auto_redeem_processed': False,
                                'created_at': datetime.utcnow().isoformat(),
                                'updated_at': datetime.utcnow().isoformat()
                            }
                        },
                        upsert=True
                    )
                    self.logger.info(f"✅ Added new code to MongoDB: {code}")
            except Exception as mongo_err:
                self.logger.error(f"⚠️ Failed to add code {code} to MongoDB: {mongo_err}")
                # Continue anyway - SQLite is the fallback
        
    except Exception as e:
        self.logger.error(f"Error inserting code {code}: {e}")
```

## How It Works Now

### Code Detection Flow
1. **API Check Task** detects new code from API
2. Code is inserted into **SQLite** with `auto_redeem_processed = 0`
3. Code is **ALSO** inserted into **MongoDB** with `auto_redeem_processed = False`
4. Auto-redeem is triggered for the code
5. After auto-redeem completes, code is marked as processed in **BOTH** databases

### Bot Restart Flow
1. Bot starts up
2. `process_existing_codes_on_startup()` is called
3. Fetches all codes from MongoDB via `GiftCodesAdapter.get_all_with_status()`
4. Filters for codes where `auto_redeem_processed = False`
5. **Now finds the code** because it was inserted into MongoDB at step 3 above
6. Checks if it's already processed (`auto_redeem_processed = True`)
7. **Skips the code** because it was marked as processed after the first auto-redeem
8. ✅ No duplicate auto-redeem!

## Testing
To verify the fix works:

1. **Wait for a new code to be detected** from the API (or manually add one)
2. **Verify MongoDB insertion** - Check logs for: `"✅ Added new code to MongoDB: [CODE]"`
3. **Let auto-redeem complete** - Check logs for: `"✅ Marked [CODE] as processed in MongoDB"`
4. **Restart the bot**
5. **Check startup logs** - Should see: `"⏭️ Skipping code [CODE] - already marked as processed"`
6. ✅ **Success** - Code should NOT be auto-redeemed again

## Benefits
- ✅ **Persistent tracking** - Codes are tracked in MongoDB from the moment they're detected
- ✅ **No duplicate redemptions** - Bot restart won't re-trigger auto-redeem for already-processed codes
- ✅ **Dual-database reliability** - Both SQLite and MongoDB are kept in sync
- ✅ **Graceful fallback** - If MongoDB fails, SQLite still works

## Files Modified
- `f:\STARK-whiteout survival bot\DISCORD BOT\cogs\manage_giftcode.py`
  - Lines 15: Added `_get_db` import
  - Line 23: Added `_get_db` fallback
  - Lines 1370-1403: Added MongoDB insertion when new codes are detected

## Related Code
The fix works in conjunction with:
- `GiftCodesAdapter.mark_code_processed()` - Marks code as processed after auto-redeem
- `GiftCodesAdapter.get_all_with_status()` - Retrieves codes with their processed status on startup
- `process_existing_codes_on_startup()` - Checks for unprocessed codes on bot startup
- `trigger_auto_redeem_for_new_codes()` - Triggers auto-redeem and marks codes as processed
