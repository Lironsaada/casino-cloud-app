# 🎰 Casino Cloud App - DevOps Infrastructure

*Production-ready casino application with enterprise-grade DevOps architecture*

**DevOps Engineering by Liron Saada** | Cloud-Native • Kubernetes • Infrastructure as Code

---

## 🎮 Application Features

- 🃏 **Blackjack** – Advanced gameplay with split hands, double down, and realistic card animations
- 🎡 **Roulette** – Interactive wheel with red/black/green betting and smooth spin animations  
- 🎰 **Slots** – Multi-reel slot machine with tiered payouts and visual effects
- 👤 **User Management** – Secure authentication with persistent balance tracking
- 🛡️ **Admin Panel** – Administrative controls with protected access
- 💰 **Transaction Logging** – Complete audit trail of all gaming activities

---

## 🏗️ Infrastructure Overview

This project demonstrates modern DevOps practices for deploying a scalable casino application on Azure cloud infrastructure using containerization, orchestration, and infrastructure as code.

### **Architecture Components**
- **🐳 Containerization**: Docker multi-stage builds with security scanning
- **☸️ Orchestration**: Azure Kubernetes Service (AKS) with auto-scaling
- **🏗️ Infrastructure**: Terraform for Azure resource provisioning
- **🔄 CI/CD**: GitHub Actions pipeline with automated testing and deployment
- **📊 Monitoring**: Prometheus metrics collection + Grafana dashboards
- **🔐 Security**: Azure Container Registry, RBAC, secrets management

---

## 🛠 Technology Stack

| Category             | Technology                        | Purpose                           |
|----------------------|-----------------------------------|-----------------------------------|
| **Application**      | Python Flask                      | Web framework and game logic     |
| **Frontend**         | HTML5, CSS3, JavaScript          | Interactive gaming interface     |
| **Containerization** | Docker                            | Application packaging             |
| **Orchestration**    | Kubernetes (AKS)                  | Container management & scaling    |
| **Infrastructure**   | Terraform (Azure Provider)       | Infrastructure as Code            |
| **CI/CD**            | GitHub Actions                    | Automated build and deployment    |
| **Monitoring**       | Prometheus + Grafana              | Metrics collection & visualization|
| **Cloud Platform**   | Microsoft Azure                   | Cloud infrastructure provider     |
| **Registry**         | Azure Container Registry (ACR)   | Container image storage           |
| **Database**         | JSON Files (SQLite for prod)     | Data persistence                  |

---

## 📁 Project Structure

```yaml
casino-cloud-app/
├── app/                          # 🎮 Flask application
│   ├── app.py                    # Main application with Prometheus metrics
│   ├── templates/                # HTML templates with modern UI
│   └── static/                   # CSS, JS, and assets
├── infra/                        # 🏗️ Infrastructure as Code
│   ├── terraform/                # Azure resource provisioning
│   │   ├── main.tf              # Main Terraform configuration
│   │   ├── variables.tf         # Input variables
│   │   └── outputs.tf           # Output values
│   └── k8s/                     # Kubernetes manifests
│       ├── deployment.yaml      # App deployment with metrics annotations
│       ├── service.yaml         # Load balancer service
│       └── monitoring/          # Monitoring stack
│           ├── namespace.yaml   # Monitoring namespace
│           ├── prometheus-*.yaml # Prometheus setup with alerts
│           └── grafana-*.yaml   # Grafana with pre-configured dashboards
├── monitoring/                   # 📊 Local monitoring setup
│   ├── docker-compose.yml       # Local Prometheus + Grafana
│   ├── prometheus.yml           # Prometheus configuration
│   └── grafana/                 # Grafana datasources and dashboards
├── scripts/                      # 🔧 Deployment automation
│   └── deploy-monitoring.sh     # Kubernetes monitoring deployment
├── Dockerfile                    # 🐳 Container image definition
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 📊 Monitoring & Observability

### **Metrics Collection**
The application exposes Prometheus metrics at `/metrics` endpoint:

- **📈 Request Metrics**: Total requests, response times, status codes
- **👥 User Metrics**: Active users, authentication events
- **🎮 Gaming Metrics**: Games played by type, win/loss ratios
- **💰 Financial Metrics**: User balances, transaction volumes
- **🔧 System Metrics**: CPU, memory, and Kubernetes pod health

### **Dashboard Features**
- **🎯 Real-time Gaming Analytics**: Live player activity and game statistics
- **📊 Performance Monitoring**: Application response times and error rates
- **👤 User Behavior**: Login patterns and user engagement metrics
- **💡 Business Intelligence**: Revenue tracking and game popularity

---

## ⚡ Quick Start (For New Users)

### **One-Command Setup**

```bash
# Clone and start the entire application
git clone https://github.com/Lironsaada/casino-cloud-app.git
cd casino-cloud-app
chmod +x quick-start.sh
./quick-start.sh
```

**What this does:**
1. ✅ Generates secure `SECRET_KEY` automatically
2. ✅ Creates `.env` file from template
3. ✅ Installs all Python dependencies
4. ✅ Starts Docker containers (Grafana + Prometheus)
5. ✅ Launches the Flask casino application

**Access Points:**
- 🎰 **Casino App**: http://localhost:5000
- 📊 **Grafana Dashboard**: http://localhost:3000 (admin / your-password)
- 📈 **Prometheus Metrics**: http://localhost:9090

---

## 🚀 Deployment Instructions

### **Prerequisites**
- Docker Desktop or Docker Engine
- kubectl configured for your cluster
- Azure CLI (for cloud deployment)
- Terraform (for infrastructure provisioning)

### **1. 🐳 Local Development Setup**

```bash
# Clone the repository
git clone https://github.com/Lironsaada/casino-cloud-app.git
cd casino-cloud-app

# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the application locally
python3 -m app.app
# App available at: http://localhost:5000
```

### **2. 📊 Local Monitoring Stack**

Deploy Prometheus and Grafana locally using Docker Compose:

```bash
# Start monitoring stack
docker-compose up -d

# Access the services
# Grafana:    http://localhost:3000 (admin/[see SECURITY.md for password setup])
# Prometheus: http://localhost:9090
# App:        http://localhost:5000
```

**Grafana Dashboard Access:**
1. Open http://localhost:3000
2. Login: `admin` / `[set GRAFANA_ADMIN_PASSWORD environment variable]`
3. Navigate to "Casino Cloud App - Monitoring Dashboard"
4. Play some games to see real-time metrics!

### **3. ☸️ Kubernetes Deployment**

#### **Deploy Application**
```bash
# Apply Kubernetes manifests
kubectl apply -f infra/k8s/

# Verify deployment
kubectl get pods
kubectl get services

# Get application URL
kubectl get service casino-service
```

#### **Deploy Monitoring Stack**
```bash
# Automated deployment
./scripts/deploy-monitoring.sh

# Manual deployment
kubectl apply -f infra/k8s/monitoring/

# Verify monitoring pods
kubectl get pods -n monitoring

# Access Grafana via port-forward
kubectl port-forward -n monitoring svc/grafana-service 3000:3000
# Open: http://localhost:3000 (admin/[set GRAFANA_ADMIN_PASSWORD env var])

# Access Prometheus via port-forward
kubectl port-forward -n monitoring svc/prometheus-service 9090:9090
# Open: http://localhost:9090
```

### **4. 🏗️ Azure Cloud Deployment**

#### **Infrastructure Provisioning**
```bash
# Initialize Terraform
cd infra/terraform
terraform init

# Plan infrastructure changes
terraform plan -var="environment=prod"

# Deploy Azure resources
terraform apply

# Get AKS credentials
az aks get-credentials --resource-group casino-rg --name casino-aks
```

#### **Application Deployment**
```bash
# Build and push Docker image
docker build -t lironsaada/casino-app:latest .
docker push lironsaada/casino-app:latest

# Deploy to AKS
kubectl apply -f infra/k8s/
kubectl apply -f infra/k8s/monitoring/

# Get public IP
kubectl get service casino-service
```

---

## 🔄 CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/deploy.yml`) provides:

### **Automated Testing**
- Code linting with flake8
- Security scanning with bandit
- Dependency vulnerability checks
- Unit test execution

### **Container Build**
- Multi-stage Docker builds for optimization
- Image security scanning
- Automated tagging with commit SHA
- Push to Azure Container Registry

### **Deployment Automation**
- Automated deployment to AKS
- Rolling updates with zero downtime
- Health checks and rollback capabilities
- Slack/Teams notifications

### **Monitoring Integration**
- Automatic dashboard updates
- Alert rule deployment
- Metrics validation
- Performance regression detection

---

## 📈 Monitoring Dashboards

### **Casino Cloud App Dashboard**
- **🎯 Total Requests**: HTTP request volume and patterns
- **👥 Active Users**: Real-time user count and activity
- **🎮 Games by Type**: Blackjack, Roulette, Slots popularity
- **🏆 Win/Loss Ratios**: Gaming outcome analytics
- **⚡ Performance**: Response times and error rates

### **Infrastructure Monitoring**
- **☸️ Kubernetes Metrics**: Pod CPU, memory, restart counts
- **🔧 Node Health**: Cluster resource utilization
- **📦 Container Metrics**: Image pulls, registry health
- **🌐 Network**: Service mesh and ingress metrics

### **Alerting Rules**
- **🚨 Application Down**: Casino app unavailable > 1 minute
- **⚠️ High Response Time**: 95th percentile > 1 second
- **🔴 Error Rate**: 5xx errors > 10% over 5 minutes
- **💾 Resource Usage**: CPU/Memory > 80% sustained

---

## 🔧 Operational Tasks

### **Scaling**
```bash
# Scale application pods
kubectl scale deployment casino-app --replicas=5

# Enable horizontal pod autoscaling
kubectl autoscale deployment casino-app --cpu-percent=70 --min=2 --max=10
```

### **Updates**
```bash
# Rolling update
kubectl set image deployment/casino-app casino=lironsaada/casino-app:v2.0.0

# Check rollout status
kubectl rollout status deployment/casino-app

# Rollback if needed
kubectl rollout undo deployment/casino-app
```

### **Monitoring**
```bash
# Check application logs
kubectl logs -f deployment/casino-app

# View metrics
curl http://localhost:5000/metrics

# Access monitoring
kubectl port-forward -n monitoring svc/grafana-service 3000:3000
```

---

## 🔐 Security Considerations

- **🛡️ Container Security**: Non-root user, minimal base images
- **🔒 Secrets Management**: Kubernetes secrets for sensitive data
- **🔐 RBAC**: Role-based access control for monitoring stack
- **📋 Security Scanning**: Automated vulnerability assessment
- **🌐 Network Policies**: Restricted pod-to-pod communication
- **📊 Audit Logging**: Complete audit trail of all activities

---

## 💰 Cost Optimization

- **📊 Resource Requests/Limits**: Efficient resource allocation
- **⚡ Horizontal Pod Autoscaling**: Scale based on demand
- **🌙 Cluster Autoscaling**: Automatic node scaling
- **📈 Monitoring Costs**: Azure cost analysis integration
- **🔄 Lifecycle Policies**: Automated cleanup of old images

---

## 📚 DevOps Best Practices Demonstrated

### **🔄 GitOps Workflow**
- Infrastructure as Code with Terraform
- Declarative Kubernetes manifests
- Git-based deployment workflows
- Automated rollback capabilities

### **📊 DORA Metrics**
- **Deployment Frequency**: Automated daily deployments
- **Lead Time**: < 30 minutes from commit to production
- **MTTR**: < 15 minutes with automated rollback
- **Change Failure Rate**: < 5% with comprehensive testing

### **🏗️ Infrastructure Patterns**
- Immutable infrastructure
- Blue-green deployments
- Circuit breaker patterns
- Health check endpoints

---

## 🚨 Disaster Recovery

### **Backup Strategy**
- **Application Data**: Automated daily backups to Azure Blob Storage
- **Configuration**: GitOps ensures all configs are in version control
- **Monitoring**: Alert history and dashboard backup

### **Recovery Procedures**
- **RTO**: < 30 minutes for complete environment restoration
- **RPO**: < 1 hour for data recovery
- **Cross-region**: Multi-region deployment capability
- **Testing**: Monthly disaster recovery drills

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Liron Saada** - DevOps Engineer  
*Specializing in Cloud-Native Architecture and Infrastructure Automation*

---

## 🎯 Learning Outcomes

This project demonstrates:
- **☁️ Cloud-Native Development**: Building applications for Kubernetes
- **🔄 CI/CD Mastery**: Complete automation from code to production
- **📊 Observability**: Comprehensive monitoring and alerting
- **🏗️ Infrastructure as Code**: Terraform for cloud resources
- **🔐 Security**: Best practices for container and cluster security
- **📈 Scalability**: Horizontal scaling and performance optimization

---

*Built with ❤️ using modern DevOps practices and cloud-native technologies*
