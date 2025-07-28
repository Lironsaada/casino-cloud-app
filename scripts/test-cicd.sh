#!/bin/bash

set -e

echo "🧪 Testing CI/CD Pipeline Locally"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if act is installed
if ! command -v act &> /dev/null; then
    print_warning "act is not installed. Installing..."
    
    # Install act based on OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install act
    else
        print_error "Please install act manually: https://github.com/nektos/act"
        exit 1
    fi
fi

# Test 1: Lint and Security Checks
print_step "1. Testing lint and security checks..."
act -j test --dry-run

# Test 2: Build Process
print_step "2. Testing Docker build process..."
docker build -t casino-app-test . || {
    print_error "Docker build failed"
    exit 1
}

print_status "Docker build successful"

# Test 3: Security Scan
print_step "3. Running security scans..."

# Install security tools if not present
pip install bandit safety flake8 || true

# Run flake8 linting
print_status "Running flake8 linting..."
flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics || {
    print_warning "Linting issues found"
}

# Run bandit security scan
print_status "Running bandit security scan..."
bandit -r app/ -f json -o bandit-report.json || {
    print_warning "Security issues found, check bandit-report.json"
}

# Run safety check
print_status "Running dependency vulnerability check..."
safety check --json --output safety-report.json || {
    print_warning "Vulnerable dependencies found, check safety-report.json"
}

# Test 4: Application Tests
print_step "4. Running application tests..."
if [ -f "tests/test_app.py" ]; then
    python -m pytest tests/ --verbose || {
        print_error "Tests failed"
        exit 1
    }
    print_status "All tests passed"
else
    print_warning "No tests found"
fi

# Test 5: Container Security Scan
print_step "5. Running container security scan..."
if command -v trivy &> /dev/null; then
    trivy image casino-app-test || {
        print_warning "Container vulnerabilities found"
    }
else
    print_warning "Trivy not installed, skipping container scan"
fi

# Test 6: Simulate full pipeline
print_step "6. Simulating full CI/CD pipeline..."
if [ -f ".github/workflows/deploy.yml" ]; then
    act --dry-run || {
        print_error "Pipeline simulation failed"
        exit 1
    }
    print_status "Pipeline simulation successful"
fi

# Cleanup
print_step "7. Cleaning up..."
docker rmi casino-app-test || true

print_status "✅ CI/CD Pipeline testing completed!"
echo ""
echo "📊 Test Reports Generated:"
echo "• bandit-report.json - Security scan results"
echo "• safety-report.json - Dependency vulnerability scan"
echo ""
echo "💡 Next Steps:"
echo "• Review security reports"
echo "• Fix any issues found"
echo "• Test actual GitHub Actions by pushing to a branch" 