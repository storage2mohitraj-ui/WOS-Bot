# Auto-Translation Detection Sensitivity Improvements

## Problem
The auto-translation feature was triggering unnecessarily for English messages, even when the message was clearly in English. This was caused by DeepL's language detection being overly sensitive, especially for:
- Short messages (1-2 words)
- Mixed English variants (EN-US vs EN-GB)
- Phrases with technical terms or names

## Solutions Implemented

### 1. **Minimum Text Length Filter** ⭐ PRIMARY FIX
- **Default**: Messages shorter than **10 characters** are now skipped
- **Reason**: Language detection is unreliable for very short text like "hi", "ok", "lol", etc.
- **Configurable**: Each translation configuration has its own `min_text_length` setting
- **Example**: "hi" (2 chars) → skipped, "hello there" (11 chars) → processed

### 2. **Normalized Language Code Comparison** ⭐ PRIMARY FIX
- **Problem**: DeepL might detect "EN-US" but you set target as "EN", causing mismatch
- **Solution**: Both detected and target languages are normalized to base codes (EN-US → en, PT-BR → pt)
- **Benefit**: English variants (EN-US, EN-GB) are all treated as "en" for comparison
- **Example**: Message in EN-GB & target is EN-US → correctly skipped (both normalize to "en")

### 3. **Improved Logging**
- More detailed logs showing detected vs target languages
- Shows message length when skipped for being too short
- Normalized language codes in logs for easier debugging

## How the Detection Works Now

```
Message: "Hello, how are you?"
1. Length check: 18 chars ≥ 10 chars ✓ (pass)
2. Language detection: Detected as "en-us"
3. Normalize: "en-us" → "en"
4. Target language: "es" (Spanish)
5. Compare: "en" ≠ "es" → Proceed with translation ✓

Message: "Hello, how are you?"
1. Length check: 18 chars ≥ 10 chars ✓ (pass)
2. Language detection: Detected as "en-gb"
3. Normalize: "en-gb" → "en"
4. Target language: "en-us"
5. Normalize target: "en-us" → "en"
6. Compare: "en" = "en" → Skip translation (same language) ✓

Message: "hi"
1. Length check: 2 chars < 10 chars ✗ (fail)
2. Skip immediately (too short for reliable detection) ✓
```

## Configuration Options

The `ignore_if_source_is_target` setting (enabled by default) uses the improved detection:
- **Enabled** (✅ Recommended): Skips translation if detected language matches target
  - Now uses normalized comparison, so EN-US = EN-GB = EN
- **Disabled** (❌): Always translates, even if same language detected

## Customizing Sensitivity

### For Existing Configurations
The minimum text length is set to 10 characters by default. To adjust it:

1. **Via MongoDB** (if you have direct access):
   ```javascript
   db.autotranslate.updateOne(
     { config_id: "your_config_id" },
     { $set: { min_text_length: 5 } }  // Change to desired length
   )
   ```

2. **Recommended Settings**:
   - **Very sensitive** (translate almost everything): `min_text_length: 3`
   - **Normal** (current default): `min_text_length: 10`
   - **Conservative** (only longer messages): `min_text_length: 20`

### For New Configurations
When creating a new auto-translate configuration through `/autotranslatecreate`, the default `min_text_length` of 10 is automatically applied.

## Testing the Changes

1. **Short English messages** should now be skipped:
   - "hi" → ✅ Skipped (too short)
   - "ok" → ✅ Skipped (too short)
   - "thank you!" → ✅ Skipped (too short)
   
2. **Longer English messages** with EN as target should be skipped:
   - "Hello, how are you today?" → ✅ Skipped (detected EN = target EN)
   
3. **Non-English messages** should still translate:
   - "Hola, ¿cómo estás?" → ✅ Translated (detected ES ≠ target EN)

## Troubleshooting

If translations are still triggering for English:

1. **Check Configuration**:
   - Run `/autotranslatelist` to see your settings
   - Verify `ignore_if_source_is_target` is enabled (it should be by default)

2. **Check Logs**:
   - Look for lines like:
     ```
     Detected language: en for text: your message here
     Translation config: source=None, target=en, detected=en
     Skipping translation: detected language (en) matches target (en)
     ```

3. **Adjust Sensitivity**:
   - Increase `min_text_length` to skip more short messages
   - Consider setting a specific source language instead of auto-detect

## Technical Details

### Code Changes
- **File**: `cogs/auto_translate.py`
- **New method**: `_normalize_lang_code()` - Converts language codes to base form
- **Updated method**: `detect_language()` - Now returns normalized code
- **Updated method**: `_process_translation()` - Adds length check and normalized comparison
- **New config field**: `min_text_length` (default: 10)

### Performance Impact
- ✅ **Reduced API calls**: Fewer DeepL API calls due to length filtering
- ✅ **Faster processing**: Short messages are filtered before detection
- ✅ **Better accuracy**: Normalized comparison reduces false positives
