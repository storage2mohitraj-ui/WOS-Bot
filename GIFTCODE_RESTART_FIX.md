# Gift Code Auto-Redeem Restart Fix

## Problem
When the bot restarts, it re-detects all existing gift codes as "new" and triggers auto-redemption again, even for codes that were already redeemed by all members.

## Root Cause
The auto-redeem system tracked whether codes exist in the database, but **not** whether auto-redeem had already been triggered for those codes.

The flow was:
1. **On first run**: New code from API → Add to DB → Trigger auto-redeem ✅
2. **On restart**: Code exists in DB → Check if in DB → Already there → Skip adding
3. **But**: No tracking if auto-redeem was already triggered → Re-triggers on every restart ❌

## Solution Implemented

### 1. Added New Column: `auto_redeem_processed`

Added a new column to the `gift_codes` table to track which codes have had auto-redeem triggered:

```sql
ALTER TABLE gift_codes ADD COLUMN auto_redeem_processed INTEGER DEFAULT 0
```

- `0` = Auto-redeem not yet triggered
- `1` = Auto-redeem already triggered

### 2. Updated Code Insertion Logic

When new codes are added to the database, they're marked with `auto_redeem_processed = 0`:

```python
self.cursor.execute(
    "INSERT OR IGNORE INTO gift_codes (giftcode, date, validation_status, added_at, auto_redeem_processed) VALUES (?, ?, ?, ?, ?)",
    (code, date, "validated", datetime.now(), 0)
)
```

### 3. Check Before Triggering Auto-Redeem

Before triggering auto-redeem, the system now checks if it was already processed:

```python
# Check if this code has already been processed for auto-redeem
self.cursor.execute(
    "SELECT auto_redeem_processed FROM gift_codes WHERE giftcode = ?",
    (code,)
)
result = self.cursor.fetchone()
already_processed = result[0] if result and result[0] else 0

if already_processed:
    self.logger.info(f"Skipping auto-redeem for code {code} - already processed")
    continue
```

### 4. Mark as Processed After Triggering

After triggering auto-redeem for all guilds, the code is marked as processed:

```python
# Mark code as processed after triggering auto-redeem for all guilds
self.cursor.execute(
    "UPDATE gift_codes SET auto_redeem_processed = 1 WHERE giftcode = ?",
    (code,)
)
self.giftcode_db.commit()
```

## Files Modified

### 1. `cogs/manage_giftcode.py`

**Database Setup (Lines ~209-220)**:
- Added column migration for `auto_redeem_processed`

**API Check Task (Lines ~1279-1285)**:
- New codes inserted with `auto_redeem_processed = 0`

**Trigger Auto-Redeem (Lines ~1360-1395)**:
- Added check for `auto_redeem_processed` status
- Skip codes that are already processed
- Mark codes as processed after triggering

## Behavior

### Before Fix ❌
```
Bot Start:
  → API Check finds: CODE123 (in DB already)
  → Triggers auto-redeem for CODE123 (duplicate!)
  
Bot Restart:
  → API Check finds: CODE123 (in DB already)
  → Triggers auto-redeem for CODE123 (duplicate again!)
```

### After Fix ✅
```
Bot Start:
  → API Check finds: CODE123 (in DB, auto_redeem_processed=0)
  → Triggers auto-redeem for CODE123
  → Marks CODE123 as processed (auto_redeem_processed=1)
  
Bot Restart:
  → API Check finds: CODE123 (in DB, auto_redeem_processed=1)
  → Skips auto-redeem (already processed)
```

## Logs to Look For

### Successful Skip (Good)
```
[INFO] Skipping auto-redeem for code ABC123 - already processed
```

### First Time Processing (Good)
```
[INFO] Started auto-redeem for guild 123456 with code ABC123
[INFO] Marked code ABC123 as auto-redeem processed
```

## Migration for Existing Codes

For codes already in the database before this fix:
- They will have `auto_redeem_processed = 0` (default)
- On next API check, they will be processed once more
- Then marked as processed
- Future restarts will skip them

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS gift_codes (
    giftcode TEXT PRIMARY KEY,
    date TEXT,
    validation_status TEXT DEFAULT 'pending',
    added_by INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    auto_redeem_processed INTEGER DEFAULT 0  -- NEW COLUMN
);
```

## Benefits

✅ **No More Duplicate Auto-Redeem**: Codes are only auto-redeemed once, regardless of bot restarts  
✅ **Persistent Tracking**: State is saved in database, survives restarts  
✅ **Backward Compatible**: Existing codes get default value of 0  
✅ **Clear Logging**: Easy to see which codes are being skipped  
✅ **Resource Efficient**: Prevents unnecessary API calls and redemption attempts  

## Testing

1. Add a new gift code while bot is running
2. Verify auto-redeem triggers
3. Restart the bot
4. Check logs - should see "Skipping auto-redeem for code X - already processed"
5. Confirm no duplicate redemption attempts

---

**Status**: ✅ FIXED  
**Priority**: HIGH - Prevents spam and unnecessary API usage  
**Impact**: HIGH - Affects all servers using auto-redeem  
