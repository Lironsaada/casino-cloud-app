pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                echo "🚀 Building ${env.BRANCH_NAME ?: 'branch'} - Build #${env.BUILD_NUMBER}"
                sh '''
                    echo "Git commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
                    echo "Workspace: $(pwd)"
                    echo "Files: $(ls -la | wc -l) items"
                    echo "✅ Build completed successfully!"
                '''
                
                // Create simple artifact
                writeFile file: 'build-result.txt', text: "Build ${env.BUILD_NUMBER} successful on ${new Date()}"
                archiveArtifacts artifacts: 'build-result.txt', allowEmptyArchive: true
            }
        }
    }
    
    post {
        always {
            echo "Build finished: ${currentBuild.result ?: 'SUCCESS'}"
        }
    }
}