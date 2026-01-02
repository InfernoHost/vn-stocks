#!/bin/bash
set -e

echo "=== GSC Bot Server Setup Script ==="
echo "This script will set up the bot on your Ubuntu server"

# Configuration
PROJECT_DIR="/opt/gsc-bot"
SERVICE_USER="gscbot"
REPO_URL="https://github.com/yourusername/vn-stocks.git"  # Update with your repo URL

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv git

# Create service user (if doesn't exist)
if ! id "$SERVICE_USER" &>/dev/null; then
    echo "Creating service user: $SERVICE_USER"
    useradd -r -m -d /home/$SERVICE_USER -s /bin/bash $SERVICE_USER
fi

# Create project directory
echo "Setting up project directory..."
mkdir -p "$PROJECT_DIR"

# Clone repository (if not already cloned)
if [ ! -d "$PROJECT_DIR/.git" ]; then
    echo "Cloning repository..."
    git clone "$REPO_URL" "$PROJECT_DIR"
else
    echo "Repository already cloned, pulling latest..."
    cd "$PROJECT_DIR"
    git pull origin main
fi

# Set ownership
chown -R $SERVICE_USER:$SERVICE_USER "$PROJECT_DIR"

# Create virtual environment
echo "Setting up Python virtual environment..."
cd "$PROJECT_DIR"
sudo -u $SERVICE_USER python3 -m venv venv
sudo -u $SERVICE_USER venv/bin/pip install --upgrade pip
sudo -u $SERVICE_USER venv/bin/pip install -r requirements.txt

# Create data directories
sudo -u $SERVICE_USER mkdir -p data/stocks data/graphs

# Create .env file if it doesn't exist
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "Creating .env file template..."
    sudo -u $SERVICE_USER cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo ""
    echo "⚠️  IMPORTANT: Edit $PROJECT_DIR/.env with your bot credentials!"
    echo ""
fi

# Install systemd service
echo "Installing systemd service..."
cat > /etc/systemd/system/gsc-bot.service << EOF
[Unit]
Description=GSC - Gearfall Stock Exchange Discord Bot
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/bot.py
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=gsc-bot

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Enable service (but don't start yet - needs .env configuration)
systemctl enable gsc-bot

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "1. Edit configuration: sudo nano $PROJECT_DIR/.env"
echo "2. Add your DISCORD_TOKEN, GUILD_ID, and ADMIN_ROLE_ID"
echo "3. Start the bot: sudo systemctl start gsc-bot"
echo "4. Check status: sudo systemctl status gsc-bot"
echo "5. View logs: sudo journalctl -u gsc-bot -f"
echo ""
echo "To enable automatic deployment:"
echo "1. Add SSH key for GitHub Actions in ~/.ssh/authorized_keys"
echo "2. Set up GitHub repository secrets (see DEPLOYMENT.md)"
echo "3. Push to main branch to trigger deployment"
echo ""
