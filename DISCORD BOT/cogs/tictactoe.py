import discord
from discord.ext import commands
from discord import app_commands
import random
from typing import Optional
from datetime import datetime

class TicTacToeButton(discord.ui.Button):
    """A button representing a cell in the Tic-Tac-Toe board."""
    
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        view: TicTacToeView = self.view
        
        # Check if it's the correct player's turn
        if interaction.user.id != view.current_player.id:
            await interaction.response.send_message(
                "⚠️ **Hold on!** It's not your turn yet! Let your opponent make their move first! 🎯",
                ephemeral=True
            )
            return
        
        # Check if cell is already taken
        if view.board[self.y][self.x] is not None:
            await interaction.response.send_message(
                "🚫 **Oops!** This cell is already occupied! Choose an empty one! ✨",
                ephemeral=True
            )
            return
        
        # Make the move
        view.board[self.y][self.x] = view.current_player
        
        # Update button appearance with enhanced styling
        if view.current_player == view.player_x:
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.emoji = '❌'
        else:
            self.style = discord.ButtonStyle.primary
            self.label = 'O'
            self.emoji = '⭕'
        
        self.disabled = True
        view.moves_made += 1
        
        # Check for winner
        winner = view.check_winner()
        
        if winner:
            # Game won
            view.game_over = True
            await view.end_game(interaction, winner, is_draw=False)
        elif view.moves_made >= 9:
            # Draw
            view.game_over = True
            await view.end_game(interaction, None, is_draw=True)
        else:
            # Switch turns
            view.current_player = view.player_o if view.current_player == view.player_x else view.player_x
            view.update_embed()
            await interaction.response.edit_message(embed=view.embed, view=view)


class TicTacToeView(discord.ui.View):
    """The game view containing all the buttons and game logic."""
    
    # Celebratory messages for wins
    WIN_MESSAGES = [
        "🎊 **SPECTACULAR VICTORY!** 🎊",
        "⭐ **FLAWLESS TRIUMPH!** ⭐",
        "🏆 **CHAMPION CROWNED!** 🏆",
        "💫 **LEGENDARY WIN!** 💫",
        "🎯 **PERFECT EXECUTION!** 🎯",
        "🌟 **OUTSTANDING VICTORY!** 🌟",
        "🔥 **DOMINATED THE BOARD!** 🔥",
        "👑 **SUPREME CHAMPION!** 👑"
    ]
    
    # Draw messages
    DRAW_MESSAGES = [
        "🤝 **EVENLY MATCHED!** An honorable draw! 🤝",
        "⚖️ **PERFECTLY BALANCED!** What a close match! ⚖️",
        "🎭 **STALEMATE!** Both players showed incredible skill! 🎭",
        "🌈 **TIE GAME!** You're both winners in our hearts! 🌈",
        "🎪 **NECK AND NECK!** Nobody could break through! 🎪"
    ]
    
    def __init__(self, player_x: discord.User, player_o: discord.User):
        super().__init__(timeout=300)  # 5 minute timeout
        self.player_x = player_x
        self.player_o = player_o
        self.current_player = player_x  # X always goes first
        self.board = [[None, None, None] for _ in range(3)]
        self.moves_made = 0
        self.game_over = False
        self.start_time = datetime.now()
        
        # Create the 3x3 grid of buttons
        for y in range(3):
            for x in range(3):
                self.add_item(TicTacToeButton(x, y))
        
        self.embed = self.create_embed()
    
    def create_embed(self) -> discord.Embed:
        """Create the game embed with enhanced styling."""
        # Vibrant gradient color
        embed = discord.Embed(
            title="🎮 ═══ TIC-TAC-TOE BATTLE ═══ 🎮",
            description="```\n⚔️  May the best player win!  ⚔️\n```",
            color=0x00FF88  # Bright cyan/green
        )
        
        # Players section with enhanced formatting
        player_info = (
            f"┏━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┃  ❌ **Player X**\n"
            f"┃  {self.player_x.mention}\n"
            f"┃\n"
            f"┃  ⭕ **Player O**\n"
            f"┃  {self.player_o.mention}\n"
            f"┗━━━━━━━━━━━━━━━━━━━━━━━┛"
        )
        embed.add_field(
            name="🎯 COMBATANTS",
            value=player_info,
            inline=False
        )
        
        # Current turn with animation
        turn_symbol = '❌' if self.current_player == self.player_x else '⭕'
        turn_text = (
            f"```css\n"
            f">>> {turn_symbol} It's {self.current_player.display_name}'s turn! <<<\n"
            f"```"
        )
        embed.add_field(
            name="⚡ CURRENT TURN",
            value=turn_text,
            inline=False
        )
        
        # Game stats
        embed.add_field(
            name="📊 GAME INFO",
            value=f"**Moves Made:** {self.moves_made}/9\n**Time Elapsed:** <t:{int(self.start_time.timestamp())}:R>",
            inline=False
        )
        
        embed.set_footer(
            text="🎯 Click on an empty cell to make your move! | ⏰ 5 min timeout",
            icon_url="https://em-content.zobj.net/thumbs/120/twitter/348/video-game_1f3ae.png"
        )
        
        # Add thumbnail for extra flair
        embed.set_thumbnail(url="https://em-content.zobj.net/thumbs/120/twitter/348/crossed-swords_2694-fe0f.png")
        
        return embed
    
    def update_embed(self):
        """Update the embed with current game state."""
        self.embed.clear_fields()
        
        # Update color based on who's turn it is
        if self.current_player == self.player_x:
            self.embed.color = 0xFF3366  # Red for X
        else:
            self.embed.color = 0x3366FF  # Blue for O
        
        # Players section
        player_info = (
            f"┏━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┃  ❌ **Player X**\n"
            f"┃  {self.player_x.mention}\n"
            f"┃\n"
            f"┃  ⭕ **Player O**\n"
            f"┃  {self.player_o.mention}\n"
            f"┗━━━━━━━━━━━━━━━━━━━━━━━┛"
        )
        self.embed.add_field(
            name="🎯 COMBATANTS",
            value=player_info,
            inline=False
        )
        
        # Current turn
        turn_symbol = '❌' if self.current_player == self.player_x else '⭕'
        turn_text = (
            f"```css\n"
            f">>> {turn_symbol} It's {self.current_player.display_name}'s turn! <<<\n"
            f"```"
        )
        self.embed.add_field(
            name="⚡ CURRENT TURN",
            value=turn_text,
            inline=False
        )
        
        # Game stats
        elapsed = datetime.now() - self.start_time
        self.embed.add_field(
            name="📊 GAME INFO",
            value=f"**Moves Made:** {self.moves_made}/9\n**Time Elapsed:** <t:{int(self.start_time.timestamp())}:R>",
            inline=False
        )
    
    def check_winner(self) -> Optional[discord.User]:
        """Check if there's a winner."""
        # Check rows
        for row in self.board:
            if row[0] == row[1] == row[2] and row[0] is not None:
                return row[0]
        
        # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] and self.board[0][col] is not None:
                return self.board[0][col]
        
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] and self.board[0][0] is not None:
            return self.board[0][0]
        
        if self.board[0][2] == self.board[1][1] == self.board[2][0] and self.board[0][2] is not None:
            return self.board[0][2]
        
        return None
    
    async def end_game(self, interaction: discord.Interaction, winner: Optional[discord.User], is_draw: bool):
        """End the game and display spectacular results."""
        # Disable all buttons
        for child in self.children:
            child.disabled = True
        
        # Calculate game duration
        game_duration = datetime.now() - self.start_time
        duration_text = f"{game_duration.seconds // 60}m {game_duration.seconds % 60}s"
        
        # Create spectacular end game embed
        if is_draw:
            embed = discord.Embed(
                title="🎭 ══════════════════ 🎭",
                description=f"## {random.choice(self.DRAW_MESSAGES)}",
                color=0xFFD700  # Gold color
            )
            
            embed.add_field(
                name="🎯 FINAL BOARD",
                value=(
                    f"┏━━━━━━━━━━━━━━━━━┓\n"
                    f"┃  ❌ {self.player_x.mention}\n"
                    f"┃  ⭕ {self.player_o.mention}\n"
                    f"┗━━━━━━━━━━━━━━━━━┛"
                ),
                inline=False
            )
            
            embed.add_field(
                name="📊 MATCH STATISTICS",
                value=(
                    f"**Total Moves:** {self.moves_made}\n"
                    f"**Duration:** {duration_text}\n"
                    f"**Result:** Draw - Both players are champions! 🏆"
                ),
                inline=False
            )
            
            embed.set_footer(
                text="🎮 Great game! Ready for a rematch? Use /ttt to play again!",
                icon_url="https://em-content.zobj.net/thumbs/120/twitter/348/trophy_1f3c6.png"
            )
            embed.set_thumbnail(url="https://em-content.zobj.net/thumbs/120/twitter/348/handshake_1f91d.png")
            
        else:
            # Winner celebration
            winner_symbol = '❌' if winner == self.player_x else '⭕'
            loser = self.player_o if winner == self.player_x else self.player_x
            
            embed = discord.Embed(
                title="🎉 ══════════════════ 🎉",
                description=f"## {random.choice(self.WIN_MESSAGES)}",
                color=0xFF1493 if winner == self.player_x else 0x1E90FF  # Pink for X, Blue for O
            )
            
            # Winner announcement with fireworks
            winner_text = (
                f"```diff\n"
                f"+ {winner_symbol} {winner.display_name.upper()} IS VICTORIOUS! {winner_symbol}\n"
                f"```\n"
                f"🎊 {winner.mention} has conquered the board! 🎊\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
            embed.add_field(
                name="👑 CHAMPION",
                value=winner_text,
                inline=False
            )
            
            embed.add_field(
                name="⚔️ WARRIORS",
                value=(
                    f"**🏆 Winner:** {winner.mention}\n"
                    f"**🎖️ Opponent:** {loser.mention}"
                ),
                inline=False
            )
            
            embed.add_field(
                name="📊 MATCH STATISTICS",
                value=(
                    f"**Total Moves:** {self.moves_made}\n"
                    f"**Duration:** {duration_text}\n"
                    f"**Winner's Symbol:** {winner_symbol}\n"
                    f"**Victory Type:** {"Lightning Fast!" if self.moves_made < 6 else "Strategic Masterclass!" if self.moves_made < 8 else "Hard-Fought Battle!"}"
                ),
                inline=False
            )
            
            # Add special achievement messages
            achievements = []
            if self.moves_made == 5:
                achievements.append("⚡ **SPEED DEMON!** Won in minimum moves!")
            if self.moves_made < 7:
                achievements.append("🎯 **TACTICAL GENIUS!** Quick and decisive victory!")
            
            if achievements:
                embed.add_field(
                    name="🏅 ACHIEVEMENTS UNLOCKED",
                    value="\n".join(achievements),
                    inline=False
                )
            
            embed.set_footer(
                text=f"🎊 Congratulations to {winner.display_name}! | 🎮 Play again with /ttt!",
                icon_url="https://em-content.zobj.net/thumbs/120/twitter/348/party-popper_1f389.png"
            )
            embed.set_thumbnail(url="https://em-content.zobj.net/thumbs/120/twitter/348/trophy_1f3c6.png")
        
        # Send the spectacular end game message
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def on_timeout(self):
        """Called when the view times out."""
        # Disable all buttons
        for child in self.children:
            child.disabled = True


class TicTacToe(commands.Cog):
    """A Tic-Tac-Toe game cog for Discord with spectacular UI."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="tictactoe", description="🎮 Start an epic Tic-Tac-Toe battle!")
    @app_commands.describe(opponent="⚔️ Choose your worthy opponent!")
    async def tictactoe(self, interaction: discord.Interaction, opponent: discord.User):
        """Start a new Tic-Tac-Toe game with enhanced visuals."""
        
        # Validation checks with better messages
        if opponent.id == interaction.user.id:
            error_embed = discord.Embed(
                title="❌ Invalid Opponent",
                description="🤔 You can't battle yourself! Challenge another player instead!",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return
        
        if opponent.bot:
            error_embed = discord.Embed(
                title="🤖 Invalid Opponent",
                description="🚫 Bots aren't programmed for this epic challenge! Choose a human player!",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return
        
        # Randomly decide who goes first (X)
        if random.choice([True, False]):
            player_x = interaction.user
            player_o = opponent
        else:
            player_x = opponent
            player_o = interaction.user
        
        # Create the game
        view = TicTacToeView(player_x, player_o)
        
        # Send epic game start message
        start_message = (
            f"# ⚔️ BATTLE INITIATED! ⚔️\n\n"
            f"**{player_x.mention}** *(❌ X)* **VS** **{player_o.mention}** *(⭕ O)*\n\n"
            f"```diff\n"
            f"+ {player_x.display_name} will make the first move!\n"
            f"```\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 **The battleground is set!** Click the grid below to make your move!\n"
            f"⏰ You have **5 minutes** to complete this epic showdown!"
        )
        
        await interaction.response.send_message(
            content=start_message,
            embed=view.embed,
            view=view
        )
    
    @app_commands.command(name="ttt", description="🎮 Quick start a Tic-Tac-Toe game!")
    @app_commands.describe(opponent="⚔️ Choose your opponent!")
    async def ttt(self, interaction: discord.Interaction, opponent: discord.User):
        """Shorthand command for Tic-Tac-Toe."""
        await self.tictactoe(interaction, opponent)


async def setup(bot):
    await bot.add_cog(TicTacToe(bot))
