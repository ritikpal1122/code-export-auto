# Test Automation Dashboard

A web-based dashboard for automating test code generation and monitoring.

## Prerequisites

- Python 3.9 or higher
- Docker (optional, for containerized deployment)
- Git

## Project Structure

```
.
├── app.py              # Flask application
├── test_automation.py  # Automation script
├── index.html         # Frontend interface
├── styles.css         # Frontend styles
├── requirements.txt   # Python dependencies
├── gunicorn_config.py # Gunicorn configuration
└── Dockerfile         # Docker configuration
```

## Local Development Setup

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
python app.py
```

4. Access the application at: http://localhost:5000

## Production Deployment

### Option 1: Direct Server Deployment

1. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nginx
```

2. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

3. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Configure Nginx:
```bash
sudo nano /etc/nginx/sites-available/test-automation
```

Add the following configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

6. Enable the Nginx site:
```bash
sudo ln -s /etc/nginx/sites-available/test-automation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

7. Run the application with Gunicorn:
```bash
gunicorn --config gunicorn_config.py app:app
```

### Option 2: Docker Deployment

1. Build the Docker image:
```bash
docker build -t test-automation-app .
```

2. Run the container:
```bash
docker run -d -p 8000:8000 test-automation-app
```

### Option 3: Heroku Deployment

1. Install Heroku CLI:
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

2. Login to Heroku:
```bash
heroku login
```

3. Create a new Heroku app:
```bash
heroku create your-app-name
```

4. Deploy to Heroku:
```bash
git push heroku main
```

## Environment Variables

Create a `.env` file with the following variables:
```
FLASK_ENV=production
AUTH_TOKEN=your_auth_token
```

## Security Considerations

1. Always use HTTPS in production
2. Keep your auth token secure
3. Implement rate limiting
4. Regular security updates

## Monitoring

The application logs are available in:
- Access logs: stdout
- Error logs: stderr
- Application logs: app.log

## Troubleshooting

1. Check application logs:
```bash
tail -f app.log
```

2. Check Nginx logs:
```bash
sudo tail -f /var/log/nginx/error.log
```

3. Check system status:
```bash
sudo systemctl status nginx
```

## Support

For issues and feature requests, please open an issue in the repository. 