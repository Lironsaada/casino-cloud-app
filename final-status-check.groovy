import jenkins.model.Jenkins

println "=== Casino App Multibranch Pipeline - Final Status ==="

def jenkins = Jenkins.getInstance()

// Check if job exists
def job = jenkins.getItemByFullName('casino-app')
if (job != null) {
    println "✅ Casino App multibranch pipeline exists"
    println "📋 Display Name: ${job.getDisplayName()}"
    println "📝 Description: ${job.getDescription()}"
    
    // Check sources
    def sources = job.getSources()
    if (sources && sources.size() > 0) {
        println "✅ Repository sources configured: ${sources.size()}"
        sources.each { source ->
            def gitSource = source.getSource()
            println "  🔗 Repository: ${gitSource.getRemote()}"
            println "  🔑 Credentials ID: ${gitSource.getCredentialsId()}"
            println "  🏷️  Source ID: ${gitSource.getId()}"
        }
    }
    
    // Check triggers
    def triggers = job.getTriggers()
    if (triggers && triggers.size() > 0) {
        println "✅ Periodic triggers configured: ${triggers.size()}"
        triggers.each { trigger ->
            if (trigger.hasProperty('spec')) {
                println "  ⏰ Schedule: ${trigger.getSpec()}"
            }
        }
    }
    
    // Check orphaned item strategy
    def orphanedStrategy = job.getOrphanedItemStrategy()
    if (orphanedStrategy != null) {
        println "✅ Orphaned item strategy configured"
        println "  🗑️  Prune dead branches: ${orphanedStrategy.isPruneDeadBranches()}"
        println "  📅 Days to keep: ${orphanedStrategy.getDaysToKeep()}"
        println "  🔢 Number to keep: ${orphanedStrategy.getNumToKeep()}"
    }
    
    // Check discovered branches
    def branches = job.getItems()
    println "🌿 Discovered branches: ${branches.size()}"
    if (branches.size() > 0) {
        branches.each { branch ->
            println "  - ${branch.getName()}"
        }
    } else {
        println "  ⚠️  No branches discovered yet (may need credentials)"
    }
    
    println ""
    println "🌐 Access URL: http://localhost:30081/job/casino-app/"
    
} else {
    println "❌ casino-app job not found"
}

// Check credentials
def store = jenkins.getExtensionList('com.cloudbees.plugins.credentials.SystemCredentialsProvider')[0].getStore()
def gitCreds = store.getCredentials(com.cloudbees.plugins.credentials.domains.Domain.global()).find { it.id == 'git-creds' }

println ""
println "=== Credentials Status ==="
if (gitCreds != null) {
    println "✅ GitLab credentials 'git-creds' exist"
    println "📋 Description: ${gitCreds.getDescription()}"
    println "👤 Username: ${gitCreds.getUsername()}"
    
    if (gitCreds.getPassword().getPlainText() == "YOUR_GITLAB_TOKEN") {
        println "⚠️  WARNING: Placeholder token detected!"
        println "🔧 Action required: Update with real GitLab token"
    } else {
        println "✅ Token appears to be configured"
    }
} else {
    println "❌ No GitLab credentials found"
}

println ""
println "=== Next Steps ==="
println "1. 🔑 Create a GitLab Personal Access Token:"
println "   - Go to https://gitlab.com/-/profile/personal_access_tokens"
println "   - Create token with 'read_repository' scope"
println "   - Minimum expiration date recommended"
println ""
println "2. 🔧 Update Jenkins credentials:"
println "   - Go to http://localhost:30081/manage/credentials/"
println "   - Click on 'git-creds' credential"
println "   - Update password field with your GitLab token"
println "   - Save changes"
println ""
println "3. 🔄 Trigger branch scan:"
println "   - Go to http://localhost:30081/job/casino-app/"
println "   - Click 'Scan Repository Now'"
println "   - Or wait for automatic 15-minute scan"
println ""
println "4. ✅ Verify pipeline functionality:"
println "   - Check that branches are discovered"
println "   - Verify Jenkinsfile is found and parsed"
println "   - Monitor build execution"

println ""
println "=== Configuration Summary ==="
println "📂 Job Path: /var/jenkins_home/jobs/casino-app/"
println "⏰ Scan Interval: Every 15 minutes (H/15 * * * *)"
println "🔗 Repository: https://gitlab.com/sela-tracks/1117/students/liron/casino-app.git"
println "📝 Jenkinsfile Path: Jenkinsfile (root of repository)"
println "🗑️  Branch Cleanup: 30 days, max 20 branches"

println "=== Status Check Complete ==="