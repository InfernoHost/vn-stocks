#!/bin/bash
set -e

PROJECT_DIR="/opt/gsc-bot"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="gsc-bot"

echo "=== GSC Bot Deployment Script ==="
echo "Deploying to: $PROJECT_DIR"

# Navigate to project directory
cd "$PROJECT_DIR"

# Pull latest changes
echo "Pulling latest changes from git..."
git pull origin main

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install/update dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create data directories if they don't exist
echo "Setting up data directories..."
mkdir -p data/stocks data/graphs

# Fix permissions on data directory
echo "Setting permissions..."
chmod -R 755 data/
chown -R $(whoami):$(whoami) data/

# Check if .env file exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please create .env file with required configuration."
    exit 1
fi

# Restart bot service
echo "Restarting bot service..."
sudo systemctl restart "$SERVICE_NAME"

# Check status
echo "Checking bot status..."
sleep 2
sudo systemctl status "$SERVICE_NAME" --no-pager

echo "=== Deployment Complete ==="
echo "Bot logs: sudo journalctl -u $SERVICE_NAME -f"
