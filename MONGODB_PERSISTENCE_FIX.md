# MongoDB Persistence Fix - Auto-Redeem Settings

## 🔥 Issue: Auto-Redeem Settings Lost on Restart

### The Problem
Every time you restart the bot on Render, auto-redeem is disabled again, even though you enabled it before.

### Why This Happens on Render

**Render uses ephemeral storage**, which means:
- ✅ **MongoDB** = PERSISTENT (data survives restarts)
- ❌ **SQLite files** = TEMPORARY (reset on every restart/deploy)

When the bot restarts:
1. SQLite database file is **wiped clean** (new empty file)
2. If MongoDB isn't working correctly, settings are lost
3. You have to re-enable auto-redeem every time

## 🔍 Enhanced Diagnostic Logging

I've added comprehensive logging to track MongoDB persistence:

### When You Enable Auto-Redeem

You'll now see detailed logs:

```
📊 MongoDB: Saving auto-redeem ENABLED for guild 123456789...
✅ MongoDB: Successfully saved auto-redeem ENABLED for guild 123456789
📂 SQLite: Saving auto-redeem ENABLED for guild 123456789...
✅ SQLite: Successfully saved auto-redeem ENABLED for guild 123456789
🎉 AUTO-REDEEM ENABLED: Settings saved to MongoDB (PERSISTENT on Render)
```

### If MongoDB Fails

```
❌ MongoDB: Failed to save auto redeem settings: [error]
✅ SQLite: Successfully saved auto-redeem ENABLED for guild 123456789
⚠️ AUTO-REDEEM ENABLED: Settings saved to SQLite only (TEMPORARY - will reset on Render restart!)
```

### If MongoDB Not Available

```
⚠️ MongoDB is not enabled - settings will be lost on restart!
⚠️ AutoRedeemSettingsAdapter not available - settings will be lost on restart!
```

## 📊 How to Diagnose

### Step 1: Enable Auto-Redeem and Check Logs

1. **Enable auto-redeem** from the configuration menu
2. **Check logs immediately** for:
   - ✅ `MongoDB: Successfully saved auto-redeem ENABLED`
   - ✅ `AUTO-REDEEM ENABLED: Settings saved to MongoDB (PERSISTENT on Render)`

### Step 2: Restart Bot and Check Logs

After restart, check for:

```
🔔 === TRIGGER AUTO-REDEEM ===
📊 Checking MongoDB for enabled guilds...
📋 Found 1 total guild settings in MongoDB
✅ MongoDB: 1 guilds with auto-redeem ENABLED  ← Should show YOUR guild!
📝 Enabled guild IDs: [123456789]
```

### Step 3: Identify the Problem

#### ✅ **Working** (MongoDB persistent):
```
Enable → 🎉 Settings saved to MongoDB (PERSISTENT)
Restart → ✅ MongoDB: 1 guilds with auto-redeem ENABLED
```

#### ❌ **NOT Working** (MongoDB failing):
```
Enable → ⚠️ Settings saved to SQLite only (TEMPORARY)
Restart → ❌ MongoDB: No guilds have auto-redeem enabled!
```

## 🛠️ Possible Issues and Solutions

### Issue 1: MongoDB Not Connected

**Symptoms**:
```
⚠️ MongoDB is not enabled
⚠️ Settings saved to SQLite only (TEMPORARY)
```

**Solution**:
1. Check `MONGODB_URI` environment variable in Render
2. Restart the bot to reconnect to MongoDB
3. Verify MongoDB connection in startup logs

### Issue 2: AutoRedeemSettingsAdapter Missing

**Symptoms**:
```
⚠️ AutoRedeemSettingsAdapter not available
```

**Solution**:
1. Check if `db/mongo_adapters.py` has `AutoRedeemSettingsAdapter` class
2. Verify imports in `cogs/manage_giftcode.py`
3. Check for import errors in startup logs

### Issue 3: MongoDB Save Failing

**Symptoms**:
```
❌ MongoDB: Failed to save auto redeem settings: [error message]
```

**Solution**:
1. Check the specific error message in logs
2. Verify MongoDB permissions (read/write access)
3. Check MongoDB connection status
4. Verify the adapter's `set_enabled()` method exists

### Issue 4: MongoDB Read Failing

**Symptoms**:
```
Enable works → Settings saved
Restart → ❌ CRITICAL: No guilds have auto-redeem enabled!
```

**Solution**:
1. Check if `get_all_settings()` method exists in AutoRedeemSettingsAdapter
2. Verify MongoDB query is working
3. Check collection name matches (`auto_redeem_settings`)
4. Look for read errors in startup logs

## ✅ Expected Behavior (Working Correctly)

### When You Enable:
```
18:30:00 [INFO] 📊 MongoDB: Saving auto-redeem ENABLED for guild 123456789...
18:30:00 [INFO] ✅ MongoDB: Successfully saved auto-redeem ENABLED for guild 123456789
18:30:00 [INFO] 📂 SQLite: Saving auto-redeem ENABLED for guild 123456789...
18:30:00 [INFO] ✅ SQLite: Successfully saved auto-redeem ENABLED for guild 123456789
18:30:00 [INFO] 🎉 AUTO-REDEEM ENABLED: Settings saved to MongoDB (PERSISTENT on Render)
```

### After Restart:
```
18:35:00 [INFO] 🔔 === TRIGGER AUTO-REDEEM ===
18:35:00 [INFO] 📊 Checking MongoDB for enabled guilds...
18:35:00 [INFO] 📋 Found 1 total guild settings in MongoDB
18:35:00 [INFO] ✅ MongoDB: 1 guilds with auto-redeem ENABLED
18:35:00 [INFO] 📝 Enabled guild IDs: [123456789]
18:35:00 [INFO] Triggering auto-redeem for 1 guilds with 4 new codes
```

## 🚀 Next Steps

1. **Deploy** the updated code to Render
2. **Enable** auto-redeem from the configuration menu
3. **Check logs** for MongoDB save confirmation:
   - Look for ✅ **green checkmarks** = Success
   - Look for ⚠️ **warnings** = Potential issues
   - Look for ❌ **errors** = Failed operations
4. **Restart** the bot
5. **Verify** auto-redeem is still enabled without manual intervention

## 📝 What to Look For

### Success Indicators:
- ✅ `MongoDB: Successfully saved auto-redeem ENABLED`
- ✅ `AUTO-REDEEM ENABLED: Settings saved to MongoDB (PERSISTENT)`
- ✅ After restart: `MongoDB: 1 guilds with auto-redeem ENABLED`

### Warning Indicators:
- ⚠️ `Settings saved to SQLite only (TEMPORARY)`
- ⚠️ `MongoDB is not enabled`
- ⚠️ `AutoRedeemSettingsAdapter not available`

### Error Indicators:
- ❌ `Failed to save auto redeem settings`
- ❌ `Failed to save to ANY database`
- ❌ `No guilds have auto-redeem enabled` (after you enabled it)

---

The enhanced logging will tell you **exactly** whether MongoDB persistence is working! 📊

If you see **any MongoDB warnings or errors**, that's why your settings aren't persisting.
