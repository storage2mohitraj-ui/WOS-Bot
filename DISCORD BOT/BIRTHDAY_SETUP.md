# 🎂 Birthday System - Quick Setup Guide

## Step 1: Add Birthday Channel to .env

Open your `.env` file and add:

```bash
BIRTHDAY_CHANNEL_ID=YOUR_CHANNEL_ID_HERE
```

**How to get Channel ID:**
1. Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
2. Right-click the channel → "Copy Channel ID"
3. Paste the ID into `.env`

## Step 2: Restart the Bot

Stop the current bot process (Ctrl+C) and restart:

```bash
python app.py
```

## Step 3: Test the Birthday System

Try these steps in Discord:

1. Type `/start`
2. Click the **🎂 Birthday** button
3. Click **🎂 Set Birthday**
4. Enter your birthday (day and month)
5. Click **📅 Upcoming Birthdays** to see the list
6. Click **🎁 My Birthday** to check your birthday

## That's it! 🎉

Users can now set their birthdays and will receive automatic birthday wishes on their special day!

---

## How It Works

### User Interface
- Access via `/start` → **Birthday** button
- 4 buttons in the dashboard:
  - **🎂 Set Birthday** - Set your birthday
  - **🗑️ Remove Birthday** - Remove your birthday
  - **📅 Upcoming Birthdays** - View upcoming birthdays (next 30 days)
  - **🎁 My Birthday** - Check your own birthday

### Automatic Wishes
- Bot checks for birthdays daily at midnight UTC
- Sends celebratory message to configured channel
- Mentions birthday users with festive embed

---

## Optional: Change Birthday Check Time

By default, birthdays are checked at midnight UTC. To change:

```bash
BIRTHDAY_CHECK_HOUR=12  # Check at noon UTC
```

## Features

✅ Button-based interface (no slash commands)
✅ Integrated into `/start` menu
✅ Automatic daily birthday wishes
✅ MongoDB support for persistent storage
✅ JSON fallback for local development
✅ Date validation (handles leap years)
✅ Upcoming birthdays view (next 30 days)
