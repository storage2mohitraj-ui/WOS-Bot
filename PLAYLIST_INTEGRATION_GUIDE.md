# Playlist Management Integration Guide

This guide shows exactly what code to add to `cogs/music.py` to enable playlist management features.

## ✅ Files Already Created

1. **playlist_storage.py** - Database layer for saving/loading playlists
2. **cogs/playlist_ui.py** - UI components (views, modals, buttons)
3. **music_playlist_integration.py** - Reference code for integration

## 📝 Manual Integration Steps

### Step 1: Add Import (Line ~22, after the existing imports)

Find this line in `music.py`:
```python
load_dotenv()
```

**Add these lines right after it:**
```python

# Import playlist UI components
try:
    from cogs.playlist_ui import PlaylistManagementView
except ImportError:
    PlaylistManagementView = None
```

---

### Step 2: Add Previous Button to PlayerControlView (Line ~74)

Find this section in `music.py`:
```python
class PlayerControlView(discord.ui.View):
    """Interactive player controls"""
    
    def __init__(self, player: CustomPlayer):
        super().__init__(timeout=None)
        self.player = player
        
    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.primary, custom_id="music_playpause")
```

**Change it to:**
```python
class PlayerControlView(discord.ui.View):
    """Interactive player controls"""
    
    def __init__(self, player: CustomPlayer):
        super().__init__(timeout=None)
        self.player = player
        
    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary, custom_id="music_previous")
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to previous track"""
        try:
            if not self.player.history:
                await interaction.response.send_message("⏮️ No previous tracks in history", ephemeral=True)
                return
            
            # Get the last track from history
            if len(self.player.history) > 0:
                previous_track = self.player.history.pop()
                await self.player.play(previous_track)
                await interaction.response.send_message(f"⏮️ Playing previous: **{previous_track.title}**", ephemeral=True)
            else:
                await interaction.response.send_message("⏮️ No previous track available", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)
        
    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.primary, custom_id="music_playpause")
```

---

### Step 3: Add /previous and /playlist Commands (Line ~813, before `async def setup`)

Find this section near the end of the Music class:
```python
        await player.seek(position * 1000)  # Convert to milliseconds
        await interaction.response.send_message(f"⏩ Seeked to **{timedelta(seconds=position)}**")


async def setup(bot: commands.Bot):
```

**Add these commands between the seek command and setup function:**
```python
        await player.seek(position * 1000)  # Convert to milliseconds
        await interaction.response.send_message(f"⏩ Seeked to **{timedelta(seconds=position)}**")
        
    @app_commands.command(name="previous", description="Play the previous track from history")
    async def previous(self, interaction: discord.Interaction):
        """Play previous track"""
        player: CustomPlayer = interaction.guild.voice_client
        
        if not player:
            await interaction.response.send_message("❌ Not connected to voice!", ephemeral=True)
            return
        
        if not player.history:
            await interaction.response.send_message("⏮️ No previous tracks in history", ephemeral=True)
            return
        
        # Get the last track from history
        previous_track = player.history.pop()
        await player.play(previous_track)
        await interaction.response.send_message(f"⏮️ Playing previous: **{previous_track.title}**")
        
    @app_commands.command(name="playlist", description="Manage your saved playlists")
    async def playlist(self, interaction: discord.Interaction):
        """Open playlist management panel"""
        if not PlaylistManagementView:
            await interaction.response.send_message(
                "❌ Playlist management is not available. Please contact the bot administrator.",
                ephemeral=True
            )
            return
        
        player: CustomPlayer = interaction.guild.voice_client
        
        # Create player if not exists (for viewing playlists even when not in voice)
        if not player:
            # Check if user is in voice channel
            if interaction.user.voice and interaction.user.voice.channel:
                try:
                    player = await interaction.user.voice.channel.connect(cls=CustomPlayer, timeout=60.0)
                    player.text_channel = interaction.channel
                except Exception as e:
                    await interaction.response.send_message(
                        f"❌ Failed to connect to voice: {e}",
                        ephemeral=True
                    )
                    return
            else:
                # Allow viewing playlists without being in voice
                # Create a dummy player reference
                player = type('DummyPlayer', (), {
                    'queue': type('Queue', (), {'is_empty': True, 'count': 0})(),
                    'current': None,
                    'current_playlist_name': None
                })()
        
        view = PlaylistManagementView(interaction.user.id, interaction.guild.id, player)
        embed = view.get_embed()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
```

---

### Step 4: Show Playlist Name in Now Playing (Line ~437, in create_now_playing_embed)

Find this section in the `create_now_playing_embed` method:
```python
        # Loop and shuffle status
        loop_emoji = {"off": "🔁", "track": "🔂", "queue": "🔁"}
        status = f"{loop_emoji[player.loop_mode]} Loop: {player.loop_mode.title()}"
        embed.set_footer(text=status)
        
        return embed
```

**Change it to:**
```python
        # Loop and shuffle status
        loop_emoji = {"off": "🔁", "track": "🔂", "queue": "🔁"}
        status = f"{loop_emoji[player.loop_mode]} Loop: {player.loop_mode.title()}"
        
        # Show playlist name if loaded from saved playlist
        if player.current_playlist_name:
            embed.add_field(
                name="📁 Playlist",
                value=player.current_playlist_name,
                inline=True
            )
        
        embed.set_footer(text=status)
        
        return embed
```

---

## 🧪 Testing After Integration

After making these changes:

1. Restart the bot
2. Join a voice channel
3. Play a YouTube playlist: `/play https://www.youtube.com/playlist?list=...`
4. Run `/playlist` to open the playlist manager
5. Click "💾 Save Current Queue" and enter a name
6. Click "📋 My Playlists" to see your saved playlists
7. Test the Previous button (⏮️) in the now playing controls
8. Test loading a saved playlist

---

## 🔧 Troubleshooting

**If `/playlist` command doesn't appear:**
- Make sure you saved the file
- Restart the bot completely
- Check for any Python syntax errors in the terminal

**If Previous button doesn't work:**
- Make sure tracks are playing (history needs to be populated)
- Check that the button was added correctly to PlayerControlView

**If playlists don't save:**
- Check if MongoDB is configured (MONGO_URI in .env)
- Check the console for any database errors
- Verify `playlist_storage.py` is in the correct directory

---

## ✨ Features Added

✅ `/playlist` command - Opens interactive playlist manager
✅ Save current queue as a playlist
✅ Load saved playlists
✅ Delete playlists
✅ View all saved playlists with pagination
✅ Previous track button (⏮️) in player controls
✅ `/previous` command
✅ Playlist name shown in now playing embed
✅ MongoDB/SQLite dual support for persistence
