# Deployment Checklist - Auto-Redeem Startup Fix

## Pre-Deployment

- [x] **Code Changes Made**
  - Added `process_existing_codes_on_startup()` method
  - Enhanced `before_api_check()` to call startup check
  - Enhanced `trigger_auto_redeem_for_new_codes()` with MongoDB support
  - All changes tested with sample data

- [x] **Documentation Created**
  - AUTO_REDEEM_STARTUP_FIX.md - Detailed explanation of the fix
  - test_auto_redeem_fix.py - Test script to verify logic

## Deployment Steps

1. **Git Commit** (if using version control)
   ```bash
   git add cogs/manage_giftcode.py
   git add AUTO_REDEEM_STARTUP_FIX.md
   git add test_auto_redeem_fix.py
   git commit -m "Fix: Auto-redeem now processes existing codes on startup"
   git push
   ```

2. **Deploy to Render**
   - Push changes to your deployment branch
   - Render will automatically detect and deploy
   - Wait for deployment to complete

3. **Verify Deployment**
   - Check Render logs immediately after deployment
   - Look for these log messages:
     ```
     Gift code API check task started
     Checking for existing unprocessed gift codes on startup...
     Found X unprocessed codes in MongoDB
     Found X total unprocessed codes on startup, triggering auto-redeem...
     Started auto-redeem for guild XXXXX with code XXXXX
     ```

## Post-Deployment Verification

### Test 1: Check Startup Logs
```bash
# In Render logs, search for:
"Checking for existing unprocessed gift codes on startup"
```
**Expected:** Should appear once when bot starts  
**Status:** [ ] PASS / [ ] FAIL

### Test 2: Verify Auto-Redeem Triggers
```bash
# In Render logs, search for:
"Started auto-redeem for guild"
```
**Expected:** Should trigger for each unprocessed code automatically  
**Status:** [ ] PASS / [ ] FAIL

### Test 3: Check MongoDB Updates
```bash
# In Render logs, search for:
"Marked code .* as auto-redeem processed in MongoDB"
```
**Expected:** Codes should be marked as processed in MongoDB  
**Status:** [ ] PASS / [ ] FAIL

### Test 4: No Manual Intervention Needed
**Test:** Restart the bot on Render without running `!test`  
**Expected:** Auto-redeem should still work for unprocessed codes  
**Status:** [ ] PASS / [ ] FAIL

## Rollback Plan

If the fix doesn't work:

1. **Check Logs First**
   - Look for error messages in the startup process
   - Check if MongoDB connection is working
   - Verify auto_redeem_settings has enabled guilds

2. **If Critical Issue**
   ```bash
   git revert HEAD
   git push
   ```

3. **Alternative Test**
   - SSH into Render (if available)
   - Check database directly for unprocessed codes
   - Manually trigger with `!test` if needed

## Success Criteria

✅ Bot starts and checks for unprocessed codes automatically  
✅ Auto-redeem triggers without manual intervention  
✅ Works on Render with MongoDB  
✅ No errors in logs during startup  
✅ Existing functionality remains intact  

## Notes
- The fix is backward compatible (works with SQLite too)
- Logging is comprehensive for debugging
- MongoDB is primary, SQLite is fallback
- No breaking changes to existing code
