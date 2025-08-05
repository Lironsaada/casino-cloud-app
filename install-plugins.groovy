import jenkins.model.*
import hudson.PluginWrapper
import hudson.model.UpdateCenter
import hudson.model.UpdateSite
import hudson.util.VersionNumber

println "=== Installing Required Plugins for GitLab Multibranch ==="

def jenkins = Jenkins.getInstance()
def pluginManager = jenkins.getPluginManager()
def updateCenter = jenkins.getUpdateCenter()

// List of required plugins
def requiredPlugins = [
    'workflow-aggregator',    // Core pipeline functionality
    'git',                   // Git SCM support
    'credentials',           // Credential management
    'branch-api',            // Branch API for multibranch
    'workflow-multibranch',  // Multibranch pipeline support
    'cloudbees-folder',      // Folder organization
    'job-dsl',              // Job DSL for programmatic job creation
    'gitlab-plugin',         // GitLab integration
    'scm-api',              // SCM API
    'workflow-cps',         // Pipeline Groovy support
    'pipeline-stage-view'    // Pipeline visualization
]

// Function to install a plugin if not already installed
def installPlugin(pluginName) {
    def plugin = pluginManager.getPlugin(pluginName)
    if (plugin != null) {
        if (plugin.isActive()) {
            println "✅ ${pluginName}: Already installed and active"
            return true
        } else {
            println "⚠️ ${pluginName}: Installed but not active"
            return false
        }
    }
    
    // Plugin not installed, try to install it
    println "📦 Installing ${pluginName}..."
    
    try {
        // Update plugin update sites first
        for (UpdateSite site : updateCenter.getSites()) {
            site.updateDirectlyNow()
        }
        
        def availablePlugin = updateCenter.getPlugin(pluginName)
        if (availablePlugin == null) {
            println "❌ ${pluginName}: Not found in update center"
            return false
        }
        
        // Install the plugin
        def future = availablePlugin.deploy(true) // true = restart if needed
        println "⏳ ${pluginName}: Installation initiated..."
        return true
        
    } catch (Exception e) {
        println "❌ ${pluginName}: Installation failed: ${e.getMessage()}"
        return false
    }
}

// Install all required plugins
def installResults = [:]
requiredPlugins.each { pluginName ->
    installResults[pluginName] = installPlugin(pluginName)
}

// Save Jenkins configuration
jenkins.save()

// Print summary
println "\n=== Plugin Installation Summary ==="
installResults.each { pluginName, success ->
    def status = success ? "✅" : "❌"
    println "${status} ${pluginName}"
}

// Create marker file
def jenkinsHome = jenkins.getRootDir()
def markerFile = new File(jenkinsHome, "plugins-install-attempted.marker")
markerFile.text = "Plugin installation attempted at: ${new Date()}\n${installResults.toString()}"

println "\n=== Plugin Installation Complete ==="
println "Note: Jenkins may need to restart to activate new plugins"