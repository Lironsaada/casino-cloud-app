# 🎰 Casino Cloud App - DevOps Infrastructure

*Production-ready casino application with enterprise-grade DevOps architecture*

**DevOps Engineering by Liron Saada** | Cloud-Native • Kubernetes • Infrastructure as Code

---

## 🏗️ Infrastructure Overview

This project demonstrates modern DevOps practices for deploying a scalable casino application on Azure cloud infrastructure using containerization, orchestration, and infrastructure as code.

### **Architecture Components**
- **🐳 Containerization**: Docker multi-stage builds
- **☸️ Orchestration**: Azure Kubernetes Service (AKS)
- **🏗️ Infrastructure**: Terraform (Azure Provider)
- **🔄 CI/CD**: GitHub Actions pipeline
- **📊 Monitoring**: Azure Log Analytics + Container Insights
- **🔐 Security**: Azure Container Registry, RBAC, Secrets Management

---

## 🛠 Technology Stack

### **Infrastructure Layer**
```yaml
Cloud Provider: Microsoft Azure
Compute: Azure Kubernetes Service (AKS)
Container Registry: Azure Container Registry (ACR)
Storage: Azure Managed Disks (Persistent Volumes)
Networking: Azure Load Balancer, Virtual Network
Monitoring: Azure Log Analytics, Container Insights
```

### **DevOps Toolchain**
```yaml
IaC: Terraform v1.5+
Orchestration: Kubernetes v1.27+
Containerization: Docker & Docker Compose
CI/CD: GitHub Actions
Configuration: Kubernetes ConfigMaps & Secrets
Scaling: Horizontal Pod Autoscaler (HPA)
```

### **Application Stack**
```yaml
Runtime: Python 3.11 (Flask microservice)
Frontend: Bootstrap 5, Vanilla JS
Data: JSON-based storage (transitioning to PostgreSQL)
Session: Redis-compatible (planned)
```

---

## 🚀 Infrastructure Deployment

### **Prerequisites**
- Azure CLI (`az`) authenticated
- Terraform v1.5+
- kubectl configured
- Docker Engine
- GitHub repository with Actions enabled

### **1. Infrastructure Provisioning**

```bash
# Clone repository
git clone https://github.com/lironsaada/casino-cloud-app.git
cd casino-cloud-app/infra

# Initialize Terraform
terraform init

# Review infrastructure plan
terraform plan -var="resource_group_name=casino-rg" \
               -var="location=East US" \
               -var="aks_cluster_name=casino-aks" \
               -var="acr_name=casinoacr$(date +%s)"

# Deploy infrastructure
terraform apply -auto-approve
```

### **2. Container Image Build & Push**

```bash
# Login to Azure Container Registry
az acr login --name <acr-name>

# Build and tag image
docker build -t <acr-name>.azurecr.io/casino-app:v1.0.0 .

# Push to registry
docker push <acr-name>.azurecr.io/casino-app:v1.0.0
```

### **3. Kubernetes Deployment**

```bash
# Get AKS credentials
az aks get-credentials --resource-group casino-rg --name casino-aks

# Deploy application manifests
kubectl apply -f infra/k8s/

# Verify deployment
kubectl get pods,svc,pvc -l app=casino

# Access application
kubectl port-forward svc/casino-service 8080:80
```

---

## 📊 Monitoring & Observability

### **Azure Monitor Integration**
```bash
# Enable Container Insights
az aks enable-addons --resource-group casino-rg \
                     --name casino-aks \
                     --addons monitoring

# View logs
az monitor log-analytics query \
  --workspace <workspace-id> \
  --analytics-query "ContainerLog | where Name contains 'casino'"
```

### **Kubernetes Metrics**
```bash
# Pod resource usage
kubectl top pods

# Node resource usage  
kubectl top nodes

# Horizontal Pod Autoscaler status
kubectl get hpa
```

---

## 🔄 CI/CD Pipeline

### **GitHub Actions Workflow** (`.github/workflows/deploy.yml`)

```yaml
name: Casino App CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'

  build:
    needs: security-scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to ACR
        uses: azure/docker-login@v1
        with:
          login-server: ${{ secrets.ACR_LOGIN_SERVER }}
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}
      
      - name: Build and push
        run: |
          IMAGE_TAG=${{ github.sha }}
          docker build -t ${{ secrets.ACR_LOGIN_SERVER }}/casino-app:${IMAGE_TAG} .
          docker push ${{ secrets.ACR_LOGIN_SERVER }}/casino-app:${IMAGE_TAG}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Get AKS credentials
        run: |
          az aks get-credentials --resource-group ${{ secrets.RESOURCE_GROUP }} \
                                --name ${{ secrets.AKS_CLUSTER_NAME }}
      
      - name: Deploy to AKS
        uses: azure/k8s-deploy@v1
        with:
          manifests: |
            infra/k8s/deployment.yaml
            infra/k8s/service.yaml
            infra/k8s/configmap.yaml
          images: |
            ${{ secrets.ACR_LOGIN_SERVER }}/casino-app:${{ github.sha }}
```

---

## 🔐 Security Implementation

### **Container Security**
- **Multi-stage Docker builds** for minimal attack surface
- **Non-root user** execution in containers
- **Vulnerability scanning** with Trivy in CI pipeline
- **Base image pinning** with digest verification

### **Kubernetes Security**
- **RBAC policies** for service account permissions
- **Network policies** for pod-to-pod communication
- **Pod Security Standards** enforcement
- **Secrets management** via Kubernetes secrets + Azure Key Vault

### **Infrastructure Security**
- **Private AKS cluster** with authorized IP ranges
- **Azure Container Registry** with admin user disabled
- **Managed identity** for AKS-to-ACR authentication
- **Terraform state** stored in encrypted Azure Storage

---

## 📈 Scaling & Performance

### **Horizontal Pod Autoscaler (HPA)**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: casino-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: casino-app
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### **Cluster Autoscaler**
```bash
# Enable cluster autoscaler
az aks update --resource-group casino-rg \
              --name casino-aks \
              --enable-cluster-autoscaler \
              --min-count 1 \
              --max-count 10
```

---

## 🗂 Infrastructure as Code

### **Terraform Modules Structure**
```
infra/
├── main.tf                 # Main infrastructure resources
├── variables.tf            # Input variables
├── outputs.tf             # Output values
├── provider.tf            # Azure provider configuration
├── terraform.tfvars.example
└── modules/
    ├── aks/               # AKS cluster module
    ├── acr/               # Container registry module
    └── monitoring/        # Log Analytics module
```

### **Key Resources Provisioned**
- **Resource Group**: Logical container for all resources
- **AKS Cluster**: Managed Kubernetes with system-assigned identity
- **Container Registry**: Private registry with admin access
- **Log Analytics**: Centralized logging and monitoring
- **Virtual Network**: Network isolation and security groups

---

## 🔧 Operational Tasks

### **Scaling Operations**
```bash
# Manual pod scaling
kubectl scale deployment casino-app --replicas=5

# Check autoscaler status
kubectl describe hpa casino-app-hpa

# Node pool scaling
az aks nodepool scale --resource-group casino-rg \
                      --cluster-name casino-aks \
                      --name agentpool \
                      --node-count 3
```

### **Troubleshooting**
```bash
# Pod logs
kubectl logs -f deployment/casino-app

# Pod shell access
kubectl exec -it <pod-name> -- /bin/bash

# Cluster events
kubectl get events --sort-by=.metadata.creationTimestamp

# Resource usage
kubectl describe node <node-name>
```

### **Backup & Recovery**
```bash
# Backup persistent volumes
kubectl get pvc
velero backup create casino-backup --include-namespaces default

# Restore from backup
velero restore create --from-backup casino-backup
```

---

## 📊 Cost Optimization

### **Resource Right-sizing**
- **Pod resource requests/limits** tuned for optimal allocation
- **Node instance types** selected based on workload characteristics
- **Spot instances** for development environments
- **Auto-shutdown** schedules for non-production clusters

### **Monitoring Costs**
```bash
# Azure cost analysis
az consumption usage list --billing-period-name <period>

# Resource utilization
kubectl top pods --containers
kubectl top nodes
```

---

## 🔄 GitOps Workflow

### **Branch Strategy**
```
main          ──────●──────●──────●
              ↗      ↗      ↗
develop   ────●──────●──────●
          ↗   ↗      ↗
feature   ●   ●      ●
```

### **Environment Promotion**
1. **Development**: Auto-deploy from `develop` branch
2. **Staging**: Manual promotion with integration tests
3. **Production**: Tagged releases with approval gates

---

## 🎯 DevOps Metrics

### **DORA Metrics Implementation**
- **Deployment Frequency**: GitHub Actions pipeline metrics
- **Lead Time**: PR creation to production deployment
- **MTTR**: Alert-to-resolution time via Azure Monitor
- **Change Failure Rate**: Rollback frequency tracking

### **SLO/SLI Targets**
- **Availability**: 99.9% uptime (43 minutes/month downtime)
- **Latency**: P95 < 500ms for game actions
- **Error Rate**: < 0.1% of requests result in 5xx errors
- **Throughput**: Support 1000+ concurrent users

---

## 🚨 Disaster Recovery

### **Backup Strategy**
- **Automated snapshots** of persistent volumes
- **Cross-region replication** of container images
- **Infrastructure state backup** via Terraform state management
- **Application data backup** to Azure Blob Storage

### **Recovery Procedures**
```bash
# Infrastructure recovery
terraform apply -auto-approve

# Application recovery
kubectl apply -f infra/k8s/

# Data recovery
velero restore create --from-backup <backup-name>
```

---

## 👨‍💻 DevOps Engineer: Liron Saada

### **Expertise Demonstrated**
- **☁️ Cloud Architecture**: Multi-service Azure infrastructure design
- **🐳 Containerization**: Docker best practices and optimization
- **☸️ Kubernetes**: Production workload orchestration
- **🏗️ Infrastructure as Code**: Terraform automation and modules
- **🔄 CI/CD**: GitHub Actions pipeline engineering
- **📊 Monitoring**: Observability and alerting implementation
- **🔐 Security**: Container and cluster security hardening

### **DevOps Practices Implemented**
- Infrastructure as Code (IaC)
- Continuous Integration/Continuous Deployment
- Container Security Scanning
- Automated Testing and Quality Gates
- Monitoring and Alerting
- Disaster Recovery Planning
- Cost Optimization

---

**© 2025 Casino Cloud App | DevOps Engineering by Liron Saada**

*Built with enterprise-grade DevOps practices for production scalability*
