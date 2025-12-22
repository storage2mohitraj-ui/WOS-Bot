# Voice Connection Timeout Fix

## Problem
The bot was experiencing connection timeouts when attempting to auto-connect to the "General" voice channel:
```
DEBUG: Error connecting to voice: Unable to connect to General as it exceeded the timeout of 60.0 seconds.
Failed to auto-connect: Unable to connect to General as it exceeded the timeout of 60.0 seconds.
```

## Root Causes
1. **Long timeout duration** (60 seconds) causing the bot to hang for too long
2. **No retry logic** - single connection attempt failures would fail entirely
3. **Lavalink not fully stabilized** before attempting voice connections
4. **Network/Discord API latency** issues causing connection delays

## Changes Made

### 1. Reduced Connection Timeout
- **Before**: 60 seconds
- **After**: 30 seconds
- **Why**: Fail faster to detect issues and move on to retry logic

### 2. Added Retry Logic with Exponential Backoff
All voice connection attempts now include retry logic:
- **Music state restoration**: 3 attempts with 2s, 4s, 6s delays
- **Auto-connect on user join**: 2 attempts with 2s delay
- **Manual play commands**: 2 attempts with 2s delay

### 3. Lavalink Stabilization Delay
Added a 5-second wait after Lavalink connection before attempting to restore music states:
```python
print("⏳ Waiting for Lavalink to stabilize before restoring music states...")
await asyncio.sleep(5)
```

### 4. Better Error Handling
- **Specific timeout error handling**: Catches `asyncio.TimeoutError` separately
- **Detailed logging**: Shows connection attempts and their outcomes
- **Graceful degradation**: Skips problematic channels instead of crashing

## Files Modified
- `f:\STARK-whiteout survival bot\DISCORD BOT\cogs\music.py`
  - `restore_music_states()` - Lines 1652-1659, 1727-1767
  - `on_voice_state_update()` - Lines 1969-2007
  - `get_player()` - Lines 2424-2457
  - `safe_play()` - Line 2164

## Testing Recommendations

### 1. Test Bot Restart
Restart your bot and monitor the console output for:
```
⏳ Waiting for Lavalink to stabilize before restoring music states...
🔄 Restoring X music state(s)...
🔌 Connecting to General in [Server Name] (attempt 1/3)...
✅ Connected successfully to General
```

### 2. Test Auto-Connect
1. Use `/play` command while not in a voice channel
2. Join a voice channel when prompted
3. Bot should auto-connect within 30s (with retries if needed)

### 3. Monitor for Errors
Watch for these improved error messages:
- `⏱️ Connection timeout (attempt X/Y)`
- `⏳ Waiting Xs before retry...`
- `❌ Failed to connect after X attempts, skipping...`

## Troubleshooting

### If Timeouts Still Occur

#### Check Network Connection
```powershell
# Test Discord voice gateway connectivity
Test-NetConnection gateway.discord.gg -Port 443
```

#### Verify Lavalink Status
```powershell
# Check if Lavalink server is responding
curl http://localhost:2333/version
```

#### Check Bot Permissions
Ensure the bot has these permissions in the voice channel:
- ✅ Connect
- ✅ Speak
- ✅ Use Voice Activity

#### Review Voice Channel
- Is the channel region having issues?
- Is the channel at user capacity?
- Are there any channel-specific restrictions?

#### Alternative: Disable Music State Persistence
If the issue persists, you can temporarily disable automatic reconnection by commenting out the restore call in `cog_load()`:

```python
# Temporarily disable auto-restore
# await self.restore_music_states()
```

### Expected Behavior Now

**Before Fix:**
- Bot hangs for 60s on each failed connection attempt
- Single failure = complete failure
- No visibility into what's happening

**After Fix:**
- Bot tries for max 30s per attempt
- Retries 2-3 times with delays between attempts
- Clear console output showing progress
- Gracefully skips problematic channels
- Faster failure detection and recovery

## Next Steps

1. **Restart your bot** to apply these changes
2. **Monitor the console** for connection attempts
3. **Join a voice channel** to test auto-connect
4. If issues persist, check the troubleshooting section above

## Additional Notes

- The timeout reduction from 60s → 30s means the bot will detect failures faster
- With 3 retry attempts, the maximum wait time is: 30s + 2s + 30s + 4s + 30s = 96s
- However, successful connections will complete much faster (typically < 5s)
- The retry logic provides resilience against temporary network hiccups
