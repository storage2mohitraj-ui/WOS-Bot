# Auto-Redeem Diagnostic Guide

## 🔍 Why Auto-Redeem Isn't Working

If you see **"all four codes are unprocessed"** but auto-redeem still doesn't work, here's how to diagnose:

### Step 1: Check the Logs

After the bot restarts, look for these specific log messages:

```
🚀 === STARTUP AUTO-REDEEM CHECK ===
📊 Attempting to fetch codes from MongoDB...
✅ MongoDB: Found 4 unprocessed out of 4 total codes
📝 Unprocessed codes: ['CODE1', 'CODE2', 'CODE3', 'CODE4']
🎯 FOUND 4 UNPROCESSED CODES - TRIGGERING AUTO-REDEEM!

🔔 === TRIGGER AUTO-REDEEM ===
📥 Received 4 codes to process: ['CODE1', 'CODE2', 'CODE3', 'CODE4']
📊 Checking MongoDB for enabled guilds...
```

### Step 2: Look for the Most Common Issue

**❌ CRITICAL: No guilds have auto-redeem enabled!**

If you see this message, it means:
- **Auto-redeem is DISABLED** for your server
- Codes are detected, but won't be processed because no guilds are configured to use auto-redeem

### How to Fix: Enable Auto-Redeem

1. **Go to Bot Operations menu** (use the bot's main menu)
2. Click **"Gift Code Settings"**
3. Click **"Auto Redeem Settings"**
4. Click **"Configure Auto-Redeem"**
5. Click **"Enable Auto-Redeem"** 🟢 button
6. Ensure you have:
   - ✅ **Members added** to the auto-redeem list (at least 1 member)
   - ✅ **FID Monitor Channel** configured
   - ✅ **Auto-Redeem enabled** (status shows 🟢 Enabled)

### Step 3: Verify Configuration

Check your auto-redeem configuration menu should show:

```
⚙️ Auto-Redeem Configuration

Current Configuration:

🔘 Status: 🟢 Enabled (NOT 🔴 Disabled!)
👥 Members: 5 (or whatever number > 0)
📢 FID Monitor Channel: #your-channel-name

Features:
• Automatically redeem new gift codes
• Monitor channel for FID codes
• Track redemption success/failure
```

### Step 4: What the Logs Should Show When Working

When auto-redeem IS enabled and working correctly:

```
🔔 === TRIGGER AUTO-REDEEM ===
📥 Received 4 codes to process: ['CODE1', 'CODE2', 'CODE3', 'CODE4']
📊 Checking MongoDB for enabled guilds...
📋 Found 1 total guild settings in MongoDB
✅ MongoDB: 1 guilds with auto-redeem ENABLED
📝 Enabled guild IDs: [123456789]

Triggering auto-redeem for 1 guilds with 4 new codes

🎯 Processing code CODE1 for 1 guilds...
✅ Started auto-redeem task: guild=123456789, code=CODE1
📊 Triggered auto-redeem for code CODE1 across 1 guilds
✅ Marked CODE1 as processed in MongoDB
✅ Marked CODE1 as processed in SQLite

🎯 Processing code CODE2 for 1 guilds...
... (and so on)

✅ Processed 4 codes for auto-redeem
🏁 === TRIGGER AUTO-REDEEM COMPLETE ===
```

## 🎯 Quick Checklist

Before expecting auto-redeem to work, verify:

- [ ] ✅ Auto-redeem is **ENABLED** (green status)
- [ ] 👥 At least **1 member added** to auto-redeem list
- [ ] 📢 **FID Monitor Channel** is configured
- [ ] 🎁 Codes exist in database with `auto_redeem_processed = 0`
- [ ] 🔄 Bot has been **restarted** after enabling auto-redeem

## 🛠️ Testing Auto-Redeem

### Method 1: Reset a Code and Restart Bot

1. Go to **Auto-Redeem Configuration**
2. Click **"Reset Code Status" 🔄**
3. Select a code from the dropdown
4. **Restart the bot** (on Render or locally)
5. Check logs for auto-redeem trigger

### Method 2: Use !test Command (Manual Trigger)

The `!test` command is a **manual fallback** - it's not needed if auto-redeem is properly configured!

If you're relying on `!test`, it means auto-redeem isn't set up correctly.

## 📋 Common Issues

### Issue: "No guilds have auto-redeem enabled"
**Solution**: Enable auto-redeem from the configuration menu (see Step 2 above)

### Issue: "No members in auto-redeem list"
**Solution**: 
1. Go to Auto-Redeem Settings
2. Click "Manage Members"
3. Add FIDs using "Add Member" or "Import from Channel"

### Issue: "No FID Monitor Channel configured"
**Solution**:
1. Go to Auto-Redeem Configuration
2. Click "Set FID Monitor Channel"
3. Select the channel where you post FIDs

### Issue: Codes stay unprocessed after restart
**Solution**:
1. Check logs for error messages
2. Verify codes exist in database: `SELECT * FROM gift_codes WHERE auto_redeem_processed = 0`
3. Verify auto-redeem settings: `SELECT * FROM auto_redeem_settings WHERE enabled = 1`

## 🎁 Next Steps

After making changes:
1. **Restart the bot** to trigger startup auto-redeem check
2. **Watch the logs** for the diagnostic messages above
3. **Look for**:
   - ✅ Green checkmarks = Success
   - ⚠️ Yellow warnings = Issue but not critical
   - ❌ Red errors = Problem that needs fixing

The enhanced logging will show you **exactly** where the process is failing!
