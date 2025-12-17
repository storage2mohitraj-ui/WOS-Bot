# Interaction Timeout Fix

## Issue
The `/syncdata` and `/verifyscope` commands were failing with:
```
404 Not Found (error code: 10062): Unknown interaction
```

## Root Cause
Discord interactions have a **3-second timeout** for the initial response. The commands were taking too long to respond because they were:
1. Checking if the user is a global admin
2. Iterating through all guilds to check bot permissions
3. Building the guild list

This processing took more than 3 seconds, causing Discord to invalidate the interaction.

## Solution
**Defer the interaction response immediately** before doing any processing:

### Before (Broken)
```python
async def extract_messages(self, interaction: discord.Interaction):
    # Check if user is global admin (takes time)
    if not await self.check_global_admin(interaction):
        return
    
    # Get all guilds (takes time)
    admin_guilds = []
    for guild in self.bot.guilds:
        if await self.check_bot_permissions(guild):
            admin_guilds.append(guild)
    
    # Finally respond (TOO LATE - timeout already occurred)
    await interaction.response.send_message(...)
```

### After (Fixed)
```python
async def extract_messages(self, interaction: discord.Interaction):
    # Defer IMMEDIATELY to acknowledge the interaction
    await interaction.response.defer(ephemeral=True)
    
    # Now we can take our time processing
    user_id = interaction.user.id
    if not is_global_admin(user_id):
        await interaction.followup.send(...)  # Use followup, not response
        return
    
    # Get all guilds (no rush now)
    admin_guilds = []
    for guild in self.bot.guilds:
        if await self.check_bot_permissions(guild):
            admin_guilds.append(guild)
    
    # Send the actual message via followup
    await interaction.followup.send(...)  # Use followup, not response
```

## Changes Made

### 1. `/syncdata` Command
- ✅ Added `await interaction.response.defer(ephemeral=True)` at the start
- ✅ Changed `await self.check_global_admin(interaction)` to direct `is_global_admin(user_id)` check
- ✅ Changed all `interaction.response.send_message()` to `interaction.followup.send()`

### 2. `/verifyscope` Command
- ✅ Added `await interaction.response.defer(ephemeral=True)` at the start
- ✅ Changed `await self.check_global_admin(interaction)` to direct `is_global_admin(user_id)` check
- ✅ Changed all `interaction.response.send_message()` to `interaction.followup.send()`

## Key Points

### Discord Interaction Lifecycle
1. **Initial Response** (within 3 seconds)
   - Must call `interaction.response.defer()` OR `interaction.response.send_message()`
   - Can only be called ONCE
   
2. **Follow-up Messages** (within 15 minutes)
   - Use `interaction.followup.send()`
   - Can be called multiple times
   - Only available after initial response

### Best Practice
```python
async def command(self, interaction: discord.Interaction):
    # ALWAYS defer first if you need to do ANY processing
    await interaction.response.defer(ephemeral=True)
    
    # Now you have 15 minutes to process and respond
    # ... do your processing ...
    
    # Send response via followup
    await interaction.followup.send("Result!", ephemeral=True)
```

## Testing
- ✅ Syntax validated with `python -m py_compile`
- ✅ No compilation errors
- ⏳ Ready for testing in Discord

## Next Steps
1. **Restart the bot** to apply changes
2. **Test `/syncdata`** - should now work without timeout
3. **Test `/verifyscope`** - should now work without timeout

## Status
✅ **FIXED** - Both commands now defer immediately and use followup messages
