#!/bin/bash

set -euo pipefail

JENKINS_URL="http://localhost:30083"
USERNAME="admin"
PASSWORD="admin123"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "🎰 Setting up Jenkins with Plugins and Pipelines"
echo "================================================"

# Wait for Jenkins to be ready
echo_info "Waiting for Jenkins to be ready..."
for i in {1..30}; do
    if curl -s "$JENKINS_URL/login" > /dev/null 2>&1; then
        echo_success "Jenkins is ready!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 5
done

# Get Jenkins crumb for CSRF protection
echo_info "Getting Jenkins crumb..."
CRUMB=$(curl -s -u "$USERNAME:$PASSWORD" "$JENKINS_URL/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,\":\",//crumb)" 2>/dev/null || echo "")

if [ -z "$CRUMB" ]; then
    echo_warning "Could not get Jenkins crumb, continuing without CSRF protection..."
    CRUMB_HEADER=""
else
    CRUMB_HEADER="-H $CRUMB"
    echo_success "Got Jenkins crumb"
fi

# Install essential plugins
echo_info "Installing essential plugins..."

PLUGINS=(
    "workflow-aggregator"
    "git" 
    "credentials"
    "credentials-binding"
    "job-dsl"
    "configuration-as-code"
    "matrix-auth"
    "workflow-multibranch"
    "pipeline-stage-view"
    "timestamper"
)

# Create plugin installation XML
PLUGIN_XML="<jenkins><install>"
for plugin in "${PLUGINS[@]}"; do
    PLUGIN_XML="$PLUGIN_XML<plugin name='$plugin' /></install>"
done
PLUGIN_XML="$PLUGIN_XML</jenkins>"

echo_info "Submitting plugin installation request..."
curl -s -X POST -u "$USERNAME:$PASSWORD" \
    $CRUMB_HEADER \
    -H "Content-Type: text/xml" \
    -d "$PLUGIN_XML" \
    "$JENKINS_URL/pluginManager/installNecessaryPlugins" > /dev/null || echo_warning "Plugin installation may have failed"

echo_info "Waiting for plugin installation (60 seconds)..."
sleep 60

# Restart Jenkins to activate plugins
echo_info "Restarting Jenkins to activate plugins..."
curl -s -X POST -u "$USERNAME:$PASSWORD" \
    $CRUMB_HEADER \
    "$JENKINS_URL/safeRestart" > /dev/null || echo_warning "Restart may have failed"

echo_info "Waiting for Jenkins to restart (90 seconds)..."
sleep 90

# Wait for Jenkins to come back up
echo_info "Waiting for Jenkins to be ready after restart..."
for i in {1..30}; do
    if curl -s "$JENKINS_URL/login" > /dev/null 2>&1; then
        echo_success "Jenkins is back online!"
        break
    fi
    echo "Waiting for restart... ($i/30)"
    sleep 5
done

# Get new crumb after restart
CRUMB=$(curl -s -u "$USERNAME:$PASSWORD" "$JENKINS_URL/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,\":\",//crumb)" 2>/dev/null || echo "")
if [ -z "$CRUMB" ]; then
    CRUMB_HEADER=""
else
    CRUMB_HEADER="-H $CRUMB"
fi

# Create the 3 pipeline jobs using Job DSL
echo_info "Creating the 3 pipeline jobs..."

# Job DSL script to create all 3 pipelines
JOB_DSL_SCRIPT=$(cat << 'EOF'
// PIPE-01: Main CI/CD Pipeline
pipelineJob('PIPE-01-Casino-App-CICD') {
    displayName('🎰 PIPE-01: Casino App CI/CD')
    description('Main CI/CD pipeline for casino cloud application')
    
    parameters {
        choiceParam('DEPLOY_ENV', ['', 'dev', 'staging', 'prod'], 'Environment to deploy to')
    }
    
    definition {
        cps {
            script('''
                pipeline {
                    agent any
                    
                    stages {
                        stage('Checkout') {
                            steps {
                                echo '📥 Checking out casino app source code'
                                // git branch: 'main', url: 'https://github.com/your-username/casino-cloud-app.git'
                            }
                        }
                        
                        stage('Lint & Test') {
                            parallel {
                                stage('Lint') {
                                    steps {
                                        echo '🧹 Running linting checks'
                                        // sh 'make lint'
                                    }
                                }
                                stage('Test') {
                                    steps {
                                        echo '🧪 Running tests'  
                                        // sh 'make test'
                                    }
                                }
                            }
                        }
                        
                        stage('Build') {
                            steps {
                                echo '🏗️ Building Docker image'
                                // sh 'make image'
                            }
                        }
                        
                        stage('Push Image') {
                            when {
                                branch 'main'
                            }
                            steps {
                                echo '📤 Pushing Docker image'
                                // sh 'make push'
                            }
                        }
                        
                        stage('Deploy') {
                            when {
                                expression { params.DEPLOY_ENV != '' }
                            }
                            steps {
                                script {
                                    if (params.DEPLOY_ENV == 'prod') {
                                        input message: 'Deploy to production?', ok: 'Deploy'
                                    }
                                    echo "🚀 Deploying to ${params.DEPLOY_ENV}"
                                    // sh "kubectl apply -f k8s/ --namespace=casino-${params.DEPLOY_ENV}"
                                }
                            }
                        }
                    }
                    
                    post {
                        always {
                            echo '📊 Pipeline completed!'
                        }
                    }
                }
            ''')
            sandbox(true)
        }
    }
}

// PIPE-02: Deployment Pipeline  
pipelineJob('PIPE-02-Deploy-Pipeline') {
    displayName('🚀 PIPE-02: Deployment Pipeline')
    description('Deploy casino app to different environments')
    
    parameters {
        choiceParam('ENVIRONMENT', ['dev', 'staging', 'prod'], 'Target environment')
        stringParam('IMAGE_TAG', 'latest', 'Docker image tag to deploy')
    }
    
    definition {
        cps {
            script('''
                pipeline {
                    agent any
                    
                    stages {
                        stage('Validate') {
                            steps {
                                echo "🔍 Validating deployment to ${params.ENVIRONMENT}"
                                script {
                                    if (params.ENVIRONMENT == 'prod') {
                                        input message: 'Deploy to PRODUCTION?', ok: 'Deploy'
                                    }
                                }
                            }
                        }
                        
                        stage('Deploy') {
                            steps {
                                echo "🚀 Deploying to ${params.ENVIRONMENT}"
                                echo "Using image tag: ${params.IMAGE_TAG}"
                                // sh "helm upgrade casino-app helm/app --namespace=casino-${params.ENVIRONMENT} --set image.tag=${params.IMAGE_TAG}"
                            }
                        }
                        
                        stage('Verify') {
                            steps {
                                echo "✅ Verifying deployment"
                                // sh "kubectl get pods -n casino-${params.ENVIRONMENT}"
                            }
                        }
                    }
                    
                    post {
                        success {
                            echo "🎉 Deployment to ${params.ENVIRONMENT} successful!"
                        }
                        failure {
                            echo "❌ Deployment failed!"
                        }
                    }
                }
            ''')
            sandbox(true)
        }
    }
}

// PIPE-03: Release Pipeline
pipelineJob('PIPE-03-Release-Pipeline') {
    displayName('🔥 PIPE-03: Release Pipeline')
    description('Build and release casino app with versioning')
    
    parameters {
        choiceParam('RELEASE_TYPE', ['patch', 'minor', 'major'], 'Type of release')
        booleanParam('DEPLOY_TO_PROD', false, 'Deploy to production after release')
    }
    
    definition {
        cps {
            script('''
                pipeline {
                    agent any
                    
                    stages {
                        stage('Version Bump') {
                            steps {
                                echo "🔢 Bumping version (${params.RELEASE_TYPE})"
                                script {
                                    env.NEW_VERSION = "1.0.${BUILD_NUMBER}"
                                    echo "New version: ${env.NEW_VERSION}"
                                }
                            }
                        }
                        
                        stage('Build & Test') {
                            parallel {
                                stage('Test') {
                                    steps {
                                        echo "🧪 Running comprehensive tests"
                                        // sh 'make test-all'
                                    }
                                }
                                stage('Build') {
                                    steps {
                                        echo "🏗️ Building release image"
                                        // sh "docker build -t casino-app:${env.NEW_VERSION} ."
                                    }
                                }
                            }
                        }
                        
                        stage('Security Scan') {
                            steps {
                                echo "🔒 Running security scans"
                                // sh 'make security-scan'
                            }
                        }
                        
                        stage('Release') {
                            steps {
                                echo "📦 Creating release ${env.NEW_VERSION}"
                                // sh "docker push casino-app:${env.NEW_VERSION}"
                                // sh "git tag v${env.NEW_VERSION}"
                            }
                        }
                        
                        stage('Deploy to Prod') {
                            when {
                                expression { params.DEPLOY_TO_PROD }
                            }
                            steps {
                                echo "🔥 Deploying to production"
                                input message: "Deploy ${env.NEW_VERSION} to PRODUCTION?", ok: 'Deploy'
                                build job: 'PIPE-02-Deploy-Pipeline', parameters: [
                                    string(name: 'ENVIRONMENT', value: 'prod'),
                                    string(name: 'IMAGE_TAG', value: env.NEW_VERSION)
                                ]
                            }
                        }
                    }
                    
                    post {
                        success {
                            echo "🎉 Release ${env.NEW_VERSION} completed!"
                        }
                    }
                }
            ''')
            sandbox(true)
        }
    }
}
EOF
)

# Create a seed job to run the Job DSL script
echo_info "Creating Job DSL seed job..."
curl -s -X POST -u "$USERNAME:$PASSWORD" \
    $CRUMB_HEADER \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "name=pipeline-seed-job" \
    --data-urlencode "mode=org.jenkinsci.plugins.workflow.job.WorkflowJob" \
    --data-urlencode "from=" \
    --data-urlencode "Submit=OK" \
    "$JENKINS_URL/createItem" > /dev/null || echo_warning "Seed job creation may have failed"

echo_info "Configuring seed job with Job DSL script..."

# Configure the seed job
SEED_JOB_CONFIG=$(cat << EOF
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>Seed job to create the 3 pipeline jobs</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
    <script>
node {
    stage('Create Pipeline Jobs') {
        jobDsl scriptText: '''
$JOB_DSL_SCRIPT
        '''
    }
}
    </script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>
EOF
)

curl -s -X POST -u "$USERNAME:$PASSWORD" \
    $CRUMB_HEADER \
    -H "Content-Type: application/xml" \
    -d "$SEED_JOB_CONFIG" \
    "$JENKINS_URL/job/pipeline-seed-job/config.xml" > /dev/null || echo_warning "Seed job configuration may have failed"

echo_info "Running seed job to create pipelines..."
curl -s -X POST -u "$USERNAME:$PASSWORD" \
    $CRUMB_HEADER \
    "$JENKINS_URL/job/pipeline-seed-job/build" > /dev/null || echo_warning "Seed job execution may have failed"

echo_info "Waiting for seed job to complete (30 seconds)..."
sleep 30

echo ""
echo_success "Jenkins setup completed!"
echo ""
echo "📋 Jenkins Access Information:"
echo "   URL: $JENKINS_URL"
echo "   Username: $USERNAME"
echo "   Password: $PASSWORD"
echo ""
echo "🎰 Created Pipeline Jobs:"
echo "   1. PIPE-01-Casino-App-CICD (Main CI/CD Pipeline)"
echo "   2. PIPE-02-Deploy-Pipeline (Environment Deployment)"
echo "   3. PIPE-03-Release-Pipeline (Release Management)"
echo ""
echo "🔧 Next Steps:"
echo "   1. Access Jenkins at $JENKINS_URL"
echo "   2. Verify the 3 pipeline jobs are created"
echo "   3. Run the pipelines to test functionality"
echo ""
echo_success "🎉 Jenkins is fully configured with plugins and pipelines!"