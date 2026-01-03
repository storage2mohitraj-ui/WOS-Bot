# Auto-Redeem Restart Fix - Summary

## Issues Identified

### 1. Repetitive Auto-Redeem on Bot Restart
**Problem**: Every time the bot restarts, the `process_existing_codes_on_startup()` function would trigger auto-redeem for all codes marked as `auto_redeem_processed = 0`, even if they were old codes that had already been processed but had database inconsistencies.

**Root Cause**: 
- The function was checking ALL unprocessed codes without any date filtering
- Database inconsistencies or migration issues could leave old codes with the wrong flag
- No mechanism to prevent re-processing of codes older than a certain threshold

**Fix Applied**:
- Added a 7-day cutoff filter to only process recent codes
- Codes older than 7 days are now skipped during startup check
- This prevents re-processing of old codes due to database inconsistencies
- Both MongoDB and SQLite queries now filter by date

### 2. Test Users with Unknown FID
**Problem**: Test users or members with invalid/unknown FIDs were being added to the auto-redeem system.

**FID Validation Rules**:
- FIDs must be exactly 9 digits
- FIDs must be numeric only
- No special characters or letters allowed

**Existing Validation**:
The code already has FID validation at line 1619 in `bot_operations.py`:
```python
fid_list = [f for f in fid_list if f and len(f) == 9 and f.isdigit()]
```

**Recommendation**:
- Manually clean up any invalid FIDs from the database
- The existing validation should prevent future invalid FIDs
- Consider adding additional validation in the auto-redeem member add flow

## Changes Made

### File: `cogs/manage_giftcode.py`

#### Modified Function: `process_existing_codes_on_startup()`

**Lines Changed**: 1503-1573

**Key Changes**:

1. **Added Date Filtering**:
   ```python
   from datetime import timedelta
   cutoff_date = datetime.now() - timedelta(days=7)
   ```

2. **MongoDB Query Enhancement**:
   - Now parses and validates code dates before processing
   - Skips codes older than 7 days
   - Handles date parsing errors gracefully

3. **SQLite Query Enhancement**:
   ```sql
   WHERE (auto_redeem_processed = 0 OR auto_redeem_processed IS NULL)
   AND (date >= ? OR date IS NULL)
   ```

4. **Improved Logging**:
   - Shows cutoff date in logs
   - Reports "recent unprocessed codes" instead of just "unprocessed codes"
   - Warns when codes are skipped due to date parsing issues

## Testing Recommendations

### 1. Verify No Repetitive Processing
1. Restart the bot
2. Check the bot logs for "STARTUP AUTO-REDEEM CHECK"
3. Verify that only recent codes (within 7 days) are processed
4. Confirm old codes are being skipped

### 2. Check Database Consistency
Run this query to check code statuses:
```python
python -c "import sqlite3; conn = sqlite3.connect('db/giftcode.sqlite'); cursor = conn.cursor(); cursor.execute('SELECT giftcode, auto_redeem_processed, date FROM gift_codes ORDER BY date DESC LIMIT 20'); [print(f'{row[0]}: processed={row[1]}, date={row[2]}') for row in cursor.fetchall()]; conn.close()"
```

### 3. Verify Auto-Redeem Members
Check for invalid FIDs:
```python
python -c "import sqlite3; conn = sqlite3.connect('db/giftcode.sqlite'); cursor = conn.cursor(); cursor.execute('SELECT guild_id, fid,  nickname FROM auto_redeem_members'); [print(f'Guild: {row[0]}, FID: {row[1]}, Nickname: {row[2]}') if not (row[1] and len(str(row[1])) == 9 and str(row[1]).isdigit()) else None for row in cursor.fetchall()]; conn.close()"
```

## Manual Cleanup (If Needed)

### Remove Test Users with Invalid FIDs

If you find any test users with invalid FIDs, run:

```python
import sqlite3
from db.mongo_adapters import mongo_enabled, AutoRedeemMembersAdapter

# Clean SQLite
conn = sqlite3.connect('db/giftcode.sqlite')
cursor = conn.cursor()

# Get all members
cursor.execute('SELECT guild_id, fid, nickname FROM auto_redeem_members')
members = cursor.fetchall()

# Find invalid FIDs
for guild_id, fid, nickname in members:
    if not fid or len(str(fid)) != 9 or not str(fid).isdigit():
        print(f'Removing invalid FID: {fid} ({nickname})')
        cursor.execute('DELETE FROM auto_redeem_members WHERE guild_id = ? AND fid = ?', (guild_id, fid))

conn.commit()
conn.close()

# Clean MongoDB (if enabled)
if mongo_enabled() and AutoRedeemMembersAdapter:
    # Get all members from MongoDB
    all_guilds = {}  # You'll need to get guild IDs
    for guild_id in all_guilds:
        members = AutoRedeemMembersAdapter.get_members(guild_id)
        for member in members:
            fid = member.get('fid', '')
            if not fid or len(str(fid)) != 9 or not str(fid).isdigit():
                print(f'Found invalid FID in MongoDB: {fid} ({member.get("nickname")})')
                # Remove using adapter
                AutoRedeemMembersAdapter.remove_member(guild_id, fid)
```

## Monitoring

### What to Watch For

1. **Startup Logs**:
   - Look for "📅 Only processing codes added after YYYY-MM-DD"
   - Verify only recent codes are being processed
   - Check for "✅ No recent unprocessed codes found" message

2. **Auto-Redeem Behavior**:
   - New codes should trigger auto-redeem once
   - After processing, code should be marked with `auto_redeem_processed = 1`
   - On next restart, that code should be skipped

3. **Member List Quality**:
   - All FIDs should be exactly 9 digits
   - No "unknown" or "test" users with invalid FIDs

## Expected Behavior After Fix

### On Bot Startup:
1. Bot waits 5 seconds for full initialization
2. Checks for codes added in the last 7 days that haven't been processed
3. Filters out any codes older than 7 days (prevents re-processing old codes)
4. Triggers auto-redeem only for recent, unprocessed codes
5. Marks those codes as processed

### On New Code Detection:
1. New code detected from API
2. Code added to database with `auto_redeem_processed = 0`
3. Auto-redeem triggered for all enabled guilds
4. Code marked as `auto_redeem_processed = 1`
5. On next restart, code will be older than the current run time, so will still be processed if within 7 days

### On Normal Operation:
- No repetitive processing for old codes
- Only genuinely new, unprocessed codes within 7 days trigger auto-redeem
- Valid FID members only (9-digit numeric)

## Rollback Plan

If issues occur, you can roll back the changes by:

1. Reverting `cogs/manage_giftcode.py` to remove the date filtering
2. Or manually marking old codes as processed:
   ```sql
   UPDATE gift_codes 
   SET auto_redeem_processed = 1 
   WHERE date < date('now', '-7 days');
   ```

## Additional Recommendations

1. **Add FID Validation to Auto-Redeem Add Flow**: 
   - Ensure all entry points for adding auto-redeem members validate FIDs
   - Add validation in any UI modals where FIDs are entered

2. **Database Maintenance**:
   - Periodically clean up old gift codes (>30 days)
   - Archive redemption history for analysis

3. **Monitoring Dashboard**:
   - Track how many codes are processed on each startup
   - Alert if more than expected codes are being reprocessed

## Contact

If you encounter any issues after this fix, check:
- Bot logs for error messages
- Database inconsistencies
- MongoDB vs SQLite synchronization

For any questions or issues, provide:
- Full bot startup logs
- Output of the database check commands above
- Description of unexpected behavior
