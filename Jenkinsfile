pipeline {
    agent any
    
    options {
        timestamps()
        ansiColor('xterm')
        buildDiscarder(logRotator(numToKeepStr: '30'))
        timeout(time: 60, unit: 'MINUTES')
    }
    
    parameters {
        choice(name: 'DEPLOY_ENV', choices: ['', 'dev', 'staging', 'prod'], description: 'Environment to deploy to')
        string(name: 'IMAGE_TAG', defaultValue: '', description: 'Override image tag')
    }
    
    environment {
        REGISTRY = 'docker.io'
        IMAGE_REPO = 'your-dockerhub-username/your-app'
        HELM_EXPERIMENTAL_OCI = '1'
    }
    
    stages {
        stage('Verify Plugins') {
            steps {
                script {
                    def requiredPlugins = [
                        'workflow-aggregator',
                        'git',
                        'git-client', 
                        'credentials',
                        'credentials-binding',
                        'pipeline-utility-steps',
                        'ssh-agent',
                        'docker-workflow',
                        'mailer',
                        'email-ext'
                    ]
                    
                    def missingPlugins = []
                    requiredPlugins.each { plugin ->
                        if (!Jenkins.instance.pluginManager.getPlugin(plugin)) {
                            missingPlugins.add(plugin)
                        }
                    }
                    
                    if (missingPlugins.size() > 0) {
                        error("Missing required plugins: ${missingPlugins.join(', ')}")
                    }
                    
                    echo "✅ All required plugins are installed"
                }
            }
        }
        
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.SHORT_SHA = sh(returnStdout: true, script: 'git rev-parse --short=7 HEAD').trim()
                    env.DATE_TAG = sh(returnStdout: true, script: 'date +%Y%m%d').trim()
                    env.TAG = "${env.DATE_TAG}-${env.SHORT_SHA}"
                    env.IS_MAIN = (env.BRANCH_NAME == 'main')
                    
                    echo "Branch: ${env.BRANCH_NAME}"
                    echo "Tag: ${env.TAG}"
                    echo "Is main branch: ${env.IS_MAIN}"
                }
            }
        }
        
        stage('Setup Python') {
            steps {
                sh '''
                    python3 -m pip install --user -r requirements.txt
                    mkdir -p reports
                '''
            }
        }
        
        stage('Lint & Test') {
            steps {
                sh 'make test'
            }
            post {
                always {
                    junit testResults: 'reports/junit-*.xml', allowEmptyResults: true
                }
            }
        }
        
        stage('Build Image') {
            steps {
                script {
                    sh "make image IMAGE=${env.IMAGE_REPO}:${env.TAG}"
                    if (env.IS_MAIN == 'true') {
                        sh "docker tag ${env.IMAGE_REPO}:${env.TAG} ${env.IMAGE_REPO}:latest"
                    }
                }
            }
        }
        
        stage('Helm Lint/Template') {
            steps {
                sh 'make helm-lint'
                sh 'make helm-template'
            }
        }
        
        stage('Push & Package') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo $DOCKER_PASS | docker login $REGISTRY -u $DOCKER_USER --password-stdin
                        docker push ${IMAGE_REPO}:${TAG}
                        docker push ${IMAGE_REPO}:latest
                    '''
                }
                
                sh 'make helm-package'
                
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo $DOCKER_PASS | helm registry login $REGISTRY -u $DOCKER_USER --password-stdin
                        helm push dist/helm/app-*.tgz oci://docker.io/your-dockerhub-username/helm
                    '''
                }
            }
        }
        
        stage('GitOps Deploy') {
            when {
                expression { params.DEPLOY_ENV == 'dev' }
            }
            steps {
                script {
                    def imageTag = params.IMAGE_TAG ?: env.TAG
                    echo "Deploying to dev with image tag: ${imageTag}"
                    
                    withCredentials([string(credentialsId: 'git-creds', variable: 'GIT_TOKEN')]) {
                        sh """
                            git config user.name "Jenkins CI"
                            git config user.email "jenkins@example.com"
                            
                            # Update dev values file
                            sed -i 's/tag: .*/tag: ${imageTag}/' environments/dev/values.yaml
                            
                            # Create and push release branch
                            git checkout -b release/dev || git checkout release/dev
                            git add environments/dev/values.yaml
                            git commit -m "Deploy ${imageTag} to dev environment"
                            
                            git remote set-url origin https://\${GIT_TOKEN}@github.com/your-username/your-repo.git
                            git push origin release/dev
                        """
                    }
                    
                    echo "✅ GitOps update completed - ArgoCD will sync the changes"
                }
            }
        }
    }
    
    post {
        failure {
            script {
                def logOutput = sh(returnStdout: true, script: 'tail -50 ${BUILD_LOG_FILE} || echo "Could not get log output"')
                
                // Slack/Discord notification
                withCredentials([string(credentialsId: 'chat-webhook', variable: 'WEBHOOK_URL')]) {
                    sh """
                        curl -X POST -H 'Content-type: application/json' \
                        --data '{"text":"🚨 Build Failed\\nJob: ${env.JOB_NAME}\\nBranch: ${env.BRANCH_NAME}\\nBuild: ${env.BUILD_URL}\\nLast 50 lines:\\n```${logOutput}```"}' \
                        \${WEBHOOK_URL}
                    """
                }
                
                // Email notification
                def developer = env.CHANGE_AUTHOR_EMAIL ?: env.GIT_COMMITTER_EMAIL ?: 'dev@example.com'
                emailext(
                    subject: "❌ Build Failed: ${env.JOB_NAME} - ${env.BRANCH_NAME}",
                    body: """
                        Build failed for ${env.JOB_NAME} on branch ${env.BRANCH_NAME}
                        
                        Build URL: ${env.BUILD_URL}
                        Commit: ${env.SHORT_SHA}
                        
                        Last 50 lines of log:
                        ${logOutput}
                    """,
                    to: "managers@example.com,${developer}"
                )
            }
        }
        
        success {
            script {
                if (currentBuild.previousBuild?.result != 'SUCCESS') {
                    def developer = env.CHANGE_AUTHOR_EMAIL ?: env.GIT_COMMITTER_EMAIL ?: 'dev@example.com'
                    emailext(
                        subject: "✅ Build Back to Normal: ${env.JOB_NAME} - ${env.BRANCH_NAME}",
                        body: """
                            Build is back to normal for ${env.JOB_NAME} on branch ${env.BRANCH_NAME}
                            
                            Build URL: ${env.BUILD_URL}
                            Commit: ${env.SHORT_SHA}
                        """,
                        to: "managers@example.com,${developer}"
                    )
                }
            }
        }
        
        always {
            cleanWs()
        }
    }
}