# Voice Conversation End Call Button

## Summary
Added an "End Call" button to the `/voice_chat` command embed that allows users to end the voice conversation directly without using the `/end_voice_chat` slash command.

## Changes Made

### 1. Created `EndCallView` Class
- **Location**: `cogs/voice_conversation.py` (lines 81-147)
- **Features**:
  - Red "🔴 End Call" button styled as danger (ButtonStyle.danger)
  - Permission check: Only the session owner or administrators can end the call
  - Plays goodbye message before ending
  - Shows summary with duration, message count, and who ended it
  - Disables the button after use to prevent double-clicks

### 2. Updated `VoiceSession` Class
- **Added**: `status_message` attribute to store the welcome message reference
- **Purpose**: Allows the button to update the original message when clicked

### 3. Updated `/voice_chat` Command
- **Added**: End Call button view to the welcome embed
- **Updated**: Help text now mentions the button: "Click '🔴 End Call' button below or use `/end_voice_chat` to stop"
- **Stores**: The status message in the session for later button updates

### 4. Enabled the Cog
- **Removed**: Unnecessary `discord.sinks` check that was blocking the cog from loading
- **Note**: The current implementation only provides text-to-voice (TTS), which works fine with discord.py
- **Full voice recording** would still require py-cord, but that's not implemented yet

## Usage

1. User runs `/voice_chat`
2. Bot connects to voice channel and shows embed with "🔴 End Call" button
3. User can either:
   - Click the "🔴 End Call" button
   - Use `/end_voice_chat` slash command
   - Leave the voice channel (auto-cleanup after 30s)

## Button Behavior

- **Who can click**: Session owner or server administrators
- **What happens**: 
  1. Bot says goodbye in voice
  2. Session is cleaned up
  3. Bot disconnects from voice
  4. Summary message is sent showing duration and stats
  5. Button is disabled to prevent re-clicks

## Testing

To test, restart the bot and the voice conversation cog should now load with the new button feature enabled.
