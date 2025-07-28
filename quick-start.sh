#!/bin/bash

echo "🎰 Casino Cloud App - Quick Start Setup"
echo "======================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    
    echo "🔑 Generating SECRET_KEY..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/your-generated-secret-key-here-use-python-secrets-token-hex-32/$SECRET_KEY/" .env
    
    echo "⚠️  Please edit .env and set your passwords:"
    echo "   - ADMIN_PASSWORD (for admin panel access)"
    echo "   - GRAFANA_ADMIN_PASSWORD (for Grafana dashboard)"
    echo ""
    echo "   nano .env"
    echo ""
    read -p "Press Enter after you've set your passwords..."
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

echo "🐳 Starting monitoring stack (Grafana + Prometheus)..."
docker compose up -d

echo "🚀 Starting Flask application..."
echo "   App: http://localhost:5000"
echo "   Grafana: http://localhost:3000 (admin / your-grafana-password)"
echo "   Prometheus: http://localhost:9090"
echo ""

# Start the Flask app
python3 -m app.app 