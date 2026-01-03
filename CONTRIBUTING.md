# Contributing to GSC - Gearfall Stock Exchange

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

This project follows a standard code of conduct. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites
- Python 3.13 or higher
- Git
- Discord bot token for testing
- Basic knowledge of discord.py library and async/await patterns

### Setting Up Development Environment

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/vn-stocks.git
   cd vn-stocks
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Copy and configure `.env`:
   ```bash
   cp .env.example .env
   # Edit .env with your test bot credentials
   ```
6. Run the bot:
   ```bash
   python bot.py
   ```

### Project Structure
```
bot.py                   # Main bot instance and event handlers
commands_*.py            # Command cogs organized by category
market.py               # Market data layer (JSON storage)
market_simulator.py     # Price update background task
market_updates.py       # Periodic market broadcast
database.py             # SQLite operations
limit_orders.py         # Limit order execution logic
price_alerts.py         # Price alert checking
achievements.py         # Achievement system
graphing.py             # Line chart generation
candlestick.py          # Candlestick chart generation
live_graphs.py          # Live updating graph system
team_detection.py       # Message-to-team attribution
utils.py                # Utility functions (currency conversion, etc.)
config.py               # Configuration and constants
```

## Making Changes

### Branch Naming Convention
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Commit Message Guidelines
Use clear, descriptive commit messages:
- `feat: add leaderboard pagination`
- `fix: correct price calculation in market simulator`
- `docs: update installation instructions`
- `refactor: simplify team detection logic`

### Code Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused (single responsibility)
- Use type hints where appropriate

Example:
```python
async def get_user_balance(user_id: int) -> Optional[int]:
    """
    Retrieve a user's balance from the database.
    
    Args:
        user_id: Discord user ID
    
    Returns:
        Balance in Spurs, or None if user not found
    """
    # Implementation here
```

### Project-Specific Conventions

#### Currency Handling
- **Always** store values in Spurs internally (1 Cog = 64 Spurs)
- Use `utils.spurs_to_cogs_display()` for user-facing output
- Use `utils.cogs_to_spurs()` when parsing user input
- Never mix Cogs and Spurs in calculations

#### Database Operations
- All database operations must be async using `aiosqlite`
- Always use `async with database.get_db() as db:` context manager
- Commit after INSERT/UPDATE/DELETE operations
- Use parameterized queries to prevent SQL injection

#### Market Operations
- Access market data via `market.market` singleton
- All price updates must include timestamps
- Use `await` for all market operations
- Price history is stored in JSON files, not database

#### Command Structure
- Use `discord.app_commands` for slash commands (not text commands)
- Return `discord.Embed` objects for rich responses
- Make error messages ephemeral (`ephemeral=True`)
- Use emoji consistently:
  - ❌ for errors
  - ✅ for success
  - 📈/📉 for market movements
  - 💰 for money
  - 🔔 for notifications

#### Background Tasks
- Use `@tasks.loop()` from `discord.ext.tasks`
- Always handle exceptions in background loops
- Log errors with `logger.error()`
- Don't block the bot with long-running operations

#### Cog Structure
- Create separate files for each command category (`commands_*.py`)
- Include `async def setup(bot):` function
- Add cog name to `bot.py` initial_extensions list
- Use descriptive command names and descriptions

## Feature Development

### Adding New Features
When adding a major feature:

1. **Database Schema**: Update `database.py` with new tables
2. **Business Logic**: Create separate module (e.g., `limit_orders.py`)
3. **Commands**: Add user-facing commands in `commands_*.py`
4. **Integration**: Hook into background tasks if needed
5. **Documentation**: Update `docs/FEATURES.md`

### Example: Adding a New Stock
1. Add to `config.TEAMS` dict with all required fields
2. Add role name for Discord attribution
3. Add tags to `config.TEAM_TAGS` for message parsing
4. Restart bot to generate JSON file

## Testing

### Manual Testing Checklist
Before submitting a PR, test the following:
- [ ] Bot starts without errors
- [ ] Commands respond correctly
- [ ] Database operations work
- [ ] Market updates continue running
- [ ] Limit orders execute properly
- [ ] Price alerts trigger and send DMs
- [ ] Graphs generate without errors
- [ ] No crashes during extended runtime
- [ ] Error messages are user-friendly

### Testing New Commands
1. Register command in appropriate `commands_*.py` file
2. Add to `bot.py` initial_extensions
3. Test with valid inputs
4. Test with invalid inputs (error handling)
5. Test permission requirements (if applicable)
6. Verify ephemeral/public message behavior
7. Check database state after execution

## Pull Request Process

1. **Update your fork**:
   ```bash
   git fetch upstream
   git merge upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** following the guidelines above

4. **Test thoroughly** using the manual testing checklist

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: your descriptive message"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request** on GitHub:
   - Provide a clear title and description
   - Reference any related issues
   - Describe what changed and why
   - Include screenshots for UI changes

### PR Review Process
- Maintainers will review your PR within a few days
- Address any requested changes
- Once approved, your PR will be merged

## Areas for Contribution

### Good First Issues
- Adding new team tags to `config.TEAM_TAGS`
- Improving error messages
- Adding command aliases
- Updating documentation

### Feature Ideas
- Transaction history command
- Price alerts/notifications
- Trading analytics dashboard
- Market manipulation detection
- Multi-guild support

### Bug Reports
When reporting bugs, include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Bot version/commit hash
- Error messages/logs
- Screenshots (if applicable)

## Architecture Reference

### Key Components
- `bot.py` - Main entry point, message handling
- `commands_*.py` - Command cogs organized by category
- `market.py` - Market data layer (JSON storage)
- `market_simulator.py` - Background price updates
- `database.py` - SQLite operations
- `team_detection.py` - Message-to-team attribution

### Data Flow
```
User Command → Command Handler → Database/Market → Response Embed
Discord Message → Team Detection → Activity Score → Market Simulator
Market Simulator → Price Update → JSON Storage → Market Broadcast
```

### Adding a New Stock
1. Add team config to `config.TEAMS`
2. Add role name to team config
3. Add tags to `config.TEAM_TAGS`
4. Restart bot (JSON file auto-generated)

### Modifying Price Algorithm
Edit `market_simulator.py`:
- `_calculate_new_price()` - Core price formula
- Adjust random walk, activity impact, or momentum
- Test with various activity levels

## Questions?

- Check existing issues and discussions
- Read the [AI coding guide](.github/copilot-instructions.md)
- Ask in GitHub Discussions
- Open an issue for clarification

Thank you for contributing to making GSC better! 🎉
