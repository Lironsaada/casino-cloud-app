import jenkins.model.*
import hudson.PluginManager
import hudson.model.UpdateCenter

def jenkins = Jenkins.getInstance()
def pluginManager = jenkins.getPluginManager()
def updateCenter = jenkins.getUpdateCenter()

println "Waiting for all plugins to be installed and loaded..."

// List of required plugins
def requiredPlugins = [
    'workflow-aggregator',
    'git',
    'git-client', 
    'credentials',
    'credentials-binding',
    'pipeline-utility-steps',
    'ssh-agent',
    'docker-workflow',
    'job-dsl',
    'configuration-as-code',
    'mailer',
    'matrix-auth'
]

// Wait for plugins to be installed
def maxRetries = 60
def retryCount = 0

while (retryCount < maxRetries) {
    def allInstalled = true
    def missingPlugins = []
    
    for (pluginName in requiredPlugins) {
        def plugin = pluginManager.getPlugin(pluginName)
        if (plugin == null || !plugin.isActive()) {
            allInstalled = false
            missingPlugins.add(pluginName)
        }
    }
    
    if (allInstalled) {
        println "All required plugins are installed and active!"
        break
    } else {
        println "Waiting for plugins to install... Missing: ${missingPlugins.join(', ')}"
        Thread.sleep(5000) // Wait 5 seconds
        retryCount++
    }
}

if (retryCount >= maxRetries) {
    println "WARNING: Timeout waiting for plugins to install"
} else {
    println "Plugin installation verification completed successfully!"
}