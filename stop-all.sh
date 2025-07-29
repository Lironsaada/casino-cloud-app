#!/bin/bash

echo "🛑 Casino Cloud App - Stop All Services"
echo "======================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Stop Flask app (if running in background)
print_info "Stopping Flask application..."
pkill -f "python3 -m app.app" > /dev/null 2>&1

# Stop monitoring containers
print_info "Stopping monitoring containers (Grafana + Prometheus)..."
if docker compose down; then
    print_status "All containers stopped successfully!"
else
    echo "Some containers may have already been stopped."
fi

# Optional: Remove volumes (uncomment if you want to clear all data)
# echo ""
# read -p "Do you want to remove all monitoring data? (y/N): " -n 1 -r
# echo ""
# if [[ $REPLY =~ ^[Yy]$ ]]; then
#     print_info "Removing monitoring data volumes..."
#     docker compose down -v
#     print_status "All data cleared!"
# fi

echo ""
print_status "All services stopped!"
echo ""
echo "📋 What was stopped:"
echo "• Flask casino application"
echo "• Grafana monitoring (port 3000)"
echo "• Prometheus metrics (port 9090)"
echo ""
echo "🔄 To start again, run: ./start-all.sh" 