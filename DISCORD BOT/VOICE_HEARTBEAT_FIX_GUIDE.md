# Quick Fix for Voice Heartbeat Timeout
# Apply these changes to your voice conversation code

## Problem:
The voice WebSocket connection times out after 30 seconds when the bot is busy
processing AI responses or generating TTS, causing constant disconnections.

## Root Cause:
1. Discord expects regular heartbeats from the voice WebSocket
2. When the bot is busy (AI request, TTS generation), it can't send heartbeats
3. After 30 seconds without heartbeat, Discord closes the connection
4. The bot tries to reconnect, creating a loop of disconnections

## Solution: Apply these 5 changes

### 1. Increase Voice Connection Timeout
```python
# OLD:
voice_client = await channel.connect()

# NEW:
voice_client = await channel.connect(
    timeout=60.0,      # Extended from default 30s
    reconnect=True      # Auto-reconnect on disconnect
)
```

### 2. Run TTS Generation Asynchronously
```python
# OLD (blocks event loop):
def _speak(self, session, text):
    audio_file = gtts.gTTS(text, lang='en')  # BLOCKS!
    audio_file.save(output_path)

# NEW (non-blocking):
async def _speak(self, session, text):
    loop = asyncio.get_event_loop()
    # Run in thread pool - doesn't block heartbeats
    audio_file = await loop.run_in_executor(
        None,
        self._generate_tts_sync,
        text
    )
```

### 3. Make AI Requests Non-Blocking
```python
# Ensure AI requests yield control to event loop
async def _get_ai_response(self, session, user_text):
    # Add small yields during long operations
    response = await self.api_call(user_text)  # Already async - good!
    await asyncio.sleep(0)  # Yield control
    return response
```

### 4. Monitor Playback Without Blocking
```python
# OLD (blocks event loop):
while voice_client.is_playing():
    time.sleep(1)  # BLOCKS!

# NEW (yields to event loop):
while voice_client.is_playing():
    await asyncio.sleep(0.5)  # Checks every 500ms but yields control
```

### 5. Add Voice Client Status Check
```python
async def _speak(self, session, text):
    voice_client = session.voice_client
    
    # Always check connection before operations
    if not voice_client or not voice_client.is_connected():
        print("⚠️ Voice client disconnected, skipping playback")
        return
    
    # ... rest of your code
```

## Quick Apply (if you have access to the code):

Find your `_speak` method and update it:

```python
async def _speak(self, session: VoiceSession, text: str):
    """Convert text to speech and play - FIXED VERSION"""
    voice_client = session.voice_client
    
    # Check connection
    if not voice_client or not voice_client.is_connected():
        print("⚠️ Voice client not connected")
        return
    
    try:
        # Generate TTS asynchronously (doesn't block)
        loop = asyncio.get_event_loop()
        audio_path = await loop.run_in_executor(
            None,
            self._generate_tts_file,  # Your existing TTS function
            text,
            session.guild_id
        )
        
        if not audio_path or not os.path.exists(audio_path):
            print("❌ TTS generation failed")
            return
        
        # Create audio source
        audio_source = discord.FFmpegPCMAudio(
            audio_path,
            options='-loglevel error'
        )
        
        # Play audio
        voice_client.play(audio_source)
        
        # Wait for playback WITHOUT blocking
        while voice_client.is_playing():
            await asyncio.sleep(0.5)  # Yield every 500ms
            
            # Safety check
            if not voice_client.is_connected():
                print("⚠️ Voice client disconnected during playback")
                break
        
        # Cleanup
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
    except Exception as e:
        print(f"❌ TTS playback error: {e}")
        # Cleanup on error
        if 'audio_path' in locals() and os.path.exists(audio_path):
            os.remove(audio_path)
```

## Testing:

After applying the fix:
1. Start a voice chat session
2. Send multiple messages quickly  
3. Voice connection should stay stable
4. No more "Disconnected from voice... Reconnecting" errors

## Additional Optimization:

Add this to your voice connection initialization:

```python
@app_commands.command(name="voice_chat", description="Start voice chat")
async def voice_chat(self, interaction: discord.Interaction):
    # ... your existing code ...
    
    # Connect with better settings
    voice_client = await interaction.user.voice.channel.connect(
        timeout=60.0,
        reconnect=True,
        self_deaf=False,
        self_mute=False
    )
    
    # Optional: Set status
    try:
        await interaction.user.voice.channel.edit(
            status="🎙️ AI Voice Assistant: Molly"
        )
    except:
        pass
    
    # ... rest of your code ...
```

## If the issue persists:

The problem might also be on Render's network. Add retry logic:

```python
MAX_RETRIES = 3
retry_count = 0

while retry_count < MAX_RETRIES:
    try:
        voice_client = await channel.connect(timeout=60.0, reconnect=True)
        break  # Success
    except asyncio.TimeoutError:
        retry_count += 1
        if retry_count >= MAX_RETRIES:
            await interaction.followup.send(
                "❌ Voice connection failed after 3 attempts. "
                "Please try again later."
            )
            return
        await asyncio.sleep(2)  # Wait before retry
```

---

**Summary of Changes:**
- ✅ Extended timeout from 30s → 60s
- ✅ Enabled auto-reconnect
- ✅ Made TTS generation async (non-blocking)
- ✅ Added yields during playback monitoring
- ✅ Added connection status checks

This should fix the heartbeat timeout issues! 🎉
