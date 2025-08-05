import jenkins.model.Jenkins

println "=== Reloading Jenkins Configuration ==="

def jenkins = Jenkins.getInstance()

try {
    // Reload configuration from disk
    jenkins.reload()
    println "✅ Jenkins configuration reloaded successfully"
    
    Thread.sleep(3000) // Wait for reload to complete
    
    // Check if casino-app job is now available
    def job = jenkins.getItemByFullName('casino-app')
    if (job != null) {
        println "✅ Found casino-app job after reload"
        println "📋 Display Name: ${job.getDisplayName()}"
        println "📝 Description: ${job.getDescription()}"
        
        // Trigger a scan to refresh branches
        println "🔄 Triggering initial branch scan..."
        job.scheduleBuild(0, new hudson.model.Cause.UserIdCause())
        println "✅ Branch scan triggered"
        
        println "🌐 Access job at: http://localhost:30081/job/casino-app/"
    } else {
        println "❌ casino-app job still not found after reload"
    }
    
} catch (Exception e) {
    println "❌ Error reloading configuration: ${e.getMessage()}"
    e.printStackTrace()
}

println "=== Configuration Reload Complete ==="