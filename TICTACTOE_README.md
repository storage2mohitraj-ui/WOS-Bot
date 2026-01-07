# 🎮 Tic-Tac-Toe Game Feature

## Overview
An interactive Tic-Tac-Toe game for Discord! Play with your friends using Discord's button UI for a smooth and modern gaming experience.

## Features
- ✅ **Interactive Gameplay**: Click buttons to make your moves
- ✅ **Two-Player Mode**: Challenge any member in your server
- ✅ **Visual Feedback**: Color-coded buttons (Red for X, Blue for O)
- ✅ **Smart Win Detection**: Automatically detects wins and draws
- ✅ **Beautiful Embeds**: Clean, modern UI with Discord embeds
- ✅ **Random Turn Assignment**: Fair random selection of who goes first
- ✅ **Timeout Protection**: Games expire after 5 minutes of inactivity

## Commands

### `/tictactoe @opponent`
Start a new Tic-Tac-Toe game with the specified opponent.

**Example:**
```
/tictactoe @Friend
```

### `/ttt @opponent`
Shorthand version of the tictactoe command.

**Example:**
```
/ttt @Friend
```

## How to Play

1. **Start a Game**: Use `/tictactoe @opponent` or `/ttt @opponent`
2. **Random Selection**: The bot randomly assigns who plays as X (goes first) and who plays as O
3. **Take Turns**: Click on empty cells to place your mark
4. **Win Condition**: Get three in a row (horizontal, vertical, or diagonal)
5. **Draw**: If all 9 cells are filled with no winner, it's a draw

## Game Rules

- ❌ **X always goes first** (randomly assigned)
- 🔄 **Players alternate turns**
- ✋ **Can't play on occupied cells**
- ⏰ **Game expires after 5 minutes of no activity**
- 🚫 **Can't play against yourself**
- 🤖 **Can't play against bots**

## Visual Example

When you start a game, you'll see:
- An embed showing both players
- Current turn indicator
- A 3x3 grid of clickable buttons
- Real-time updates as moves are made
- Win/draw announcement with special formatting

## Technical Details

### File Location
- **Cog file**: `cogs/tictactoe.py`
- **Loaded in**: `app.py` (automatically on bot startup)

### Classes
- `TicTacToe`: Main cog class with slash commands
- `TicTacToeView`: View containing the game board and logic
- `TicTacToeButton`: Individual button for each cell

### Features
- Persistent view with 300-second timeout
- Win detection for all 8 possible winning combinations
- Draw detection when board is full
- Turn validation to prevent wrong player moves
- Cell occupancy validation

## Troubleshooting

**Q: The buttons don't respond**
A: Make sure it's your turn! Only the current player can make a move.

**Q: I can't challenge a bot**
A: This is by design - bots can't play interactive games.

**Q: Game disappeared**
A: Games timeout after 5 minutes. Start a new one!

**Q: Can I play multiple games at once?**
A: Yes! Each game is independent, so you can play in multiple channels or have multiple games running.

## Future Enhancements (Potential)
- 🤖 Single-player mode against AI
- 📊 Win/loss statistics tracking
- 🏆 Leaderboard system
- 🎨 Custom emoji support for X and O
- ⚙️ Configurable board sizes (4x4, 5x5)
- 🎭 Different game themes

## Enjoy!
Have fun playing Tic-Tac-Toe with your Discord friends! 🎉
