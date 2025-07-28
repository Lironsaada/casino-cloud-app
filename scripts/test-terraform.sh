#!/bin/bash

set -e

echo "🏗️ Testing Terraform Infrastructure"
echo "==================================="

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

# Change to terraform directory
cd infra || {
    print_error "infra directory not found"
    exit 1
}

# Test 1: Terraform Format Check
print_step "1. Checking Terraform formatting..."
terraform fmt -check -recursive || {
    print_warning "Terraform files need formatting. Running terraform fmt..."
    terraform fmt -recursive
    print_status "Files formatted"
}

# Test 2: Terraform Validation
print_step "2. Validating Terraform configuration..."
terraform init -backend=false
terraform validate || {
    print_error "Terraform validation failed"
    exit 1
}
print_status "Terraform configuration is valid"

# Test 3: Security Scanning with tfsec
print_step "3. Running security scan with tfsec..."
if command -v tfsec &> /dev/null; then
    tfsec . --format json --out tfsec-report.json || {
        print_warning "Security issues found, check tfsec-report.json"
    }
    print_status "Security scan completed"
else
    print_warning "tfsec not installed, installing..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install tfsec
    else
        print_warning "Please install tfsec manually"
    fi
fi

# Test 4: Cost Estimation with Infracost
print_step "4. Estimating infrastructure costs..."
if command -v infracost &> /dev/null; then
    infracost breakdown --path . --format json --out-file infracost-report.json || {
        print_warning "Cost estimation failed"
    }
    print_status "Cost estimation completed"
else
    print_warning "Infracost not installed, skipping cost estimation"
    echo "Install with: curl -fsSL https://raw.githubusercontent.com/infracost/infracost/master/scripts/install.sh | sh"
fi

# Test 5: Terraform Plan (Dry Run)
print_step "5. Running Terraform plan (dry run)..."

# Create a test tfvars file
cat > test.tfvars << EOF
resource_group_name = "casino-test-rg"
location = "East US"
acr_name = "casinotestacr$(date +%s)"
aks_cluster_name = "casino-test-aks"
EOF

print_status "Created test variables file"

# Run terraform plan with test variables
terraform plan -var-file=test.tfvars -out=test.tfplan || {
    print_error "Terraform plan failed"
    exit 1
}

print_status "Terraform plan successful"

# Test 6: Analyze the plan
print_step "6. Analyzing Terraform plan..."
terraform show -json test.tfplan > plan-analysis.json

# Count resources to be created
RESOURCES_TO_CREATE=$(jq '.resource_changes | map(select(.change.actions[] == "create")) | length' plan-analysis.json)
RESOURCES_TO_UPDATE=$(jq '.resource_changes | map(select(.change.actions[] == "update")) | length' plan-analysis.json)
RESOURCES_TO_DELETE=$(jq '.resource_changes | map(select(.change.actions[] == "delete")) | length' plan-analysis.json)

echo ""
echo "📊 Plan Analysis:"
echo "• Resources to create: $RESOURCES_TO_CREATE"
echo "• Resources to update: $RESOURCES_TO_UPDATE"
echo "• Resources to delete: $RESOURCES_TO_DELETE"

# Test 7: Validate Kubernetes manifests
print_step "7. Validating Kubernetes manifests..."
cd ../infra/k8s || {
    print_error "k8s directory not found"
    exit 1
}

# Check if kubeval is installed
if command -v kubeval &> /dev/null; then
    for file in *.yaml; do
        if [ -f "$file" ]; then
            kubeval "$file" || {
                print_warning "Validation failed for $file"
            }
        fi
    done
    
    # Validate monitoring manifests
    if [ -d "monitoring" ]; then
        for file in monitoring/*.yaml; do
            if [ -f "$file" ]; then
                kubeval "$file" || {
                    print_warning "Validation failed for $file"
                }
            fi
        done
    fi
    
    print_status "Kubernetes manifest validation completed"
else
    print_warning "kubeval not installed, skipping K8s validation"
    echo "Install with: wget https://github.com/instrumenta/kubeval/releases/latest/download/kubeval-linux-amd64.tar.gz"
fi

# Test 8: Lint Kubernetes manifests
print_step "8. Linting Kubernetes manifests..."
if command -v kube-score &> /dev/null; then
    for file in *.yaml; do
        if [ -f "$file" ]; then
            kube-score score "$file" || {
                print_warning "Linting issues in $file"
            }
        fi
    done
    print_status "Kubernetes linting completed"
else
    print_warning "kube-score not installed, skipping K8s linting"
fi

# Cleanup
cd ../../infra
print_step "9. Cleaning up test files..."
rm -f test.tfvars test.tfplan plan-analysis.json

print_status "✅ Terraform infrastructure testing completed!"
echo ""
echo "📊 Test Reports Generated:"
echo "• tfsec-report.json - Security scan results"
echo "• infracost-report.json - Cost estimation"
echo ""
echo "💡 Next Steps:"
echo "• Review security scan results"
echo "• Check cost estimates"
echo "• Run 'terraform apply' in a test environment"
echo "• Test Kubernetes deployment with 'kubectl apply --dry-run=client'" 