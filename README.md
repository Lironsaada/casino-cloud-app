# 🎰 Casino Cloud App

A modern, cloud-native Casino Web Application featuring **Blackjack**, **Roulette**, and **Slots**, rebuilt in Python and deployed using cutting-edge DevOps tools. This project showcases full DevOps lifecycle implementation, from infrastructure provisioning and CI/CD automation to container orchestration and real-time monitoring on Microsoft Azure.

---

## 🚀 Features

- 🃏 **Blackjack** – Supports split hands, double down, and emoji-based cards  
- 🎡 **Roulette** – Includes red/black/green wheel with spin animation  
- 🎰 **Slots** – Emoji reels with tiered payouts and randomized outcomes  
- 👤 **User Management** – Login system with persistent balance tracking  
- ☁️ **Cloud-Native Deployment** – Runs on Azure Kubernetes Service (AKS)  
- 🔄 **CI/CD Pipeline** – Automated build, test, and deploy workflow  
- 📊 **Monitoring & Observability** – Prometheus & Grafana dashboards  

---

## 🛠 Tech Stack

| Category             | Tool/Service                      |
|----------------------|-----------------------------------|
| Programming Language | Python (Flask)                    |
| Containerization     | Docker                            |
| Orchestration        | Kubernetes (AKS)                  |
| Infrastructure       | Terraform                         |
| CI/CD                | GitHub Actions / GitLab CI        |
| Monitoring           | Prometheus, Grafana               |
| Cloud Provider       | Microsoft Azure                   |

---

## 📁 Project Structure

```yaml
casino-cloud-app/
├── app/           → Python Flask app (web & logic)
├── docker/        → Dockerfiles and Docker config
├── infra/         → Terraform scripts & K8s manifests
├── cicd/          → CI/CD pipeline definitions
├── monitoring/    → Prometheus & Grafana setup
├── legacy/        → Original Bash version of the casino
└── README.md
```

---

## 🧱 Infrastructure (Planned)

- Azure Resource Group & Networking  
- Azure Kubernetes Service (AKS)  
- Azure Container Registry (ACR)  
- IAM & Secrets Management  
- Provisioned using **Terraform**  

---

## 🔄 CI/CD Workflow (Planned)

1. Code push triggers:
   - Linting & testing  
   - Docker build & push to ACR  
   - Kubernetes deployment  
2. Integrated via:
   - GitHub Actions or GitLab CI  
   - Kubernetes Rollouts  
   - Helm (optional)  

---

## 📈 Monitoring (Planned)

- Prometheus scrapes metrics from Flask app & K8s pods  
- Grafana dashboards include:
  - Pod CPU/memory usage  
  - Active users  
  - App request statistics  
  - Error rates  

---

## 📦 Quick Start (Local)

```bash
# Build and run locally
cd app/
docker build -t casino-app .
docker run -p 5000:5000 casino-app
```
