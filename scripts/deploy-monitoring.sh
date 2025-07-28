#!/bin/bash

echo "🚀 Deploying Casino App Monitoring Stack"

# Create monitoring namespace
echo "📋 Creating monitoring namespace..."
kubectl apply -f infra/k8s/monitoring/namespace.yaml

# Deploy Prometheus
echo "📊 Deploying Prometheus..."
kubectl apply -f infra/k8s/monitoring/prometheus-config.yaml
kubectl apply -f infra/k8s/monitoring/prometheus-deployment.yaml

# Deploy Grafana  
echo "📈 Deploying Grafana..."
kubectl apply -f infra/k8s/monitoring/grafana-deployment.yaml

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available deployment/prometheus -n monitoring --timeout=300s
kubectl wait --for=condition=available deployment/grafana -n monitoring --timeout=300s

echo "✅ Monitoring stack deployed successfully!"
echo ""
echo "🔍 Access Instructions:"
echo "1. Prometheus UI:"
echo "   kubectl port-forward -n monitoring svc/prometheus-service 9090:9090"
echo "   Then visit: http://localhost:9090"
echo ""
echo "2. Grafana UI:"
echo "   kubectl port-forward -n monitoring svc/grafana-service 3000:3000"
echo "   Then visit: http://localhost:3000"
echo "   Login: admin / casino123"
echo ""
echo "3. Check monitoring status:"
echo "   kubectl get pods -n monitoring" 