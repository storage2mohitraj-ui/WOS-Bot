# 🎁 Gift Code v1.4.0 Integration Guide

## Overview
This guide helps you integrate the v1.4.0 gift code system enhancements extracted from https://github.com/whiteout-project/bot/releases/tag/v1.4.0 into your Discord bot.

## 📦 What's Included

### New Features
1. **VIP-Only Code Support** - Automatically detect and skip members without VIP for VIP-only codes
2. **Furnace Level Validation** - Validate minimum furnace level requirements
3. **Code Reactivation Detection** - Detect when expired codes become active again
4. **Enhanced Error Handling** - Better categorization and handling of redemption errors
5. **Redemption Priority Queue** - Prioritize VIP members and high-level players

### Files Created
- `gift_code_v14_enhancements.py` - Main enhancement module
- `GIFTCODE_V1.4.0_FEATURES.md` - Feature documentation
- `GIFTCODE_V1.4.0_INTEGRATION.md` - This integration guide

## 🚀 Quick Start Integration

### Step 1: Database Setup

Run this to create the new v1.4.0 tables:

```python
python integrate_v14_enhancements.py --setup-database
```

Or manually:

```python
from gift_code_v14_enhancements import GiftCodeV14Schema
from db_utils import get_db_connection

db = get_db_connection('giftcode.sqlite')
GiftCodeV14Schema.setup_all_tables(db)
```

### Step 2: Integrate into ManageGiftCode Cog

#### Option A: Automatic Integration (Recommended)

```bash
python integrate_v14_enhancements.py --auto-integrate
```

#### Option B: Manual Integration

Edit `cogs/manage_giftcode.py`:

```python
# At the top of the file, add import
from gift_code_v14_enhancements import GiftCodeV14Integrator

# In ManageGiftCode.__init__ method, after database setup:
def __init__(self, bot):
    # ... existing code ...
    
    # Initialize v1.4.0 features
    try:
        from gift_code_v14_enhancements import GiftCodeV14Schema, GiftCodeV14Integrator
        GiftCodeV14Schema.setup_all_tables(self.giftcode_db)
        self.v14 = GiftCodeV14Integrator(self, self.giftcode_db)
        self.logger.info("✨ Gift Code v1.4.0 features enabled")
    except Exception as e:
        self.logger.error(f"Failed to initialize v1.4.0 features: {e}")
        self.v14 = None
```

### Step 3: Update Redemption Logic

In the `_redeem_for_member` method, add checks before redemption:

```python
async def _redeem_for_member(self, guild_id, fid, nickname, furnace_lv, giftcode):
    # NEW: Check if member should be skipped (VIP/furnace requirements)
    if hasattr(self, 'v14') and self.v14:
        should_skip, reason = await self.v14.should_skip_member(
            fid, nickname, furnace_lv, giftcode
        )
        if should_skip:
            self.logger.info(reason)
            return ("SKIPPED", 0, 0, 0)
    
    # ... existing login and redemption code ...
    
    # After redemption attempt
    status, img, code, method = await self.attempt_gift_code_with_api(fid, giftcode, session)
    
    # NEW: Enhanced error handling
    if hasattr(self, 'v14') and self.v14:
        error_info = await self.v14.handle_redemption_error(status, giftcode, fid, nickname)
        
        # If permanent error (VIP/furnace), don't retry
        if error_info['is_permanent'] and not error_info['category'] == 'SUCCESS':
            return (status, 0, 0, 1)
    
    # Continue with existing retry logic...
```

### Step 4: Add Reactivation Detection

In your code validation logic (e.g. in `GiftOperations` cog):

```python
# When validating a code
async def validate_code(self, giftcode):
    # ... existing validation ...
    
    # NEW: Check for reactivation
    if hasattr(self.manage_giftcode_cog, 'v14') and self.manage_giftcode_cog.v14:
        reactivated = await self.manage_giftcode_cog.v14.check_code_reactivation(
            giftcode, current_status
        )
        if reactivated:
            self.logger.info(f"🔄 Code '{giftcode}' was reactivated - triggering auto-redeem")
            # Trigger auto-redeem for all guilds
```

## 📋 Configuration

### Setting Alliance Priority

Higher priority alliances get codes redeemed first:

```python
# In Discord command or admin panel
from gift_code_v14_enhancements import RedemptionPriorityQueue

priority_queue = RedemptionPriorityQueue(db_connection)

# Set alliance 123 to high priority (1) in guild 456
priority_queue.set_alliance_priority(guild_id=456, alliance_id=123, priority=1)

# Priority levels:
# 0 = Normal (default)
# 1 = High (VIP members, main alliance)
# 2 = Critical (testing, admin alliance)
```

### Marking VIP Members

```python
from gift_code_v14_enhancements import VIPValidator

vip_validator = VIPValidator(db_connection)

# Update member VIP status
vip_validator.update_member_vip_status(
    fid="12345", 
    is_vip=True, 
    vip_level=5
)
```

### Setting Code Requirements

```python
from gift_code_v14_enhancements import VIPValidator, FurnaceLevelValidator

# Mark code as VIP-only
vip_validator = VIPValidator(db_connection)
vip_validator.record_vip_requirement("VIPCODE2024")

# Set furnace level requirement
furnace_validator = FurnaceLevelValidator(db_connection)
furnace_validator.record_furnace_requirement("HIGHLEVELCODE", min_level=30)
```

## 🧪 Testing

### Test VIP Detection

```python
from gift_code_v14_enhancements import VIPValidator

vip_val = VIPValidator(db)

# Test VIP error detection
assert vip_val.is_vip_required_error("RECHARGE_MONEY_VIP")
assert vip_val.is_vip_required_error("VIP_REQUIREMENT_NOT_MET")

# Test VIP member check
vip_val.update_member_vip_status("12345", True, 5)
is_vip, level = vip_val.is_member_vip("12345")
assert is_vip == True
assert level == 5

print("✅ VIP Detection tests passed")
```

### Test Furnace Level Validation

```python
from gift_code_v14_enhancements import FurnaceLevelValidator

furnace_val = FurnaceLevelValidator(db)

# Set requirement
furnace_val.record_furnace_requirement("TESTCODE", min_level=25)

# Test validation
meets, msg = furnace_val.meets_furnace_requirement(30, "TESTCODE")
assert meets == True

meets, msg = furnace_val.meets_furnace_requirement(20, "TESTCODE")
assert meets == False

print("✅ Furnace Level tests passed")
```

### Test Code Reactivation

```python
from gift_code_v14_enhancements import CodeReactivationDetector

detector = CodeReactivationDetector(db)

# Simulate reactivation
reactivated = await detector.detect_reactivation(
    "EXPIREDCODE", 
    current_status="SUCCESS",
    previous_status="EXPIRED"
)
assert reactivated == True

print("✅ Reactivation Detection tests passed")
```

## 📊 Monitoring

### Check VIP-Only Codes

```sql
SELECT code, vip_required, min_furnace_level, reactivated 
FROM gift_code_requirements 
WHERE vip_required = 1;
```

### View Reactivation History

```sql
SELECT code, previous_status, reactivated_at 
FROM code_reactivation_history 
ORDER BY reactivated_at DESC 
LIMIT 10;
```

### Check Alliance Priorities

```sql
SELECT guild_id, alliance_id, priority_level 
FROM alliance_redemption_priority 
ORDER BY priority_level DESC;
```

### View VIP Members

```sql
SELECT fid, is_vip, vip_level, last_updated 
FROM member_vip_status 
WHERE is_vip = 1
ORDER BY vip_level DESC;
```

## 🔧 Troubleshooting

### Issue: VIP detection not working
- Ensure member VIP status is being updated from player data
- Check if `fetch_and_update_vip_status` is called after  fetching player info
- Verify VIP fields in API response match expected format

### Issue: Furnace requirements not detected
- Check if error messages contain furnace level keywords
- Manually record requirements for known codes
- Update `FURNACE_LEVEL_ERRORS` list if needed

### Issue: Code reactivation not clearing history
- Verify permissions on database
- Check if `clear_redemption_history` has correct table names
- Ensure MongoDB adapters (if used) support deletion

## 🎯 Next Steps

1. **Deploy to Production**
   ```bash
   git add gift_code_v14_enhancements.py
   git commit -m "Add v1.4.0 gift code enhancements"
   git push
   ```

2. **Monitor Logs**
   Look for:
   - `💎 Marked code 'X' as VIP-required`
   - `🏭 Marked code 'X' as requiring furnace level Y+`
   - `🔄 Code reactivation detected`
   - `✨ Gift Code v1.4.0 features enabled`

3. **Configure Priorities**
   - Set VIP/main alliances to priority 1
   - Set testing alliances to priority 2

4. **Update VIP Status**
   - Ensure VIP status updates when fetching player data
   - Run batch update for existing members if needed

## 📖 Reference

### Error Categories

- `SUCCESS` - Redemption successful
- `VIP_REQUIRED` - Code requires VIP status (permanent)
- `FURNACE_LEVEL_REQUIRED` - Code requires higher furnace level (permanent)
- `INVALID_CODE` - Code invalid/expired (permanent)
- `RATE_LIMITED` - Too many requests (temporary, retry)
- `TEMPORARY_ERROR` - Network/timeout error (temporary, retry)
- `UNKNOWN` - Unrecognized error (limited retry)

### Priority Levels

- `0` - Normal priority (default all alliances)
- `1` - High priority (VIP members, main alliance)
- `2` - Critical priority (testing, admin alliance)

## ✅ Success Indicators

After integration, you should see:
- ✅ New database tables created
- ✅ VIP members skipped for non-VIP codes
- ✅ Low-level members skipped for high-level codes
- ✅ Reactivated codes trigger new redemptions
- ✅ Better error messages in logs
- ✅ Reduced failed redemption attempts

---

**Version**: 1.4.0
**Status**: Ready for Integration
**Compatibility**: Requires Python 3.8+, Discord.py 2.0+

For questions or issues, refer to `GIFTCODE_V1.4.0_FEATURES.md`
