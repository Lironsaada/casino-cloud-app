# 🧪 Testing Guide - Casino Cloud App

This document outlines how to test all components of the Casino Cloud App, including CI/CD pipelines, Terraform infrastructure, and application functionality.

## 📋 **Testing Overview**

Our testing strategy covers:
- **Unit Tests** - Application logic testing
- **Integration Tests** - End-to-end deployment testing  
- **Infrastructure Tests** - Terraform and Kubernetes validation
- **Security Tests** - Vulnerability scanning and compliance
- **Performance Tests** - Load testing and monitoring
- **CI/CD Tests** - Pipeline validation and deployment testing

---

## 🚀 **Quick Start Testing**

### **1. Run All Tests**
```bash
# Run comprehensive test suite
./scripts/test-integration.sh
```

### **2. Test CI/CD Pipeline**
```bash
# Test GitHub Actions pipeline locally
./scripts/test-cicd.sh
```

### **3. Test Infrastructure**
```bash
# Test Terraform and Kubernetes manifests
./scripts/test-terraform.sh
```

---

## 🧪 **Detailed Testing Instructions**

### **Application Testing**

#### **Unit Tests**
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run unit tests
python -m pytest tests/ --verbose --cov=app

# Generate coverage report
python -m pytest tests/ --cov=app --cov-report=html
```

#### **Security Testing**
```bash
# Install security tools
pip install bandit safety

# Run security scan
bandit -r app/ -f json -o bandit-report.json

# Check for vulnerable dependencies  
safety check --json --output safety-report.json
```

#### **Code Quality**
```bash
# Install linting tools
pip install flake8 black isort

# Run linting
flake8 app/ --max-line-length=127

# Format code
black app/
isort app/
```

### **Infrastructure Testing**

#### **Terraform Validation**
```bash
cd infra

# Format check
terraform fmt -check -recursive

# Validate configuration
terraform init -backend=false
terraform validate

# Security scan
tfsec . --format json --out tfsec-report.json

# Cost estimation
infracost breakdown --path . --format json
```

#### **Terraform Integration Tests**
```bash
cd infra/test

# Install Go dependencies
go mod tidy

# Run tests (requires Azure credentials)
go test -v -timeout 30m

# Run specific test
go test -v -run TestTerraformValidation
```

#### **Kubernetes Testing**
```bash
# Validate manifests
kubeval infra/k8s/*.yaml
kubeval infra/k8s/monitoring/*.yaml

# Lint manifests
kube-score score infra/k8s/*.yaml

# Dry run deployment
kubectl apply -f infra/k8s/ --dry-run=client
```

### **Container Testing**

#### **Docker Build Testing**
```bash
# Build image
docker build -t casino-app:test .

# Test image
docker run --rm -p 5000:5000 casino-app:test &
sleep 10
curl -f http://localhost:5000/metrics
```

#### **Security Scanning**
```bash
# Install Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Scan image
trivy image casino-app:test
```

### **CI/CD Testing**

#### **Local Pipeline Testing with Act**
```bash
# Install act
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Test specific job
act -j test

# Test full workflow
act push

# Test with secrets
act -s GITHUB_TOKEN=your_token
```

#### **Pipeline Validation**
```bash
# Validate workflow syntax
act --list

# Dry run
act --dry-run

# Test specific event
act pull_request
```

---

## 🔧 **Testing Tools Installation**

### **Required Tools**

#### **Python Tools**
```bash
pip install pytest pytest-cov bandit safety flake8 black isort
```

#### **Infrastructure Tools**
```bash
# Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# tfsec
curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash

# Infracost
curl -fsSL https://raw.githubusercontent.com/infracost/infracost/master/scripts/install.sh | sh
```

#### **Kubernetes Tools**
```bash
# kubeval
wget https://github.com/instrumenta/kubeval/releases/latest/download/kubeval-linux-amd64.tar.gz
tar xf kubeval-linux-amd64.tar.gz
sudo mv kubeval /usr/local/bin

# kube-score
wget https://github.com/zegl/kube-score/releases/latest/download/kube-score_linux_amd64
chmod +x kube-score_linux_amd64
sudo mv kube-score_linux_amd64 /usr/local/bin/kube-score
```

#### **Container Tools**
```bash
# Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
```

#### **CI/CD Tools**
```bash
# Act (GitHub Actions runner)
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

---

## 🎯 **Test Scenarios**

### **1. Development Testing**
```bash
# Before committing code
./scripts/test-cicd.sh
python -m pytest tests/
```

### **2. Pre-deployment Testing**
```bash
# Before deploying to production
./scripts/test-integration.sh
./scripts/test-terraform.sh
```

### **3. Security Testing**
```bash
# Regular security audits
bandit -r app/
safety check
trivy image casino-app:latest
tfsec infra/
```

### **4. Performance Testing**
```bash
# Load testing (requires running app)
for i in {1..100}; do
  curl -s http://localhost:5000/metrics > /dev/null
done
```

---

## 📊 **Test Reports**

### **Generated Reports**
- `bandit-report.json` - Security scan results
- `safety-report.json` - Dependency vulnerabilities
- `tfsec-report.json` - Infrastructure security issues
- `infracost-report.json` - Cost estimation
- `htmlcov/` - Code coverage reports

### **Interpreting Results**

#### **Security Reports**
- **High/Critical**: Must fix before deployment
- **Medium**: Should fix in next iteration
- **Low**: Nice to fix when time permits

#### **Coverage Reports**
- **Target**: >80% code coverage
- **Critical paths**: 100% coverage required

#### **Performance Metrics**
- **Response time**: <500ms for 95th percentile
- **Error rate**: <1% under normal load

---

## 🔄 **Continuous Testing**

### **Pre-commit Hooks**
```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### **Automated Testing**
- **GitHub Actions**: Runs on every push/PR
- **Scheduled scans**: Weekly security scans
- **Performance monitoring**: Continuous in production

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Docker Build Fails**
```bash
# Check Dockerfile syntax
docker build --no-cache -t casino-app:debug .

# Debug build process
docker build --progress=plain --no-cache .
```

#### **Terraform Tests Fail**
```bash
# Check Azure credentials
az account show

# Validate manually
terraform plan -var-file=test.tfvars
```

#### **Kubernetes Tests Fail**
```bash
# Check cluster connection
kubectl cluster-info

# Debug deployment
kubectl describe deployment casino-app
kubectl logs -l app=casino
```

---

## 📚 **Best Practices**

### **Testing Guidelines**
1. **Test Early**: Run tests before committing
2. **Test Often**: Automated testing on every change
3. **Test Everything**: Code, infrastructure, security
4. **Test Realistically**: Use production-like environments
5. **Test Continuously**: Monitor in production

### **Test Data Management**
- Use test-specific data
- Clean up after tests
- Don't use production data in tests
- Mock external dependencies

### **Security Testing**
- Scan regularly (weekly minimum)
- Fix critical issues immediately
- Track security metrics over time
- Test security controls

---

## 🎯 **Testing Checklist**

### **Before Each Release**
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Security scans clean
- [ ] Performance tests meet SLA
- [ ] Infrastructure tests pass
- [ ] Documentation updated

### **Production Deployment**
- [ ] Smoke tests pass
- [ ] Health checks working
- [ ] Monitoring alerts configured
- [ ] Rollback plan tested
- [ ] Security controls verified

---

## 📞 **Support**

For testing issues:
1. Check this documentation
2. Review test logs and reports
3. Run tests in verbose mode
4. Check tool versions and dependencies
5. Consult tool-specific documentation

**Remember**: Good testing prevents production issues! 🛡️ 