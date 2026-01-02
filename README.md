# GSC - Gearfall Stock Exchange

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![Discord.py](https://img.shields.io/badge/discord.py-2.3+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A Discord bot for simulating a stock market economy tied to team activity. Players trade team stocks, track portfolios, and watch prices fluctuate based on real-time server engagement.

[Features](#features) • [Installation](#installation) • [Configuration](#configuration) • [Commands](#commands) • [Contributing](#contributing)

</div>

---

## Features

### 💰 Dual Currency System
- **Cogs** and **Spurs** (1 Cog = 64 Spurs)
- Automatic conversion between denominations
- Starting balance: 10 Cogs per player

### 📈 Dynamic Market Simulation
- Prices update every 3 minutes based on:
  - Random market movements (volatility)
  - Team activity scores (message-driven)
  - Momentum and trend persistence
- Activity decay prevents spam manipulation

### 👥 Team-Based Trading
Six teams with tradeable stocks:
- **STMP** - Team Steampire
- **VOC** - Team VOC
- **CRAV** - Team Crava
- **ROSE** - Team Rose
- **VIOL** - Team Violet
- **POT** - Team Potchi

### 📊 Analytics & Visualization
- Portfolio tracking with profit/loss calculations
- Price history graphs (matplotlib)
- Leaderboard rankings by total value

### 🛡️ Anti-Manipulation Features
- Message cooldowns (60s between market-influencing messages)
- Role-based and tag-based team attribution
- Admin tools for economy management

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Discord bot token ([Create one here](https://discord.com/developers/applications))
- Discord server with appropriate permissions

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/vn-stocks.git
   cd vn-stocks
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your credentials:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   GUILD_ID=your_server_id_here
   ADMIN_ROLE_ID=your_admin_role_id_here
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

The bot will automatically create the necessary data directories and database on first run.

---

## Configuration

### Team Settings
Edit `config.py` to customize teams:
```python
TEAMS = {
    'SYMBOL': {
        'name': 'Team Name',
        'symbol': 'SYMBOL',
        'starting_price': 1 * SPURS_PER_COG,  # 1 Cog
        'volatility': 0.02,  # 2% volatility
        'role_name': 'Discord Role Name'
    }
}
```

### Market Parameters
Key configuration options in `config.py`:
- `MARKET_UPDATE_INTERVAL`: Price update frequency (default: 180s)
- `MESSAGE_COOLDOWN`: Minimum time between market-influencing messages (default: 60s)
- `ACTIVITY_DECAY`: Activity score decay per update (default: 0.95)
- `ACTIVITY_IMPACT`: Message impact on price movement (default: 0.001)

### Team Tags
Map message tags to teams in `config.TEAM_TAGS`:
```python
TEAM_TAGS = {
    'NH': 'STMP',
    'STEAMPIRE': 'STMP',
    # ... more tags
}
```

---

## Commands

### User Commands
| Command | Description | Example |
|---------|-------------|---------|
| `/register` | Create a trading account | `/register` |
| `/balance` | View your balance | `/balance` |
| `/market` | List all stocks and prices | `/market` |
| `/stock <symbol>` | View details for a specific stock | `/stock STMP` |
| `/buy <symbol> <amount>` | Purchase stock shares | `/buy STMP 10` |
| `/sell <symbol> <amount>` | Sell stock shares | `/sell ROSE 5` |
| `/portfolio` | View your holdings | `/portfolio` |
| `/leaderboard` | View top players by total value | `/leaderboard` |
| `/graph <symbol>` | Display price history graph | `/graph VOC` |

### Admin Commands
| Command | Description | Example |
|---------|-------------|---------|
| `/give <user> <cogs>` | Grant currency to a user | `/give @player 100` |
| `/take <user> <cogs>` | Remove currency from a user | `/take @player 50` |
| `/setprice <symbol> <price>` | Manually set a stock price | `/setprice CRAV 150` |
| `/resetmarket` | Reset all prices to starting values | `/resetmarket` |

---

## Architecture

### Data Flow
```
Discord Messages → Team Detection → Activity Score
                                         ↓
Market Simulator ← Activity Scores + Volatility + Momentum
       ↓
Price Updates → JSON Storage → Database Transactions
```

### Storage
- **SQLite** (`data/economy.db`): Player balances, portfolios, transactions
- **JSON** (`data/stocks/*.json`): Stock prices, price history, metadata
- **PNG** (`data/graphs/*.png`): Generated price charts

### Background Tasks
- **Market Simulator**: Updates prices every 3 minutes
- **Market Broadcaster**: Posts price updates to designated channel every 15 minutes

---

## Deployment

### Manual Deployment
Follow the [Installation](#installation) steps on your server.

### Automated Deployment (Ubuntu Server)
This project includes GitHub Actions for automatic deployment on each commit:

1. **Server Setup**
   - Ubuntu server with SSH access
   - Python 3.8+ installed
   - User with sudo privileges

2. **GitHub Secrets Configuration**
   Add these secrets to your repository:
   - `DEPLOY_HOST`: Server hostname/IP
   - `DEPLOY_USER`: SSH username
   - `DEPLOY_KEY`: SSH private key
   - `DISCORD_TOKEN`: Bot token
   - `GUILD_ID`: Discord server ID
   - `ADMIN_ROLE_ID`: Admin role ID

3. **Deploy**
   ```bash
   git push origin main
   ```
   The bot will automatically update and restart on the server.

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

---

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting PRs.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (if applicable)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and concise

---

## Project Structure
```
.
├── bot.py                  # Main bot entry point
├── commands_*.py           # Command cogs (user, admin, stock, graph, info)
├── config.py               # Configuration and team definitions
├── database.py             # SQLite database operations
├── market.py               # Market data management (JSON)
├── market_simulator.py     # Background price update loop
├── market_updates.py       # Periodic market broadcasts
├── team_detection.py       # Message-to-team attribution logic
├── utils.py                # Currency formatting utilities
├── graphing.py             # Price chart generation
├── data/                   # Auto-generated data directory
│   ├── economy.db         # SQLite database
│   ├── stocks/            # Per-stock JSON files
│   └── graphs/            # Generated PNG charts
└── .github/
    ├── workflows/         # GitHub Actions
    └── copilot-instructions.md  # AI coding assistant guide
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/vn-stocks/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/vn-stocks/discussions)

---

<div align="center">
Made with ❤️ for the Gearfall Minecraft community
</div>
