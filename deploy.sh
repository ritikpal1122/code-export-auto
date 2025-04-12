#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="test-automation"
APP_DIR="/opt/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
USER="test-automation"
GROUP="test-automation"

# Create user and group if they don't exist
if ! id "$USER" &>/dev/null; then
    useradd -r -s /bin/false "$USER"
fi

# Create application directory
mkdir -p "$APP_DIR"
chown -R "$USER:$GROUP" "$APP_DIR"

# Install system dependencies
apt-get update
apt-get install -y python3-pip python3-venv nginx

# Create and activate virtual environment
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Install Python dependencies
pip install -r requirements.txt
pip install gunicorn

# Copy application files
cp -r . "$APP_DIR/"
chown -R "$USER:$GROUP" "$APP_DIR"

# Create log directory
mkdir -p "/var/log/$APP_NAME"
chown -R "$USER:$GROUP" "/var/log/$APP_NAME"

# Configure Nginx
cp nginx.conf /etc/nginx/nginx.conf
nginx -t
systemctl restart nginx

# Configure systemd service
cp test-automation.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable test-automation
systemctl start test-automation

# Set up SSL (uncomment and configure when ready)
# apt-get install -y certbot python3-certbot-nginx
# certbot --nginx -d your-domain.com

echo "Deployment completed successfully!"
echo "Application is running at http://your-domain.com"
echo "To check the status: systemctl status test-automation"
echo "To view logs: journalctl -u test-automation" 