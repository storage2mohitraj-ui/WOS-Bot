# 🎁 v1.4.0 Integration Checklist

## ✅ Pre-Integration

- [x] Files created:
  - [x] `gift_code_v14_enhancements.py` - Main module
  - [x] `integrate_v14_enhancements.py` - Integration script
  - [x] `GIFTCODE_V1.4.0_FEATURES.md` - Feature docs
  - [x] `GIFTCODE_V1.4.0_INTEGRATION.md` - Integration guide
  - [x] `GIFTCODE_V1.4.0_QUICKREF.md` - Quick reference
  - [x] `GIFTCODE_V1.4.0_SUMMARY.md` - Summary
  - [x] `GIFTCODE_V1.4.0_CHECKLIST.md` - This file

## 📋 Integration Steps

### Step 1: Database Setup
- [ ] Run: `python integrate_v14_enhancements.py --setup-database`
- [ ] Verify 4 new tables created:
  - [ ] `member_vip_status`
  - [ ] `gift_code_requirements`
  - [ ] `alliance_redemption_priority`
  - [ ] `code_reactivation_history`
- [ ] Check: `python integrate_v14_enhancements.py --status`

### Step 2: Backup (Optional but Recommended)
- [ ] Backup `giftcode.sqlite`
- [ ] Backup `cogs/manage_giftcode.py`

### Step 3: Update ManageGiftCode Cog
- [ ] Open `cogs/manage_giftcode.py`
- [ ] Add import at top:
  ```python
  from gift_code_v14_enhancements import GiftCodeV14Integrator
  ```
- [ ] Add to `__init__` (after `self.setup_database()`):
  ```python
  try:
      from gift_code_v14_enhancements import GiftCodeV14Schema
      GiftCodeV14Schema.setup_all_tables(self.giftcode_db)
      self.v14 = GiftCodeV14Integrator(self, self.giftcode_db)
      self.logger.info("✨ Gift Code v1.4.0 features enabled")
  except Exception as e:
      self.logger.error(f"Failed to initialize v1.4.0: {e}")
      self.v14 = None
  ```
- [ ] Add to `_redeem_for_member` (before login, line ~498):
  ```python
  # Check if member should be skipped
  if hasattr(self, 'v14') and self.v14:
      should_skip, reason = await self.v14.should_skip_member(
          fid, nickname, furnace_lv, giftcode
      )
      if should_skip:
          self.logger.info(reason)
          return ("SKIPPED", 0, 0, 0)
  ```
- [ ] Add to `_redeem_for_member` (after redemption, line ~573):
  ```python
  # Enhanced error handling
  if hasattr(self, 'v14') and self.v14:
      error_info = await self.v14.handle_redemption_error(
          status, giftcode, fid, nickname
      )
      if error_info['is_permanent'] and error_info['category'] not in ['SUCCESS']:
          return (status, 0, 0, 1)
  ```
- [ ] Save file

### Step 4: Testing
- [ ] Run tests: `python integrate_v14_enhancements.py --test`
- [ ] Check all tests pass:
  - [ ] VIP Validator tests
  - [ ] Furnace Level Validator tests
  - [ ] Redemption Priority Queue tests
  - [ ] Enhanced Error Handler tests

### Step 5: Restart Bot
- [ ] Stop bot (Ctrl+C if running)
- [ ] Start bot: `python app.py`
- [ ] Check logs for: `✨ Gift Code v1.4.0 features enabled`
- [ ] No errors during startup

### Step 6: Verify Integration
- [ ] Run status check: `python integrate_v14_enhancements.py --status`
- [ ] Verify all tables exist with ✅
- [ ] Verify cog integration shows ✅
- [ ] Check bot logs for v1.4.0 messages

## 🧪 Post-Integration Testing

### Test VIP Detection
- [ ] Trigger redemption with code that requires VIP
- [ ] Check logs for: `💎 Marked code 'X' as VIP-required`
- [ ] Verify non-VIP members are skipped
- [ ] Check logs for: `💎 {nickname} - Skipped (VIP required)`

### Test Furnace Level Validation
- [ ] Trigger redemption with code requiring high furnace level
- [ ] Check logs for: `🏭 Marked code 'X' as requiring furnace level Y+`
- [ ] Verify low-level members are skipped
- [ ] Check logs for: `🏭 {nickname} - Skipped (Furnace level too low)`

### Test Error Handling
- [ ] Check various error types are categorized correctly
- [ ] Verify permanent errors don't retry
- [ ] Verify temporary errors do retry with backoff
- [ ] Check logs for clear error messages

### Test Code Reactivation (Optional)
- [ ] Manually test reactivation detector (if possible)
- [ ] Or wait for natural reactivation event
- [ ] Check logs for: `🔄 Code reactivation detected`

## 🎯 Configuration (Optional)

### Set Alliance Priorities
- [ ] Identify VIP/main alliances
- [ ] Run Python script to set priority:
  ```python
  from gift_code_v14_enhancements import RedemptionPriorityQueue
  from db_utils import get_db_connection
  
  db = get_db_connection('giftcode.sqlite')
  pq = RedemptionPriorityQueue(db)
  
  # Set your main alliance to high priority
  pq.set_alliance_priority(guild_id=YOUR_GUILD_ID, alliance_id=YOUR_ALLIANCE_ID, priority=1)
  ```

### Mark Known VIP Codes
- [ ] List known VIP-only codes
- [ ] Mark them manually:
  ```python
  from gift_code_v14_enhancements import VIPValidator
  from db_utils import get_db_connection
  
  db = get_db_connection('giftcode.sqlite')
  vip_val = VIPValidator(db)
  
  vip_val.record_vip_requirement("KNOWN_VIP_CODE")
  ```

### Mark Known Furnace Requirements
- [ ] List known high-level codes
- [ ] Mark requirements:
  ```python
  from gift_code_v14_enhancements import FurnaceLevelValidator
  from db_utils import get_db_connection
  
  db = get_db_connection('giftcode.sqlite')
  fv = FurnaceLevelValidator(db)
  
  fv.record_furnace_requirement("HIGHLEVEL_CODE", min_level=30)
  ```

## 📊 Monitoring

### Daily Checks
- [ ] Review logs for v1.4.0 messages
- [ ] Check skip rates (how many members skipped)
- [ ] Monitor failed redemptions (should be lower)
- [ ] Check for reactivation events

### Weekly Review
- [ ] Check database for new VIP-only codes detected
- [ ] Review furnace requirements detected
- [ ] Analyze priority queue effectiveness
- [ ] Update alliance priorities if needed

### Monthly Audit
- [ ] Review all gift code requirements
- [ ] Clean up old reactivation history
- [ ] Update VIP status for members (if API available)
- [ ] Optimize priority settings

## 📈 Success Metrics

After integration, track:
- [ ] Failed redemption rate (should decrease 30-50%)
- [ ] Auto-skip rate (how many members automatically skipped)
- [ ] Processing time (should be faster due to skips)
- [ ] VIP code detection accuracy
- [ ] Furnace level validation accuracy

## 🐛 Troubleshooting

If issues occur:

### Bot won't start
```powershell
# Check syntax errors in edited file
python -m py_compile cogs/manage_giftcode.py

# Check detailed error logs
python app.py 2>&1 | Select-String -Pattern "error|exception" -Context 2
```

### v1.4.0 features not enabled
- [ ] Check import path is correct
- [ ] Verify `gift_code_v14_enhancements.py` exists
- [ ] Check bot logs for exact error message
- [ ] Verify database tables were created

### Tables not created
```powershell
# Manually run setup
python integrate_v14_enhancements.py --setup-database

# Verify tables exist
python
>>> import sqlite3
>>> db = sqlite3.connect('giftcode.sqlite')
>>> cursor = db.cursor()
>>> cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
>>> print(cursor.fetchall())
```

### Tests failing
```powershell
# Run specific test with debug
python integrate_v14_enhancements.py --test

# Check database permissions
# Ensure giftcode.sqlite is writable
```

## ✅ Integration Complete!

Once all checkboxes are checked:
- [ ] v1.4.0 features fully integrated
- [ ] All tests passing
- [ ] Bot running with new features
- [ ] Monitoring in place
- [ ] Documentation reviewed

## 🎉 Congratulations!

You've successfully integrated the v1.4.0 giftcode redeem system from https://github.com/whiteout-project/bot/releases/tag/v1.4.0

Enjoy:
- ✅ Automatic VIP detection and skipping
- ✅ Furnace level validation
- ✅ Smart code reactivation handling
- ✅ Enhanced error categorization
- ✅ Priority-based redemption
- ✅ Fewer failed redemptions
- ✅ Better UX for your users

---

**Need Help?**
- See: `GIFTCODE_V1.4.0_INTEGRATION.md` for detailed steps
- See: `GIFTCODE_V1.4.0_QUICKREF.md` for quick commands
- See: `GIFTCODE_V1.4.0_FEATURES.md` for feature details
- See: `gift_code_v14_enhancements.py` for code documentation
