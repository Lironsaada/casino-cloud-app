.PHONY: lint test image helm-lint helm-template helm-package helm-push dev-up argo-bootstrap

# Variables
IMAGE ?= your-dockerhub-username/your-app:latest
REGISTRY ?= docker.io
HELM_REPO ?= your-dockerhub-username/helm

# Optional placeholder for linting
lint:
	@echo "🧹 Linting code..."
	# Add your linting commands here (e.g., flake8, pylint)

# Run pytest with JUnit output
test:
	@echo "🧪 Running tests..."
	mkdir -p reports
	python3 -m pytest -q --junitxml=reports/junit-results.xml

# Build Docker image
image:
	@echo "🏗️ Building Docker image..."
	docker build -t $(IMAGE) .

# Helm lint
helm-lint:
	@echo "🔍 Linting Helm chart..."
	helm lint helm/app

# Helm template rendering
helm-template:
	@echo "📋 Rendering Helm template..."
	helm template test-render helm/app -f environments/dev/values.yaml

# Helm package
helm-package:
	@echo "📦 Packaging Helm chart..."
	mkdir -p dist/helm
	helm package helm/app -d dist/helm

# Helm push to OCI registry
helm-push:
	@echo "📤 Pushing Helm package to OCI registry..."
	export HELM_EXPERIMENTAL_OCI=1 && \
	helm push dist/helm/*.tgz oci://$(REGISTRY)/$(HELM_REPO)

dev-up:
	docker-compose up -d

argo-bootstrap:
	kubectl apply -f k8s/namespaces.yaml
	kubectl apply -f argocd/app-of-apps.yaml
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo update
	helm install mongodb bitnami/mongodb -n database -f k8s/mongo/helm-values.yaml
	helm install kube-prometheus prometheus-community/kube-prometheus-stack -n observability -f monitoring/kube-prometheus-values.yaml