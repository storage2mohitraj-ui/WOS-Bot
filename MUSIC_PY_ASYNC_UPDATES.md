# Quick Reference: music.py Async Updates Required

## Summary
All calls to `music_state_storage` methods now need to be AWAITED because they're async.

## Changes to Make in cogs/music.py

### 1. Update CustomPlayer.save_state() method (around line 222)

**BEFORE:**
```python
def save_state(self):
    """Save current playback state to database"""
    if not music_state_storage or not self.guild:
        return
    
    try:
        # ... preparation code ...
        
        # Save to storage
        music_state_storage.save_state(
            guild_id=self.guild.id,
            # ... parameters ...
        )
```

**AFTER:**
```python
async def save_state(self):
    """Save current playback state to database"""
    if not music_state_storage or not self.guild:
        return
    
    try:
        # ... preparation code ...
        
        # Save to storage
        await music_state_storage.save_state(
            guild_id=self.guild.id,
            # ... parameters ...
        )
```

### 2. Update all calls to CustomPlayer.save_state()

Find all instances of `player.save_state()` or `self.save_state()` and add `await`:

**Search for:** `save_state()`
**Replace with:** `await save_state()`

**NOTE:** This needs to be in an async function. If called from a non-async function, wrap in `asyncio.create_task()`:
```python
# If you can't await (in a non-async context):
asyncio.create_task(player.save_state())
```

### 3. Update music_state_storage.set_persistent_channel() calls (around line 680)

**BEFORE:**
```python
if music_state_storage:
    music_state_storage.set_persistent_channel(self.guild.id, self.channel.id)
```

**AFTER:**
```python
if music_state_storage:
    await music_state_storage.set_persistent_channel(self.guild.id, self.channel.id)
```

### 4. Update music_state_storage.get_all_states() call (around line 1690)

**BEFORE:**
```python
states = music_state_storage.get_all_states()
```

**AFTER:**
```python
states = await music_state_storage.get_all_states()
```

### 5. Update music_state_storage.get_persistent_channel() calls (around line 2280)

**BEFORE:**
```python
persistent_channel_id = music_state_storage.get_persistent_channel(interaction.guild.id)
```

**AFTER:**
```python
persistent_channel_id = await music_state_storage.get_persistent_channel(interaction.guild.id)
```

### 6. Update music_state_storage.clear_persistent_channel() calls (around lines 2288, 2295, 2299)

**BEFORE:**
```python
music_state_storage.clear_persistent_channel(interaction.guild.id)
```

**AFTER:**
```python
await music_state_storage.clear_persistent_channel(interaction.guild.id)
```

## Finding All Occurrences

Use your text editor's "Find and Replace" with regex:

1. **Find:** `music_state_storage\.(save_state|load_state|delete_state|get_all_states|set_persistent_channel|get_persistent_channel|clear_persistent_channel)\(`
2. **Check each occurrence** - if not already awaited, add `await ` before it

## Testing After Changes

1. **Local Testing:**
   ```bash
   # Ensure bot starts without errors
   python app.py
   ```

2. **Check Logs:**
   Look for these messages on startup:
   ```
   [MusicStateStorage] ✅ Connected to primary MongoDB successfully!
   ✅ Music state storage initialized
   ```

3. **Functional Testing:**
   - Play music → Check state saves
   - Set persistent channel → Verify it's stored
   - Restart bot → Music state should be restored

## Quick Checklist

- [ ] Updated `CustomPlayer.save_state()` to `async def`
- [ ] Added `await` to `music_state_storage.save_state()` call
- [ ] Added `await` to all `music_state_storage.set_persistent_channel()` calls
- [ ] Added `await` to all `music_state_storage.get_persistent_channel()` calls
- [ ] Added `await` to all `music_state_storage.clear_persistent_channel()` calls
- [ ] Added `await` to `music_state_storage.get_all_states()` call
- [ ] Added `await` to all `player.save_state()` calls (or wrapped in asyncio.create_task)
- [ ] Tested bot starts without errors
- [ ] Tested music state persistence on Render
