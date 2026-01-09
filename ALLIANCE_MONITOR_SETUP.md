# Alliance Online Status Monitor - Setup Guide

## 📋 Prerequisites

Before using the alliance online status monitor, you need to install and configure several components:

### 1. Install Python Dependencies

Run this command in your bot directory to install all required packages:

```bash
pip install -r requirements.txt
```

This will install:
- `mss` - Screen capture library
- `opencv-python` - Image processing and detection
- `pytesseract` - OCR for text extraction
- `pywin32` - Windows API for window management

### 2. Install Tesseract OCR

Tesseract is required for extracting player names from screenshots.

**Windows:**
1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest `.exe` installer (e.g., `tesseract-ocr-w64-setup-5.3.3.exe`)
3. Run the installer and note the installation path (default: `C:\Program Files\Tesseract-OCR`)
4. Update the path in `alliance_monitor/monitor_config.py`:
   ```python
   TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
   ```

**Verify installation:**
```bash
tesseract --version
```

### 3. Install ADB (Android Debug Bridge)

ADB is required for scrolling automation in BlueStacks.

**Windows:**
1. Download Android SDK Platform Tools: https://developer.android.com/studio/releases/platform-tools
2. Extract the ZIP file to a location (e.g., `C:\adb`)
3. Add the ADB directory to your system PATH:
   - Right-click "This PC" → Properties → Advanced system settings
   - Click "Environment Variables"
   - Under "System variables", select "Path" and click "Edit"
   - Click "New" and add the ADB directory path
   - Click "OK" to save

**Verify installation:**
```bash
adb version
```

### 4. Configure BlueStacks

Enable ADB in BlueStacks settings:

1. Open BlueStacks
2. Click the ⚙️ Settings icon (top-right)
3. Go to **Advanced** tab
4. Enable **Android Debug Bridge (ADB)**
5. Note the ADB port number (usually 5555 or 5565)
6. Click "Save changes"
7. Restart BlueStacks if prompted

### 5. Connect to BlueStacks via ADB

After enabling ADB in BlueStacks:

```bash
# Connect to BlueStacks (replace 5555 with your port if different)
adb connect localhost:5555

# Verify connection
adb devices
```

You should see output like:
```
List of devices attached
localhost:5555   device
```

If you see a different port in BlueStacks, update `alliance_monitor/monitor_config.py`:
```python
ADB_PORT = 5565  # Change to your port
```

---

## 🎮 Preparing Whiteout Survival

1. **Open Whiteout Survival** in BlueStacks
2. **Navigate to Alliance Members List**:
   - Open your alliance
   - Go to the member list view
3. **Ensure 1280x720 Resolution**:
   - BlueStacks should be set to 1280x720 resolution
   - Check BlueStacks Settings → Display → Resolution

---

## 🔧 Calibration

The default coordinates are configured for a standard 1280x720 layout, but you may need to adjust them based on your specific setup.

### Test Screenshot Capture

First, verify that the bot can capture BlueStacks:

```bash
# Run in Discord
!online_test
```

This will:
- Find the BlueStacks window
- Capture a screenshot
- Send it to Discord for review

### View Detection Regions

To see where the bot is looking for green dots and player names:

```bash
# Run in Discord (Admin only)
!online_visualize
```

This creates two images:
- **detection_viz.png** - Shows green dot detection regions (green = online detected, red = offline)
- **ocr_viz.png** - Shows player name extraction regions

### Adjust Coordinates (if needed)

If the detection regions don't line up with player rows, edit `alliance_monitor/monitor_config.py`:

```python
# Starting Y position of first player row
FIRST_ROW_Y = 150  # Adjust this

# Height of each player row
ROW_HEIGHT = 80  # Adjust if rows are taller/shorter

# Maximum number of visible rows on screen
MAX_VISIBLE_ROWS = 6  # Adjust if you see more/fewer rows

# Green dot region within each row
GREEN_DOT_REGION = {
    'x': 50,      # X offset from left edge
    'y': 10,      # Y offset from top of row
    'width': 30,  # Width of detection area
    'height': 30  # Height of detection area
}

# Player name region within each row
NAME_OCR_REGION = {
    'x': 100,     # X offset from left edge
    'y': 20,      # Y offset from top of row
    'width': 300, # Width of name area
    'height': 40  # Height of name area
}
```

### Calibration Process:

1. Run `!online_visualize`
2. Look at the visualization images
3. Adjust coordinates in `monitor_config.py`
4. Restart the bot
5. Run `!online_visualize` again
6. Repeat until regions align correctly

---

## 🚀 Usage

Once everything is set up and calibrated:

### Check Online Status

```bash
!online
```

This will:
1. Scroll through the entire alliance member list
2. Capture screenshots at each position
3. Detect green "online" dots
4. Extract player names using OCR
5. Post results in Discord

**Example output:**
```
🟢 ONLINE (5)
• Luna
• Ragnar
• Frost
• Shadow
• Wolf

⚪ OFFLINE (3)
• Ghost
• Blaze
• Storm

Last scanned: 2026-01-08 00:38:57
Duration: 45.2s | Screenshots: 8
```

### Rate Limiting

To prevent excessive scanning, there's a cooldown of 10-20 minutes between scans.

### Admin Commands

**View Configuration:**
```bash
!online_config
```

**Test Screenshot Capture:**
```bash
!online_test
```

**Visualize Detection Regions:**
```bash
!online_visualize
```

---

## ⚙️ Advanced Configuration

All settings can be adjusted in `alliance_monitor/monitor_config.py`:

### Timing Settings
```python
# Delay between scroll actions (seconds)
SCROLL_DELAY_MIN = 2.5
SCROLL_DELAY_MAX = 5.5

# Cooldown between full scans (seconds)
SCAN_COOLDOWN_MIN = 600   # 10 minutes
SCAN_COOLDOWN_MAX = 1200  # 20 minutes
```

### Detection Settings
```python
# HSV color range for green dot
GREEN_HSV_LOWER = (40, 100, 100)
GREEN_HSV_UPPER = (80, 255, 255)

# Minimum area for green blob
MIN_GREEN_BLOB_AREA = 20
```

### Scroll Settings
```python
# Scroll coordinates
SCROLL_START_X = 640  # Center of screen
SCROLL_START_Y = 600  # Near bottom
SCROLL_END_X = 640
SCROLL_END_Y = 200    # Near top

# Randomization (makes scrolling human-like)
SCROLL_RANDOMIZATION = 10  # ±10 pixels
```

---

## 🐛 Troubleshooting

### "BlueStacks window not found"
- Make sure BlueStacks is running
- Check if window title contains "BlueStacks"
- Update `WINDOW_TITLE_PATTERN` in config if needed

### "ADB connection failed"
- Verify ADB is enabled in BlueStacks settings
- Check ADB port matches in config
- Try `adb connect localhost:5555` manually
- Restart BlueStacks

### "Tesseract not found"
- Verify Tesseract is installed
- Update `TESSERACT_PATH` in config
- Run `tesseract --version` to verify

### Poor OCR accuracy
- Make sure BlueStacks resolution is 1280x720
- Adjust `NAME_OCR_REGION` coordinates
- Check OCR visualization with `!online_visualize`
- Ensure text is clear and visible

### Green dots not detected
- Use `!online_visualize` to see detection regions
- Adjust `GREEN_DOT_REGION` coordinates
- Fine-tune HSV color range if green color varies
- Check if green dots are visible in screenshot

### Scrolling not working
- Verify ADB connection is active
- Check scroll coordinates align with your layout
- Ensure Whiteout Survival is in focus
- Try adjusting `SCROLL_START_Y` and `SCROLL_END_Y`

---

## 🔒 Safety Features

This monitoring system is designed to be safe and non-intrusive:

✅ **What it does:**
- Captures screenshots (passive observation)
- Scrolls through member list (minimal interaction)
- Reads visible player data only

❌ **What it DOESN'T do:**
- No clicking on players
- No joining rallies
- No donations
- No collecting rewards
- No memory access
- No packet sniffing

The bot operates at human-like speeds with randomized delays to avoid detection.

---

## 📝 Notes

- **First scan may take longer** as it scrolls through the entire list
- **Accuracy depends on calibration** - take time to set up coordinates correctly
- **Resolution matters** - ensure BlueStacks is 1280x720
- **Keep BlueStacks in foreground** during scanning
- **Rate limiting prevents spam** - respect the cooldown time

---

## 🆘 Support

If you encounter issues:

1. Check this guide thoroughly
2. Verify all prerequisites are installed
3. Run calibration commands (`!online_test`, `!online_visualize`)
4. Check bot console logs for error messages
5. Adjust configuration values incrementally

Happy monitoring! 🎮
