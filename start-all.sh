#!/bin/bash

echo "🎰 Casino Cloud App - Full Stack Startup"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if .env exists and set it up
if [ ! -f .env ]; then
    print_info "Creating .env file from template..."
    cp env.example .env
    
    print_info "Generating SECRET_KEY..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/your-generated-secret-key-here-use-python-secrets-token-hex-32/$SECRET_KEY/" .env
    
    print_info "Setting default passwords..."
    sed -i "s/your-secure-admin-password/admin123/" .env
    sed -i "s/your-grafana-admin-password/admin123/" .env
    
    print_status "Environment configured with default passwords!"
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not available in PATH"
    echo "Please install Docker Desktop and enable WSL2 integration"
    exit 1
fi

# Check if Python dependencies are installed
if [ ! -d "venv" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv venv
fi

print_info "Installing/updating Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

# Stop any existing containers
print_info "Stopping any existing monitoring containers..."
docker compose down > /dev/null 2>&1

# Start monitoring stack (Grafana + Prometheus)
print_info "Starting monitoring stack (Grafana + Prometheus)..."
if docker compose up -d; then
    print_status "Monitoring containers started successfully!"
else
    print_error "Failed to start monitoring containers"
    exit 1
fi

# Wait for containers to be ready
print_info "Waiting for containers to be ready..."
sleep 5

# Check if containers are running
if docker ps --filter "name=casino-prometheus" --filter "status=running" | grep -q casino-prometheus && \
   docker ps --filter "name=casino-grafana" --filter "status=running" | grep -q casino-grafana; then
    print_status "All monitoring containers are running!"
else
    print_warning "Some containers may not be ready yet..."
fi

# Function to start Flask app
start_flask() {
    print_info "Starting Flask casino application..."
    source venv/bin/activate
    python3 -m app.app
}

# Display access information
echo ""
echo "🚀 All services starting up!"
echo "============================="
echo ""
echo -e "${GREEN}📱 Access Points:${NC}"
echo "🎰 Casino App:      http://localhost:5000"
echo "   - Username: Create any username"
echo "   - Starting balance: 1000 coins"
echo ""
echo "🔐 Admin Panel:     http://localhost:5000/admin_auth"
echo "   - Password: admin123"
echo ""
echo "📊 Grafana:         http://localhost:3000"
echo "   - Username: admin"
echo "   - Password: admin123"
echo ""
echo "📈 Prometheus:      http://localhost:9090"
echo "   - No authentication required"
echo ""
echo "🔍 App Metrics:     http://localhost:5000/metrics"
echo "   - JSON metrics endpoint"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo "• Play some games to generate metrics data"
echo "• Check Grafana dashboards for real-time analytics"
echo "• Use Ctrl+C to stop the Flask app"
echo "• Run 'docker compose down' to stop monitoring"
echo ""
echo -e "${BLUE}🎮 Starting Flask application...${NC}"
echo "=================================="
echo ""

# Start Flask app (this will block until Ctrl+C)
start_flask 