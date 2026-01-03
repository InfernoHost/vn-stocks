# Project Setup Checklist

This checklist will guide you through setting up the GSC Discord bot from scratch.

## Local Development Setup

- [ ] **Clone the repository**
  ```bash
  git clone https://github.com/yourusername/vn-stocks.git
  cd vn-stocks
  ```

- [ ] **Create virtual environment**
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  ```

- [ ] **Install dependencies**
  ```bash
  pip install -r requirements.txt
  ```

- [ ] **Create Discord bot** at https://discord.com/developers/applications
  - Enable "Message Content Intent" in Bot settings
  - Generate bot token
  - Add bot to your server with appropriate permissions

- [ ] **Configure environment**
  ```bash
  cp .env.example .env
  ```
  Edit `.env` with your values:
  - `DISCORD_TOKEN` - Your bot token
  - `GUILD_ID` - Your Discord server ID
  - `ADMIN_ROLE_ID` - Role ID for admin commands

- [ ] **Configure team roles**
  - Verify role names in `config.py` match your Discord server
  - Add any additional team tags to `config.TEAM_TAGS`

- [ ] **Run the bot**
  ```bash
  python bot.py
  ```

- [ ] **Test basic commands**
  - `/register` - Create account
  - `/market` - View stocks
  - `/balance` - Check balance

## Production Deployment Setup

- [ ] **Prepare Ubuntu server**
  - Ubuntu 18.04 or later
  - SSH access with sudo privileges
  - Python 3.13+ installed

- [ ] **Run setup script on server**
  ```bash
  wget https://raw.githubusercontent.com/yourusername/vn-stocks/main/scripts/setup.sh
  chmod +x setup.sh
  sudo ./setup.sh
  ```

- [ ] **Configure server .env file**
  ```bash
  sudo nano /opt/gsc-bot/.env
  ```
  Add production credentials

- [ ] **Start the bot service**
  ```bash
  sudo systemctl start gsc-bot
  sudo systemctl status gsc-bot
  ```

- [ ] **Generate SSH key for GitHub Actions**
  ```bash
  ssh-keygen -t ed25519 -f ~/.ssh/github_actions -N ""
  cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
  ```

- [ ] **Configure GitHub repository secrets**
  - `DEPLOY_HOST` - Server IP/hostname
  - `DEPLOY_USER` - SSH username
  - `DEPLOY_KEY` - Private key from `~/.ssh/github_actions`
  - `DISCORD_TOKEN` - Bot token
  - `GUILD_ID` - Server ID
  - `ADMIN_ROLE_ID` - Admin role ID

- [ ] **Grant sudo permissions** for deployment
  ```bash
  sudo visudo
  ```
  Add: `username ALL=(ALL) NOPASSWD: /bin/systemctl restart gsc-bot, /bin/systemctl status gsc-bot`

- [ ] **Test automatic deployment**
  ```bash
  git commit --allow-empty -m "test: deployment"
  git push origin main
  ```
  Check GitHub Actions tab for status

- [ ] **Configure systemd for auto-start**
  ```bash
  sudo systemctl enable gsc-bot
  ```

- [ ] **Set up log monitoring** (optional)
  - Configure log rotation in `/etc/systemd/journald.conf`
  - Set up monitoring alerts

## Post-Setup Configuration

- [ ] **Customize market parameters** in `config.py`
  - `MARKET_UPDATE_INTERVAL` - Price update frequency
  - `MESSAGE_COOLDOWN` - Anti-spam cooldown
  - `ACTIVITY_IMPACT` - Message influence strength
  - Team volatility values

- [ ] **Configure market updates channel**
  - Set `MARKET_UPDATES_CHANNEL_ID` in `config.py`
  - Adjust `MARKET_UPDATES_INTERVAL` (default: 15 min)

- [ ] **Set up Discord permissions**
  - Ensure bot can read messages in monitored channels
  - Verify bot can send embeds and files
  - Test admin commands with admin role

- [ ] **Backup strategy**
  - Schedule regular backups of `/opt/gsc-bot/data/`
  - Store backups off-server
  - Test restoration process

## Maintenance Checklist

### Daily
- [ ] Check bot uptime: `sudo systemctl status gsc-bot`
- [ ] Monitor logs for errors: `sudo journalctl -u gsc-bot -n 100`

### Weekly
- [ ] Review transaction patterns for anomalies
- [ ] Check database size: `du -h /opt/gsc-bot/data/economy.db`
- [ ] Verify all teams have activity

### Monthly
- [ ] Backup database and market data
- [ ] Review and update team configurations
- [ ] Check for dependency updates: `pip list --outdated`
- [ ] Review and address GitHub issues

### As Needed
- [ ] Adjust volatility for balanced gameplay
- [ ] Add new teams (update config, restart bot)
- [ ] Reset market if economy becomes unbalanced

## Troubleshooting Quick Reference

**Bot won't start:**
```bash
sudo journalctl -u gsc-bot -n 50
```

**Database locked:**
```bash
sudo systemctl restart gsc-bot
```

**Deployment failed:**
- Check GitHub Actions logs
- Verify SSH key permissions
- Test manual SSH: `ssh -i key user@host`

**Commands not working:**
- Verify bot token is correct
- Check command permissions
- Ensure guild ID is set
- Try resyncing: restart bot

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting.
