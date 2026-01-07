# Auto-Redeem Persistence Fix - MongoDB Tracking

## Problem
Every time the bot restarts, it was re-attempting to auto-redeem the same gift codes for all members, even if they had already redeemed them successfully. This was causing:
- Duplicate redemption attempts
- Unnecessary API calls
- "ALREADY_RECEIVED" responses flooding the logs
- Poor user experience

## Root Cause
The previous system only tracked if a code had been **triggered** for auto-redeem (using the `auto_redeem_processed` flag), but it didn't track **which specific members** had successfully redeemed each code. On restart, the system would:
1. Check if `auto_redeem_processed = 0` 
2. If true, trigger auto-redeem for ALL members again
3. Result: Members who already redeemed would get "ALREADY_RECEIVED" responses

## Solution: Per-Member Redemption Tracking

### 1. New MongoDB Collection: `auto_redeemed_codes`
Created a new adapter `AutoRedeemedCodesAdapter` that tracks redemptions at the **guild/code/FID level**:

**Document Structure:**
```javascript
{
  _id: "guild_id:CODE:fid",  // Composite key
  guild_id: 123456789,
  code: "GIFTCODE123",
  fid: "player_fid_here",
  status: "success",  // or "already_redeemed"
  redeemed_at: "2025-12-26T12:00:00Z",
  created_at: "2025-12-26T12:00:00Z",
  updated_at: "2025-12-26T12:00:00Z"
}
```

**Key Methods:**
- `is_code_redeemed_for_member(guild_id, code, fid)` - Check if a specific member redeemed a code
- `mark_code_redeemed_for_member(guild_id, code, fid, status)` - Mark a code as redeemed for a member
- `get_redeemed_members_for_code(guild_id, code)` - Get all FIDs that redeemed a code
- `is_code_fully_processed_for_guild(guild_id, code)` - Check if ANY member redeemed (startup check)
- `get_stats_for_guild(guild_id)` - Get redemption statistics

### 2. Enhanced `GiftCodesAdapter`
Added new methods to `GiftCodesAdapter` for better code tracking:

**New Methods:**
- `get_code(code)` - Get a specific code's details with `auto_redeem_processed` status
- `mark_code_processed(code)` - Mark a code as globally processed
- `reset_code_processed(code)` - Reset processed status (for re-triggering)
- `get_all_with_status()` - Get all codes with their processed status

### 3. Updated `_redeem_for_member` Method
Now tracks each successful redemption in MongoDB:

```python
# After successful redemption
if redemption_successful or final_status == "ALREADY_RECEIVED":
    AutoRedeemedCodesAdapter.mark_code_redeemed_for_member(
        guild_id=guild_id,
        code=giftcode,
        fid=str(fid),
        status="success" if redemption_successful else "already_redeemed"
    )
```

### 4. Updated `process_auto_redeem` Method
**Before:** Attempted redemption for ALL members every time

**After:** 
1. Gets all auto-redeem members
2. **Checks MongoDB** for each member to see if they already redeemed the code
3. Filters out members who already redeemed
4. Only processes remaining members
5. Shows "All members already redeemed" message if everyone has redeemed

```python
# Filter members who haven't redeemed yet
for member in members_data:
    already_redeemed = AutoRedeemedCodesAdapter.is_code_redeemed_for_member(
        guild_id, giftcode, fid
    )
    if not already_redeemed:
        members_to_process.append(member)
```

### 5. Updated `process_existing_codes_on_startup` Method
**Before:** Assumed all MongoDB codes were unprocessed

**After:** Properly checks `auto_redeem_processed` status from MongoDB:

```python
# Get codes with status
all_codes = GiftCodesAdapter.get_all_with_status()
unprocessed_codes = [
    (code['giftcode'], code['date'])
    for code in all_codes
    if not code.get('auto_redeem_processed', False)
]
```

## Files Modified

### 1. `db/mongo_adapters.py`
- **Added:** `AutoRedeemedCodesAdapter` class with 6 methods
- **Enhanced:** `GiftCodesAdapter` with 4 new methods
- **Lines Added:** ~200 lines

### 2. `cogs/manage_giftcode.py`
- **Updated imports:** Added `AutoRedeemedCodesAdapter`
- **Enhanced:** `_redeem_for_member()` to track per-member redemptions
- **Enhanced:** `process_auto_redeem()` to filter already-redeemed members
- **Enhanced:** `process_existing_codes_on_startup()` to properly check MongoDB status
- **Lines Modified:** ~80 lines

## How It Works Now

### Scenario 1: New Code Added
1. API detects new code `WINTER2025`
2. Code added to MongoDB with `auto_redeem_processed: false`
3. Auto-redeem triggered for all enabled guilds
4. For each guild, system checks which members haven't redeemed yet
5. Processes only members who haven't redeemed
6. Each successful redemption is tracked in `auto_redeemed_codes` collection
7. Code marked as `auto_redeem_processed: true` globally

### Scenario 2: Bot Restart
1. Bot starts up
2. Calls `process_existing_codes_on_startup()`
3. Fetches all codes from MongoDB with status
4. Filters for codes with `auto_redeem_processed: false`
5. For each unprocessed code:
   - Gets enabled guilds
   - For each guild, gets auto-redeem members
   - **Checks MongoDB to see which members already redeemed**
   - Only processes members who haven't redeemed yet
6. If all members already redeemed, sends "All members already redeemed" message

### Scenario 3: Partial Completion
If auto-redeem was processing and bot crashes:
1. Some members redeemed successfully (tracked in MongoDB)
2. Some members didn't get processed
3. On restart:
   - Code is still `auto_redeem_processed: false`
   - System checks MongoDB for each member
   - **Skips members who already redeemed**
   - **Only processes remaining members**
4. No duplicate redemptions!

## Benefits

✅ **No More Duplicates:** Each member is only processed once per code
✅ **Crash-Resistant:** System resumes from where it left off
✅ **Efficient:** Skips already-processed members, saves API calls
✅ **Transparent:** Shows "X members skipped (already redeemed)" in messages
✅ **Persistent:** All tracking survives bot restarts via MongoDB
✅ **Per-Guild:** Same code can be processed independently for each guild
✅ **Auditable:** Full history of who redeemed what and when

## Testing Checklist

- [ ] Add new code via API → Should auto-redeem for all members
- [ ] Restart bot → Should NOT re-redeem already processed codes
- [ ] Add code manually while bot running → Should trigger auto-redeem
- [ ] Restart bot mid-redemption → Should resume with remaining members only
- [ ] Check MongoDB collections:
  - [ ] `gift_codes` has codes with `auto_redeem_processed` status
  - [ ] `auto_redeemed_codes` has per-member redemption records
- [ ] Verify logs show "Skipping X (already redeemed)" messages
- [ ] Verify channel messages show "All members already redeemed" when applicable

## MongoDB Collections Used

1. **`gift_codes`** - Stores all gift codes
   - `auto_redeem_processed`: Boolean flag
   - `auto_redeem_processed_at`: Timestamp

2. **`auto_redeemed_codes`** (NEW) - Tracks per-member redemptions
   - Composite key: `guild_id:CODE:fid`
   - Tracks which members redeemed which codes

3. **`auto_redeem_settings`** - Tracks enabled/disabled state per guild
4. **`auto_redeem_channels`** - Tracks import channel per guild
5. **`auto_redeem_members`** - Tracks which members to auto-redeem for

## Migration Notes

**Existing Deployments:**
- No migration needed - new collections will be created automatically
- Existing codes will work fine - they'll just be processed once more on next restart
- After that, the new tracking will prevent duplicates

**Clean Slate:**
- System will work immediately with no setup required
