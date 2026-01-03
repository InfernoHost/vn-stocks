# GSC - Gearfall Stock Exchange

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)
![Discord.py](https://img.shields.io/badge/discord.py-2.3+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Discord bot that simulates a stock market for your server. Trade team stocks, set limit orders, track your portfolio, and compete on the leaderboard.

[Features](#features) • [Installation](#installation) • [Configuration](#configuration) • [Commands](#commands) • [Contributing](#contributing)

</div>

---

## Features

### 💰 Dual Currency System
- **Cogs** and **Spurs** (1 Cog = 64 Spurs)
- Automatic conversion
- Everyone starts with 10 Cogs

### 📈 Dynamic Market
- Prices update every 3 minutes
- Influenced by server activity (your messages matter!)
- Random volatility keeps things interesting
- Momentum and trend tracking
- Spam protection with cooldowns

### 👥 Team Stocks
Six teams to trade:
- **STMP** - Team Steampire
- **VOC** - Team VOC
- **CRAV** - Team Crava
- **ROSE** - Team Rose
- **VIOL** - Team Violet
- **POT** - Team Potchi

### 📊 Advanced Analytics
- **Portfolio Breakdown**: Pie charts of your holdings
- **Price Graphs**: TradingView-style charts with live updates
- **Candlestick Charts**: OHLC data for technical traders
- **Trade History**: See all your past trades with P/L
- **Leaderboard**: Compete for the top spot

### 🎯 Trading Features
- **Limit Orders**: Set buy/sell orders that trigger at your price
- **Price Alerts**: Get DM'd when stocks hit your targets
- **Watchlist**: Keep an eye on stocks before buying

### 🏆 Achievements
Earn badges for milestones:
- 💰 Millionaire - Hit 1M Spurs
- 💎 Diamond Hands - Hold for 7+ days
- 📊 Day Trader - 10+ trades in a day
- 🌈 Diversified - Own all 6 teams
- 🐋 Whale - 100k+ Cog trade
- And more!

### 🛡️ Anti-Cheat
- Message cooldowns (60s)
- Role and tag-based team detection
- Admin tools for managing the economy

---

## Installation

### What You Need
- Python 3.13+
- Discord bot token ([Get one here](https://discord.com/developers/applications))
- A Discord server with admin perms

### Setup

1. **Clone it**
   ```bash
   git clone https://github.com/yourusername/vn-stocks.git
   cd vn-stocks
   ```

2. **Install stuff**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your info:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   GUILD_ID=your_server_id_here
   ADMIN_ROLE_ID=your_admin_role_id_here
   ```

4. **Run it**
   ```bash
   python bot.py
   ```

The bot creates all the data folders and database on first run.

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

### 📊 Trading Commands
| Command | Description | Example |
|---------|-------------|---------|
| `/register` | Create a trading account | `/register` |
| `/balance` | View your balance | `/balance` |
| `/buy <symbol> <amount>` | Purchase stock shares | `/buy STMP 10` |
| `/sell <symbol> <amount>` | Sell stock shares | `/sell ROSE 5` |
| `/portfolio` | View your holdings with analytics and pie chart | `/portfolio` |

### 📈 Market Information
| Command | Description | Example |
|---------|-------------|---------|
| `/market` | List all stocks and prices | `/market` |
| `/stock <symbol>` | View details for a specific stock | `/stock STMP` |
| `/graph <symbol>` | Display price history graph (live updating) | `/graph VOC` |
| `/candlestick <symbol> [hours]` | View OHLC candlestick chart | `/candlestick STMP 24` |
| `/leaderboard` | View top players by total value | `/leaderboard` |

### 🎯 Advanced Trading
| Command | Description | Example |
|---------|-------------|---------|
| `/limitbuy <symbol> <shares> <price>` | Set limit buy order (auto-executes at target price) | `/limitbuy STMP 10 15.5` |
| `/limitsell <symbol> <shares> <price>` | Set limit sell order | `/limitsell ROSE 5 20` |
| `/orders` | View your active limit orders | `/orders` |
| `/cancelorder <id>` | Cancel a limit order | `/cancelorder 123` |

### 🔔 Alerts & Watchlist
| Command | Description | Example |
|---------|-------------|---------|
| `/alert <symbol> <condition> <price>` | Set price alert (get DM when triggered) | `/alert STMP above 18` |
| `/alerts` | View your active alerts | `/alerts` |
| `/removealert <id>` | Remove a price alert | `/removealert 5` |
| `/watch <symbol>` | Add stock to watchlist | `/watch CRAV` |
| `/unwatch <symbol>` | Remove from watchlist | `/unwatch CRAV` |
| `/watchlist` | View your watchlist with 24h changes | `/watchlist` |

### 📜 History & Analytics
| Command | Description | Example |
|---------|-------------|---------|
| `/history [days] [symbol]` | View trade history with P/L | `/history 7 STMP` |
| `/achievements` | View unlocked achievements and progress | `/achievements` |

### ⚙️ Admin Commands
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
Price Updates → JSON Storage → Limit Order Execution
       ↓                              ↓
Database Transactions    Price Alert Checks → DM Notifications
```

### Storage
- **SQLite** (`data/economy.db`): Player balances, portfolios, transactions, limit orders, alerts, watchlists, achievements
- **JSON** (`data/stocks/*.json`): Stock prices, price history, OHLC data, metadata
- **PNG** (`data/graphs/*.png`): Generated price charts and portfolio visualizations

### Background Tasks
- **Market Simulator**: Updates prices every 3 minutes, executes limit orders
- **Price Alerts Checker**: Monitors alerts and sends DM notifications every minute
- **Market Broadcaster**: Posts price updates to designated channel every 15 minutes
- **Live Graph Updater**: Refreshes active graph displays every 30 seconds

---

## Deployment

### Manual Deployment
Follow the [Installation](#installation) steps on your server.

### Automated Deployment (Ubuntu Server)
This project includes GitHub Actions for automatic deployment on each commit:

1. **Server Setup**
   - Ubuntu server with SSH access
   - Python 3.13+ installed
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

- **Issues**: [GitHub Issues](https://github.com/InfernoHost/vn-stocks/issues)
- **Discussions**: [GitHub Discussions](https://github.com/InfernoHost/vn-stocks/discussions)

---

<div align="center">
Made with ❤️ for the Voltcore Network players.
</div>
