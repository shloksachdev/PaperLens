#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status

echo "=========================================="
echo " Starting PaperLens EC2 Bootstrap Script  "
echo "=========================================="

# 1. Update and install dependencies
echo "[1/6] Installing system dependencies..."
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib curl git libcairo2-dev -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 2. Database Setup
echo "[2/6] Setting up PostgreSQL Database..."
# Run postgres commands safely (ignore errors if DB/User already exists)
sudo -u postgres psql -c "CREATE DATABASE paperlens;" || true
sudo -u postgres psql -c "CREATE USER paperlensuser WITH PASSWORD 'paperlens_secure_pass';" || true
sudo -u postgres psql -c "ALTER ROLE paperlensuser SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE paperlensuser SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE paperlensuser SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE paperlens TO paperlensuser;" || true

# 3. Setup Backend
echo "[3/6] Configuring FastAPI Backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn uvicorn "psycopg[binary]"

# Create backend .env if it doesn't exist
if [ ! -f .env ]; then
    echo "DATABASE_URL=postgresql+psycopg://paperlensuser:paperlens_secure_pass@localhost/paperlens" > .env
    echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
    echo "GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID" >> .env
    echo "HUGGINGFACEHUB_API_TOKEN=YOUR_HF_TOKEN" >> .env
    echo "! .env file generated cleanly! (Make sure to update API keys)"
fi
cd ..

# 4. Setup Frontend
echo "[4/6] Building React Frontend..."
cd frontend
if [ ! -f .env ]; then
    echo "VITE_GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID" > .env
fi
npm install
npm run build
cd ..

# 5. Systemd Service
echo "[5/6] Creating Systemd Service..."
cat <<EOF | sudo tee /etc/systemd/system/paperlens-backend.service
[Unit]
Description=Gunicorn daemon for PaperLens FastAPI
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$(pwd)/backend
Environment="PATH=$(pwd)/backend/venv/bin"
ExecStart=$(pwd)/backend/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 127.0.0.1:8000 main:app

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start paperlens-backend
sudo systemctl enable paperlens-backend

# 6. Nginx Setup
echo "[6/6] Configuring Nginx..."
cat <<EOF | sudo tee /etc/nginx/sites-available/paperlens
server {
    listen 80;
    server_name _; 

    location / {
        root $(pwd)/frontend/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # Proxy API calls
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_addrs;
    }
}
EOF

# Enable Nginx Site
sudo ln -sf /etc/nginx/sites-available/paperlens /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

echo "=========================================="
echo " Deployment Engine Execution Complete!    "
echo " Note: Please strictly edit backend/.env  "
echo " to inject your accurate HuggingFace &   "
echo " Google API keys. Then restart the app:  "
echo " sudo systemctl restart paperlens-backend "
echo "=========================================="
