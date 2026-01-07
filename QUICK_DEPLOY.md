# 🚀 Quick Start: Deploy to LemonHosting

Your bot is already on GitHub! Follow these steps to deploy to LemonHosting.

---

## ✅ Your Current Setup

- **GitHub Repository:** `https://github.com/storage1mohitraj-cmd/WOS-BOT-1.git`
- **Branch:** `main`
- **Main File:** `app.py`
- **Dependencies:** `requirements.txt`

---

## 📝 Deployment Steps

### Step 1: Push Latest Changes to GitHub

```bash
cd "f:\STARK-whiteout survival bot\DISCORD BOT"
git add .
git commit -m "Prepare for LemonHosting deployment"
git push origin main
```

### Step 2: Configure LemonHosting Server

1. **Log into LemonHosting Panel**
   - Go to your server dashboard
   - Click **STOP** to stop the server

2. **Clear Existing Files** (via File Manager or Console)
   ```bash
   cd /home/container
   rm -rf *
   rm -rf .git
   ```

3. **Clone Your Repository**
   ```bash
   cd /home/container
   git clone https://github.com/storage1mohitraj-cmd/WOS-BOT-1.git .
   ```
   
   > **Note:** The `.` at the end is important! It clones into the current directory.

4. **Verify Startup Variables** (Go to **Startup** tab)
   - `PY_FILE` = `app.py`
   - `REQUIREMENTS_FILE` = `requirements.txt`
   - `AUTO_UPDATE` = `1` ✅ (Already enabled!)

### Step 3: Set Up Environment Variables

**Option A: Upload .env file via SFTP** (Recommended)
- Use FileZilla or WinSCP
- Upload your `.env` file to `/home/container/`

**Option B: Set via Panel Environment Variables**
- Go to **Startup** → **Variables**
- Add each variable from your `.env` file

### Step 4: Handle Private Repository Authentication

Since your repo might be private, you need to authenticate:

1. **Generate GitHub Personal Access Token**
   - Go to: https://github.com/settings/tokens
   - Click **Generate new token (classic)**
   - Name: "LemonHosting Deploy"
   - Scopes: Select `repo` (full control)
   - Click **Generate token**
   - **Copy the token** (you won't see it again!)

2. **Update Git Remote URL** (in LemonHosting console)
   ```bash
   cd /home/container
   git remote set-url origin https://YOUR_TOKEN@github.com/storage1mohitraj-cmd/WOS-BOT-1.git
   ```
   
   Replace `YOUR_TOKEN` with the token you just copied.

### Step 5: Start Your Bot

1. Click **START** in LemonHosting panel
2. Watch the console for:
   - ✅ `git pull` → Checking for updates
   - ✅ `pip install` → Installing dependencies
   - ✅ Bot startup messages → Success!

---

## 🔄 Future Updates (Auto-Deploy)

Whenever you make changes:

```bash
# On your local machine
git add .
git commit -m "Your changes description"
git push origin main

# Then in LemonHosting panel
# Just click RESTART button - it will auto-pull latest changes!
```

---

## 🐛 If You See Errors

### "can't open file '/home/container/app.py'"
- Files not cloned properly
- Re-run: `git clone https://github.com/storage1mohitraj-cmd/WOS-BOT-1.git .`

### "Permission denied (publickey)"
- Need to authenticate with Personal Access Token (see Step 4)

### "No module named 'discord'"
- Dependencies not installed
- Check if `requirements.txt` exists
- Manually run: `pip install -U --prefix .local -r requirements.txt`

---

## 📞 Need Help?

See the full guide: `DEPLOYMENT_GUIDE.md`
