#!/usr/bin/env python3
"""
Launcher script for WOS Bot on Render
This script changes to the DISCORD_BOT_CLEAN directory and runs the main app
"""
import os
import sys

# Change to the DISCORD_BOT_CLEAN directory
os.chdir('DISCORD_BOT_CLEAN')

# Add the directory to Python path
sys.path.insert(0, os.getcwd())

# Import and run the main app
import app
