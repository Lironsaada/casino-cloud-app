#!/bin/bash

set -euo pipefail

# Jenkins Helm Deployment Script
echo "🚀 Deploying Jenkins with Helm"

# Configuration
NAMESPACE="jenkins"
RELEASE_NAME="casino-jenkins"
CHART_PATH="helm/jenkins"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Create namespace if it doesn't exist
echo_info "Creating namespace: $NAMESPACE"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Install/upgrade Jenkins
echo_info "Deploying Jenkins"

if helm list -n $NAMESPACE | grep -q $RELEASE_NAME; then
    echo_info "Upgrading existing Jenkins release"
    helm upgrade $RELEASE_NAME $CHART_PATH \
        --namespace $NAMESPACE \
        --wait \
        --timeout 300s
else
    echo_info "Installing new Jenkins release"
    helm install $RELEASE_NAME $CHART_PATH \
        --namespace $NAMESPACE \
        --wait \
        --timeout 300s \
        --create-namespace
fi

echo_success "Jenkins deployment completed!"

# Get service information
echo_info "Getting service information..."
kubectl get services -n $NAMESPACE

echo_success "Jenkins is now available!"
echo ""
echo "📋 Access Information:"
echo "   Namespace: $NAMESPACE"
echo "   Release: $RELEASE_NAME"
echo ""
echo "🔐 Login Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "🌐 Access Methods:"
echo "   NodePort: http://localhost:30081"
echo "   Port-forward: kubectl port-forward -n $NAMESPACE svc/casino-jenkins 8080:8080"

echo ""
echo "🔧 Useful Commands:"
echo "   View pods: kubectl get pods -n $NAMESPACE"
echo "   View logs: kubectl logs -n $NAMESPACE deployment/casino-jenkins"
echo "   Delete: helm uninstall $RELEASE_NAME -n $NAMESPACE"

echo ""
echo_success "Jenkins deployment script completed! 🎉"