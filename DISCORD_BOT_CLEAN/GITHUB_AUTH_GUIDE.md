# 🔐 GitHub Authentication Guide

## Issue
You're trying to push to a new GitHub account (`storage2mohitraj-ui`) but Git is using credentials from your old account (`storage1mohitraj-cmd`).

---

## Solution Options

### **Option 1: Use Personal Access Token (Recommended)**

1. **Generate a Personal Access Token**
   - Go to: https://github.com/settings/tokens
   - Click **"Generate new token (classic)"**
   - Name: "WOS Bot Deploy"
   - Expiration: Choose duration (90 days recommended)
   - Scopes: Check **`repo`** (full control of private repositories)
   - Click **"Generate token"**
   - **COPY THE TOKEN** (you won't see it again!)

2. **Push with Token**
   ```bash
   git push https://YOUR_TOKEN@github.com/storage2mohitraj-ui/WOS-Bot.git main
   ```
   
   Replace `YOUR_TOKEN` with the token you just copied.

3. **Update Remote URL (Optional - for future pushes)**
   ```bash
   git remote set-url origin https://YOUR_TOKEN@github.com/storage2mohitraj-ui/WOS-Bot.git
   ```

---

### **Option 2: Update Git Credentials (Windows)**

1. **Open Credential Manager**
   - Press `Win + R`
   - Type: `control /name Microsoft.CredentialManager`
   - Click **Windows Credentials**

2. **Remove Old GitHub Credentials**
   - Find entries starting with `git:https://github.com`
   - Click each one → **Remove**

3. **Push Again**
   ```bash
   git push -u origin main
   ```
   
   Git will prompt you to log in with the new account.

---

### **Option 3: Use GitHub CLI (Easiest)**

1. **Install GitHub CLI** (if not installed)
   - Download from: https://cli.github.com/
   - Or use: `winget install GitHub.cli`

2. **Authenticate**
   ```bash
   gh auth login
   ```
   
   Follow the prompts to authenticate with your new account.

3. **Push**
   ```bash
   git push -u origin main
   ```

---

## Quick Command (Use Personal Access Token)

Once you have your token, run this in PowerShell:

```powershell
cd "f:\STARK-whiteout survival bot\DISCORD BOT"
git push https://YOUR_TOKEN@github.com/storage2mohitraj-ui/WOS-Bot.git main
```

Replace `YOUR_TOKEN` with your actual Personal Access Token.

---

## After Successful Push

Update your deployment guides with the new repository URL:

**For LemonHosting:**
```bash
git clone https://YOUR_TOKEN@github.com/storage2mohitraj-ui/WOS-Bot.git .
```

Or if the repo is public:
```bash
git clone https://github.com/storage2mohitraj-ui/WOS-Bot.git .
```
