#!/usr/bin/env python3
"""
Launcher script for WOS Bot on Render
This script changes to the DISCORD_BOT_CLEAN directory and runs the main app
"""
import os
import sys
import runpy

# Get the absolute path to DISCORD_BOT_CLEAN
bot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DISCORD_BOT_CLEAN')

# Change to that directory
os.chdir(bot_dir)

# Add it to Python path at the beginning
sys.path.insert(0, bot_dir)

# Run the app.py file as a module
runpy.run_path('app.py', run_name='__main__')
