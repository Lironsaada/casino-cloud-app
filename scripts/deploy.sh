#!/bin/bash

set -e

echo "🚀 Casino Cloud App Deployment Script"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if we're connected to a cluster
if ! kubectl cluster-info &> /dev/null; then
    print_error "Not connected to a Kubernetes cluster"
    exit 1
fi

print_status "Connected to cluster: $(kubectl config current-context)"

# Deploy application
print_status "Deploying Casino Cloud App..."

# Create namespace if it doesn't exist
kubectl create namespace casino --dry-run=client -o yaml | kubectl apply -f -

# Apply Kubernetes manifests
print_status "Applying Kubernetes manifests..."
kubectl apply -f infra/k8s/

# Deploy monitoring stack
print_status "Deploying monitoring stack..."
kubectl apply -f infra/k8s/monitoring/

# Wait for deployments to be ready
print_status "Waiting for deployments to be ready..."
kubectl wait --for=condition=available deployment/casino-app --timeout=300s
kubectl wait --for=condition=available deployment/prometheus -n monitoring --timeout=300s
kubectl wait --for=condition=available deployment/grafana -n monitoring --timeout=300s

# Get service information
print_status "Deployment completed successfully!"
echo ""
echo "📊 Service Information:"
echo "======================"
kubectl get services
echo ""
kubectl get services -n monitoring

echo ""
print_status "Access your application:"
echo "• Casino App: kubectl port-forward svc/casino-service 8080:80"
echo "• Prometheus: kubectl port-forward -n monitoring svc/prometheus-service 9090:9090"
echo "• Grafana: kubectl port-forward -n monitoring svc/grafana-service 3000:3000"
echo ""
print_status "Grafana credentials: admin / casino123" 