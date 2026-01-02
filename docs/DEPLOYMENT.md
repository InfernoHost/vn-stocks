# Deployment Guide

This guide covers deploying the GSC Discord bot to an Ubuntu server with automated deployment via GitHub Actions.

## Prerequisites

- Ubuntu 18.04+ server with SSH access
- Root or sudo access on the server
- GitHub repository set up
- Discord bot token

## Initial Server Setup

### 1. Run Setup Script

Copy the setup script to your server and run it:

```bash
# On your server
wget https://raw.githubusercontent.com/yourusername/vn-stocks/main/scripts/setup.sh
chmod +x setup.sh
sudo ./setup.sh
```

This script will:
- Install Python 3, pip, and git
- Create a service user (`gscbot`)
- Clone the repository to `/opt/gsc-bot`
- Set up a Python virtual environment
- Install dependencies
- Create a systemd service
- Generate `.env` template

### 2. Configure Environment Variables

Edit the `.env` file with your bot credentials:

```bash
sudo nano /opt/gsc-bot/.env
```

Add your values:
```env
DISCORD_TOKEN=your_actual_bot_token
GUILD_ID=your_server_id
ADMIN_ROLE_ID=your_admin_role_id
```

### 3. Start the Bot

```bash
# Start the bot service
sudo systemctl start gsc-bot

# Check status
sudo systemctl status gsc-bot

# View logs
sudo journalctl -u gsc-bot -f
```

### 4. Verify Bot is Running

The bot should now be online in your Discord server. Test with `/register` command.

## Automated Deployment Setup

### 1. Generate SSH Key for GitHub Actions

On your server, create a dedicated SSH key:

```bash
# Generate SSH key
ssh-keygen -t ed25519 -f ~/.ssh/github_actions -N ""

# Add public key to authorized_keys
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Display private key (you'll need this for GitHub)
cat ~/.ssh/github_actions
```

### 2. Configure GitHub Repository Secrets

In your GitHub repository, go to **Settings → Secrets and variables → Actions** and add:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `DEPLOY_HOST` | `your.server.ip` | Server hostname or IP address |
| `DEPLOY_USER` | `your-username` | SSH username (must have sudo access) |
| `DEPLOY_KEY` | `<private key>` | Contents of `~/.ssh/github_actions` |
| `DISCORD_TOKEN` | `<bot token>` | Your Discord bot token |
| `GUILD_ID` | `<server id>` | Your Discord server ID |
| `ADMIN_ROLE_ID` | `<role id>` | Your admin role ID |

### 3. Grant Sudo Access for Service Restart

The deployment user needs sudo access to restart the bot service:

```bash
# On your server
sudo visudo
```

Add this line (replace `your-username` with your SSH user):
```
your-username ALL=(ALL) NOPASSWD: /bin/systemctl restart gsc-bot, /bin/systemctl status gsc-bot, /bin/systemctl is-active gsc-bot, /usr/bin/journalctl -u gsc-bot *
```

### 4. Test Deployment

Push a commit to the `main` branch:

```bash
git add .
git commit -m "test: automated deployment"
git push origin main
```

GitHub Actions will automatically:
1. Connect to your server via SSH
2. Pull the latest code
3. Update dependencies
4. Update `.env` file
5. Restart the bot service
6. Verify the bot started successfully

Monitor the deployment in the **Actions** tab of your GitHub repository.

## Manual Deployment

If you need to deploy manually:

```bash
# On your server
cd /opt/gsc-bot
sudo -u gscbot ./scripts/deploy.sh
```

## Systemd Service Management

### Useful Commands

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

# Disable auto-start
sudo systemctl disable gsc-bot

# View logs (live)
sudo journalctl -u gsc-bot -f

# View last 100 log lines
sudo journalctl -u gsc-bot -n 100

# View logs from today
sudo journalctl -u gsc-bot --since today
```

## Troubleshooting

### Bot Won't Start

Check logs for errors:
```bash
sudo journalctl -u gsc-bot -n 50
```

Common issues:
- **Missing .env file**: Ensure `/opt/gsc-bot/.env` exists with correct values
- **Invalid token**: Verify `DISCORD_TOKEN` in `.env`
- **Permission errors**: Check file ownership: `sudo chown -R gscbot:gscbot /opt/gsc-bot`
- **Port conflicts**: Ensure no other process is using required resources

### Deployment Fails

1. **SSH connection issues**:
   - Verify SSH key is correct in GitHub secrets
   - Check server firewall allows SSH (port 22)
   - Test manual SSH: `ssh -i deploy_key user@host`

2. **Permission denied**:
   - Verify sudo permissions in `/etc/sudoers`
   - Check GitHub Actions user matches `DEPLOY_USER`

3. **Git pull fails**:
   - Ensure repository is accessible
   - Check file permissions in `/opt/gsc-bot`

### Database/Data Issues

```bash
# Backup database
cp /opt/gsc-bot/data/economy.db /opt/gsc-bot/data/economy.db.backup

# Backup market data
tar -czf /opt/gsc-bot/data/stocks-backup.tar.gz /opt/gsc-bot/data/stocks/

# Reset market (keep database)
sudo systemctl stop gsc-bot
cd /opt/gsc-bot
source venv/bin/activate
# Run admin reset command or manually delete stock JSONs
sudo systemctl start gsc-bot
```

## Updating Bot

### With GitHub Actions (Automatic)

Simply push to `main` branch:
```bash
git push origin main
```

### Manual Update

```bash
ssh user@your-server
cd /opt/gsc-bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart gsc-bot
```

## Monitoring

### Log Monitoring

Set up log rotation to prevent disk space issues:

```bash
sudo nano /etc/systemd/journald.conf
```

Set:
```ini
SystemMaxUse=1G
SystemMaxFileSize=100M
```

Then restart journald:
```bash
sudo systemctl restart systemd-journald
```

### Resource Monitoring

Check bot resource usage:
```bash
# CPU and memory usage
systemctl status gsc-bot

# Detailed resource usage
top -p $(pgrep -f "python.*bot.py")
```

## Security Best Practices

1. **Keep SSH keys secure**: Never commit private keys
2. **Use SSH key authentication**: Disable password authentication
3. **Firewall**: Only allow necessary ports (SSH, HTTPS)
4. **Regular updates**: Keep Ubuntu and Python packages updated
5. **Environment variables**: Never commit `.env` file
6. **Backup data**: Regularly backup database and market data

## Rollback

If a deployment breaks something:

```bash
# On server
cd /opt/gsc-bot
git log  # Find previous working commit
git reset --hard <commit-hash>
sudo systemctl restart gsc-bot
```

## Support

For deployment issues:
- Check GitHub Actions logs in the Actions tab
- Review server logs: `sudo journalctl -u gsc-bot -f`
- Open an issue with relevant logs and error messages
