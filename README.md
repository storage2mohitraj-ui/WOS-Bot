# WOS Bot - Whiteout Survival Discord Bot

A comprehensive Discord bot for Whiteout Survival game management, featuring alliance monitoring, gift code management, auto-translation, music player, and more.

## 📁 Repository Structure

**Note:** The main bot code is located in the `DISCORD BOT` directory, which contains a separate git repository and could not be included in this initial commit due to embedded git repository conflicts. 

### Current Structure:
- `BOT 2/` - Legacy bot version
- `alliance.py` - Alliance management utilities
- `verify_font.py` - Font verification script
- `requirements.txt` - Python dependencies

### Main Bot (DISCORD BOT folder - to be added):
The primary Discord bot application with all features including:
- Alliance monitoring and management
- Gift code auto-redeem system
- Auto-translation features
- Music player with Lavalink integration
- Member management
- Attendance tracking
- And many more features

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- Discord Bot Token
- MongoDB URI (for production)
- Lavalink server (for music features)

### Installation

1. Clone this repository
```bash
git clone https://github.com/storage2mohitraj-ui/WOS-Bot.git
cd WOS-Bot
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure environment variables
Create a `bot_token.txt` file with your Discord bot token
Create a `mongo_uri.txt` file with your MongoDB connection string

4. Run the bot
```bash
python app.py
```

## 📝 Configuration

- Bot tokens and sensitive credentials should be stored in separate `.txt` files (excluded from git)
- MongoDB is used for persistent storage in production
- SQLite is used as a fallback for local development

## 🔒 Security

This repository excludes sensitive files including:
- `bot_token.txt`
- `mongo_uri.txt`
- Database files (`.sqlite`)
- Virtual environments
- Log files

## 📚 Documentation

For detailed documentation, deployment guides, and feature explanations, please refer to the documentation files in the `DISCORD BOT` directory once added.

## ⚠️ Important Notes

- This is a fresh repository with no connection to previous repositories
- Sensitive files and credentials are gitignored for security
- The embedded git repositories (backend, frontend, lavalink) are excluded

## 🤝 Contributing

This is a private bot for Whiteout Survival game management. 

## 📄 License

Private - All rights reserved
