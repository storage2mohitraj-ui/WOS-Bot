# 🚀 LemonHosting Deployment Guide (GitHub Auto-Pull)

This guide will help you deploy your Discord bot to LemonHosting using GitHub auto-deployment.

---

## 📋 Prerequisites

- ✅ GitHub account with your bot repository
- ✅ LemonHosting account with a Python server
- ✅ All bot files committed to GitHub

---

## 🔧 Step 1: Prepare Your GitHub Repository

### 1.1 Check if you have a Git repository

```bash
cd "f:\STARK-whiteout survival bot\DISCORD BOT"
git status
```

If you see "not a git repository", initialize one:

```bash
git init
git add .
git commit -m "Initial commit - Discord bot"
```

### 1.2 Create a GitHub repository

1. Go to [GitHub](https://github.com/new)
2. Create a new **private** repository (recommended for bots)
3. Name it something like `whiteout-survival-bot`
4. **Do NOT** initialize with README (you already have files)

### 1.3 Push your code to GitHub

```bash
# Replace YOUR_USERNAME and YOUR_REPO with your actual values
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

> [!IMPORTANT]
> Make sure your `.env` file is in `.gitignore` to keep your tokens safe!

---

## 🎯 Step 2: Configure LemonHosting

### 2.1 Access your server panel

1. Log into [LemonHosting](https://lemonhosting.net)
2. Go to your Python server panel

### 2.2 Stop the server

Click the **STOP** button to stop your server before making changes.

### 2.3 Clone your GitHub repository

Go to **File Manager** and:

1. **Delete all existing files** in `/home/container/` (or backup if needed)
2. Click **Create File** → Name it `.git` (this will be replaced)
3. Go back to **Console** tab

In the console, run these commands manually via SFTP or the terminal:

```bash
cd /home/container
rm -rf *  # Clear everything
rm -rf .git  # Remove any existing git folder
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git .
```

> [!TIP]
> The `.` at the end clones into the current directory instead of creating a subfolder.

### 2.4 Configure Startup Variables

Go to **Startup** tab and verify these variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `PY_FILE` | `app.py` | Main Python file to run |
| `REQUIREMENTS_FILE` | `requirements.txt` | Dependencies file |
| `AUTO_UPDATE` | `1` | Enable GitHub auto-pull on restart |
| `PY_PACKAGES` | *(leave empty)* | Additional packages (optional) |

### 2.5 Set up environment variables

Go to **Startup** → **Environment Variables** or create a `.env` file:

**Option A: Using Panel Environment Variables** (Recommended)
- Add each variable from your `.env` file as a separate environment variable

**Option B: Upload `.env` file via SFTP**
- Use an SFTP client (FileZilla, WinSCP)
- Upload your `.env` file to `/home/container/`

> [!CAUTION]
> Never commit your `.env` file to GitHub! It contains sensitive tokens.

---

## 🔐 Step 3: Secure Your Repository (For Private Repos)

If your repository is **private**, you need to authenticate:

### Option 1: Personal Access Token (Recommended)

1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token (classic)**
3. Give it a name like "LemonHosting Bot Deploy"
4. Select scopes: `repo` (full control)
5. Generate and **copy the token**

Update your git remote URL in LemonHosting console:

```bash
cd /home/container
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/YOUR_REPO.git
```

### Option 2: Deploy Key (Advanced)

1. Generate SSH key on LemonHosting server
2. Add public key to GitHub repository deploy keys
3. Configure git to use SSH

---

## ✅ Step 4: Start Your Bot

### 4.1 Install dependencies

The startup script will automatically run:
```bash
pip install -U --prefix .local -r requirements.txt
```

### 4.2 Start the server

Click the **START** button in your LemonHosting panel.

### 4.3 Monitor the console

Watch for:
- ✅ `Pulling Docker container image` → Container ready
- ✅ `git pull` → Auto-update checking for changes
- ✅ `pip install` → Installing dependencies
- ✅ Your bot's startup messages → Bot is running!

---

## 🔄 Step 5: Auto-Deployment Workflow

Now whenever you make changes:

### Local Development
```bash
# Make your changes
git add .
git commit -m "Description of changes"
git push origin main
```

### Automatic Deployment
1. Go to LemonHosting panel
2. Click **RESTART** button
3. The server will automatically:
   - Run `git pull` to fetch latest changes
   - Reinstall dependencies from `requirements.txt`
   - Start your bot with the new code

---

## 🐛 Troubleshooting

### Error: "can't open file '/home/container/app.py'"

**Cause:** Files not in the correct directory

**Solution:**
```bash
cd /home/container
ls -la  # Check if app.py exists
```

If `app.py` is missing, re-clone your repository.

---

### Error: "Permission denied (publickey)"

**Cause:** SSH authentication failed for private repo

**Solution:** Use Personal Access Token method (see Step 3)

---

### Error: "No module named 'discord'"

**Cause:** Dependencies not installed

**Solution:** 
- Check if `requirements.txt` exists in `/home/container/`
- Verify `REQUIREMENTS_FILE` variable is set to `requirements.txt`
- Manually install: `pip install -U --prefix .local -r requirements.txt`

---

### Bot starts but crashes immediately

**Cause:** Missing environment variables or MongoDB connection

**Solution:**
1. Check if `.env` file exists: `ls -la /home/container/.env`
2. Verify all required variables are set
3. Test MongoDB connection (check `MONGODB_URI`)

---

## 📝 Quick Reference Commands

### Check current git status
```bash
cd /home/container
git status
git log -1  # Show last commit
```

### Manually pull latest changes
```bash
cd /home/container
git pull
```

### Reinstall dependencies
```bash
pip install -U --prefix .local -r requirements.txt
```

### View environment variables
```bash
printenv | grep -i discord
printenv | grep -i mongo
```

---

## 🎉 Success Checklist

- [ ] GitHub repository created and code pushed
- [ ] LemonHosting server configured with correct startup variables
- [ ] Repository cloned to `/home/container/`
- [ ] `.env` file uploaded or environment variables set
- [ ] `AUTO_UPDATE=1` enabled for auto-pull
- [ ] Bot starts successfully without errors
- [ ] Bot responds to commands in Discord
- [ ] Auto-deployment tested (push change → restart → verify)

---

## 🔗 Useful Links

- [LemonHosting Panel](https://lemonhosting.net)
- [GitHub Personal Access Tokens](https://github.com/settings/tokens)
- [Discord Developer Portal](https://discord.com/developers/applications)

---

> [!NOTE]
> With `AUTO_UPDATE=1`, every time you restart your server, it will automatically pull the latest changes from GitHub. This makes deployment as simple as:
> 1. Push to GitHub
> 2. Restart server
> 3. Done! ✨
