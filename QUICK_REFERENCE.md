# Quick Reference Guide

Quick reference for common tasks and commands.

## Development Commands

### Starting the Bot
```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run bot
python bot.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Updating Dependencies
```bash
pip install --upgrade discord.py python-dotenv matplotlib aiosqlite
pip freeze > requirements.txt
```

## Server Management

### Service Control
```bash
# Start bot
sudo systemctl start gsc-bot

# Stop bot
sudo systemctl stop gsc-bot

# Restart bot
sudo systemctl restart gsc-bot

# Check status
sudo systemctl status gsc-bot

# Enable auto-start on boot
sudo systemctl enable gsc-bot
```

### Viewing Logs
```bash
# Live log stream
sudo journalctl -u gsc-bot -f

# Last 100 lines
sudo journalctl -u gsc-bot -n 100

# Today's logs
sudo journalctl -u gsc-bot --since today

# Logs with timestamps
sudo journalctl -u gsc-bot -o short-precise

# Logs from specific time
sudo journalctl -u gsc-bot --since "2 hours ago"
```

### Manual Deployment
```bash
cd /opt/gsc-bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart gsc-bot
```

## Database Operations

### Backup Database
```bash
# Full backup
cp /opt/gsc-bot/data/economy.db /backup/economy.db.$(date +%Y%m%d)

# With compression
tar -czf /backup/gsc-data-$(date +%Y%m%d).tar.gz /opt/gsc-bot/data/
```

### Restore Database
```bash
# Stop bot first
sudo systemctl stop gsc-bot

# Restore
cp /backup/economy.db /opt/gsc-bot/data/economy.db

# Restart bot
sudo systemctl start gsc-bot
```

### View Database
```bash
cd /opt/gsc-bot
sqlite3 data/economy.db

# Useful SQLite commands:
.tables              # List all tables
.schema players      # Show table structure
SELECT * FROM players LIMIT 10;  # View data
.quit               # Exit
```

## Git Operations

### Commit and Deploy
```bash
git add .
git commit -m "feat: your changes"
git push origin main
# Deployment happens automatically via GitHub Actions
```

### Create Feature Branch
```bash
git checkout -b feature/your-feature
# Make changes
git add .
git commit -m "feat: description"
git push origin feature/your-feature
# Create PR on GitHub
```

### Update from Main
```bash
git checkout main
git pull origin main
git checkout feature/your-feature
git merge main
```

## Configuration Changes

### Update Team Configuration
```bash
# Edit config
nano /opt/gsc-bot/config.py

# Restart bot
sudo systemctl restart gsc-bot
```

### Update Environment Variables
```bash
# Edit .env
sudo nano /opt/gsc-bot/.env

# Restart bot
sudo systemctl restart gsc-bot
```

## Troubleshooting

### Bot Won't Start
```bash
# Check logs
sudo journalctl -u gsc-bot -n 50

# Common issues:
# 1. Check .env file exists and has correct values
ls -la /opt/gsc-bot/.env

# 2. Check Python path
which python3

# 3. Check file permissions
ls -la /opt/gsc-bot/bot.py

# 4. Test Python script manually
cd /opt/gsc-bot
source venv/bin/activate
python bot.py
```

### Database Locked
```bash
# Stop bot
sudo systemctl stop gsc-bot

# Check for locks
lsof /opt/gsc-bot/data/economy.db

# Kill if needed (use PID from lsof)
kill -9 <PID>

# Restart bot
sudo systemctl start gsc-bot
```

### Disk Space Issues
```bash
# Check disk usage
df -h

# Check data directory size
du -sh /opt/gsc-bot/data/

# Clean old logs
sudo journalctl --vacuum-time=7d

# Clean old graphs
find /opt/gsc-bot/data/graphs/ -mtime +7 -delete
```

### Deployment Failed
```bash
# Check GitHub Actions logs on GitHub

# Manual deployment
ssh user@server
cd /opt/gsc-bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart gsc-bot
```

## Discord Operations

### Get IDs
```bash
# Enable Developer Mode in Discord:
# Settings → Advanced → Developer Mode

# Then:
# Server ID: Right-click server → Copy ID
# Role ID: Right-click role → Copy ID
# Channel ID: Right-click channel → Copy ID
# User ID: Right-click user → Copy ID
```

### Bot Permissions
Required permissions (integer: 274878237696):
- Read Messages/View Channels
- Send Messages
- Embed Links
- Attach Files
- Read Message History
- Use Slash Commands

### Test Bot Locally
```bash
# Use a test server
# Update .env with test server GUILD_ID
# Run bot locally:
python bot.py
```

## Data Management

### Reset Market Prices
```bash
# Stop bot
sudo systemctl stop gsc-bot

# Delete stock files (they'll be recreated)
rm /opt/gsc-bot/data/stocks/*.json

# Start bot
sudo systemctl start gsc-bot
```

### Export Data
```bash
# Export database to SQL
cd /opt/gsc-bot
sqlite3 data/economy.db .dump > economy_backup.sql

# Export stock data
tar -czf stocks_backup.tar.gz data/stocks/
```

## Monitoring

### Resource Usage
```bash
# Memory usage
free -h

# CPU usage
top -b -n 1 | head -20

# Bot process info
ps aux | grep python

# Detailed bot stats
systemctl status gsc-bot
```

### Check Bot Status
```bash
# Is bot running?
systemctl is-active gsc-bot

# When did bot start?
systemctl show gsc-bot -p ActiveEnterTimestamp

# How long has it been running?
systemctl show gsc-bot -p ActiveEnterTimestampMonotonic
```

## Useful Discord Bot Commands

### User Commands
- `/register` - Create account
- `/balance` - Check balance
- `/market` - View all stocks
- `/stock <symbol>` - Stock details
- `/buy <symbol> <amount>` - Buy shares
- `/sell <symbol> <amount>` - Sell shares
- `/portfolio` - View holdings
- `/leaderboard` - Top players
- `/graph <symbol>` - Price chart

### Admin Commands
- `/give <user> <cogs>` - Give currency
- `/take <user> <cogs>` - Take currency
- `/setprice <symbol> <price>` - Set price
- `/resetmarket` - Reset all prices

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Bot token | `MTAx...` |
| `GUILD_ID` | Discord server ID | `1234567890` |
| `ADMIN_ROLE_ID` | Admin role ID | `9876543210` |

## File Locations

| Path | Description |
|------|-------------|
| `/opt/gsc-bot/` | Bot installation directory |
| `/opt/gsc-bot/data/economy.db` | SQLite database |
| `/opt/gsc-bot/data/stocks/` | Stock JSON files |
| `/opt/gsc-bot/data/graphs/` | Generated charts |
| `/opt/gsc-bot/.env` | Environment config |
| `/etc/systemd/system/gsc-bot.service` | Systemd service |

## Support Resources

- **GitHub Issues**: https://github.com/yourusername/vn-stocks/issues
- **Documentation**: See `docs/` directory
- **Contributing**: See `CONTRIBUTING.md`
- **Deployment**: See `docs/DEPLOYMENT.md`
