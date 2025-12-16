#!/usr/bin/env python3
"""
Launcher script for WOS Bot on Render
This script changes to the DISCORD_BOT_CLEAN directory and runs the main app
"""
import os
import sys

# Change to the DISCORD_BOT_CLEAN directory
bot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DISCORD_BOT_CLEAN')
os.chdir(bot_dir)

# Add the directory to Python path at the beginning
sys.path.insert(0, bot_dir)

# Execute the app.py file directly
with open('app.py', 'r', encoding='utf-8') as f:
    exec(f.read())
