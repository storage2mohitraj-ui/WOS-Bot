# Gift Code System Fixes and Improvements

## Issues Fixed

### 1. ❌ Infinite Retry Loop on Unknown Status Errors
**Problem**: When the API returned unknown status codes like `UNKNOWN_STATUS_RECHARGE_MONEY_VIP`, the redemption system would retry indefinitely, creating spam in logs and wasting resources.

**Fix**: 
- Added smart handling for `UNKNOWN_STATUS_*` errors
- Unknown statuses are treated as permanent failures after 3 attempts
- Added maximum retry cap of 10 attempts for all errors to prevent infinite loops
- Improved error categorization to distinguish between transient and permanent failures

**Location**: `cogs/manage_giftcode.py` - `_redeem_for_member()` method

### 2. ❌ Gift Code Auto-Detection Not Working on Render
**Problem**: When hosted on Render, the gift code poster wasn't detecting new codes or the detection was unreliable due to network issues and state persistence problems.

**Fixes**:
1. **Retry Logic**: Added exponential backoff retry (3 attempts) for fetching gift codes
2. **Enhanced Logging**: Comprehensive logging at each step to diagnose issues
3. **Dual-Write Persistence**: State is now saved to BOTH MongoDB and local file system
4. **Health Monitoring**: Added health checks that log system status periodically
5. **Error Recovery**: Better error handling with consecutive error tracking and automatic recovery

**Locations**: 
- `giftcode_poster.py` - `run_check_once()`, `start_poster()`, `mark_sent()`

### 3. ⚡ System Robustness Improvements
- Added consecutive error tracking (max 5 errors before temporary backoff)
- Implemented health check logging every ~100 checks
- Enhanced state persistence with dual-write to MongoDB + local file
- Better error messages with emojis for easier log parsing
- Graceful degradation when MongoDB is unavailable

## Error Handling Matrix

### Permanent Errors (No Retry)
These errors stop retries immediately as they won't succeed:
- `INVALID_CODE` - Code doesn't exist
- `EXPIRED` - Code has expired
- `CDK_NOT_FOUND` - Code not found in database
- `USAGE_LIMIT` - Usage limit reached
- `TIME_ERROR` - Time-based error
- `UNKNOWN_STATUS_*` (after 3 attempts) - Unknown API response

### Transient Errors (Retry with Backoff)
These errors are retried up to 10 times:
- `CAPTCHA_FETCH_ERROR` - Temporary CAPTCHA fetch issue
- `RATE_LIMITED` - Rate limiting (uses session pool)
- `CAPTCHA_TOO_FREQUENT` - CAPTCHA request too frequent
- Other temporary network/API errors

### Success States
- `SUCCESS` - Code redeemed successfully
- `ALREADY_RECEIVED` - Already redeemed (treated as success)
- `SAME TYPE EXCHANGE` - Same type already claimed (treated as success)

## Monitoring and Verification

### Check if Gift Code Poster is Running
Look for these log entries:
```
Starting giftcode poster with interval=10s
Processing X configured channels (initialized=True/False)
📊 Health check: Gift code poster healthy. Checks completed: X
```

### Check for New Code Detection
When a new code is found, you should see:
```
Successfully fetched X gift codes (attempt 1)
Found X new codes for guild XXXXX: ['CODE1', 'CODE2']
Posted X new codes to guild XXXXX
✅ State saved to MongoDB for guild XXXXX
✅ State saved to local file for guild XXXXX
✅ Dual-write success: State persisted to both MongoDB and file
```

### Check for Redemption Issues
Normal redemption flow:
```
✅ Login successful for PlayerName (attempt 1)
✅ Redeemed for PlayerName: SUCCESS (attempt 1)
```

Failed redemption (will now stop after max attempts):
```
⚠️ Unknown API status for PlayerName: RECHARGE_MONEY_VIP
Redemption attempt 1 failed for PlayerName: UNKNOWN_STATUS_RECHARGE_MONEY_VIP, retrying in 2.0s
Redemption attempt 2 failed for PlayerName: UNKNOWN_STATUS_RECHARGE_MONEY_VIP, retrying in 4.0s
Redemption attempt 3 failed for PlayerName: UNKNOWN_STATUS_RECHARGE_MONEY_VIP, retrying in 6.0s
❌ Giving up on PlayerName after 3 attempts with unknown status: RECHARGE_MONEY_VIP
```

## Configuration

### Environment Variables
```bash
# Gift code check interval (seconds)
GIFTCODE_CHECK_INTERVAL=10  # Default: 10 seconds

# MongoDB connection (optional, falls back to SQLite)
MONGODB_URI=mongodb://...
```

### Key Settings in Code
- **Check Interval**: 10 seconds (DEFAULT_INTERVAL in giftcode_poster.py)
- **Max Fetch Retries**: 3 attempts with exponential backoff
- **Max Redemption Retries**: 10 attempts for temporary errors, 3 for unknown errors
- **Max Consecutive Errors**: 5 before increasing interval
- **Concurrent Redemptions**: 2 simultaneous (configurable in manage_giftcode.py)

## Testing on Render

### 1. Deploy the fixes
Push the updated code to your Render deployment.

### 2. Monitor the logs
Watch for the startup sequence:
```bash
render logs --tail
```

Look for:
- `Starting giftcode poster with interval=10s`
- `Processing X configured channels`
- Health check logs every ~100 checks

### 3. Test with a new code
Add a test gift code through the API or manually, then verify:
- The poster detects it within 10 seconds
- The code is posted to configured channels
- State is persisted (check for dual-write success logs)

### 4. Verify auto-redemption
If auto-redemption is enabled:
- New codes should trigger automatic redemption
- Check logs for redemption progress
- Verify no infinite retry loops on errors

## Troubleshooting

### Poster not detecting codes
1. Check if channels are configured: Look for configured channel IDs in logs
2. Verify MongoDB/file state persistence: Should see dual-write success logs
3. Check fetch errors: Look for "Error fetching codes" in logs
4. Verify bot has access to configured channels

### Redemption stuck in retry loop
1. Check the error message - should now cap at 3-10 attempts
2. Look for "Giving up on" or "Max retry attempts reached" messages
3. Review the actual API status being returned

### State not persisting on Render
1. Verify MongoDB connection (check logs for MongoDB errors)
2. Ensure write permissions for local file system (Render ephemeral storage)
3. Look for "CRITICAL: Failed to persist state" errors

### High error rate
1. Check consecutive error counter in logs
2. Look for "Too many consecutive errors" messages
3. Verify API connectivity and rate limiting

## Best Practices for Render Deployment

1. **Enable MongoDB**: For persistent state across restarts
2. **Monitor Logs**: Regularly check logs for health checks and errors
3. **Set Alerts**: Configure alerts for "CRITICAL" log entries
4. **Check Resources**: Ensure adequate CPU/memory for concurrent operations
5. **Regular Health Checks**: Look for the 📊 health check logs

## Support

If issues persist after these fixes:
1. Check the logs for specific error messages
2. Verify MongoDB connection if using it
3. Ensure bot has proper permissions in Discord channels
4. Check network connectivity to WOS API
5. Review rate limiting configurations

---

**Last Updated**: 2025-12-20
**Version**: 2.0 - Robust and Production-Ready
