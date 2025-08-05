import jenkins.model.Jenkins

println "=== Checking Plugin Status ==="

def jenkins = Jenkins.getInstance()
def pluginManager = jenkins.getPluginManager()

println "\n--- Disabled Plugins ---"
pluginManager.getPlugins().findAll { !it.isEnabled() }.each { plugin ->
    println "${plugin.getShortName()}: ${plugin.getDisplayName()} - Enabled: ${plugin.isEnabled()}"
}

println "\n--- Failed Plugins ---"
pluginManager.getFailedPlugins().each { plugin ->
    println "FAILED: ${plugin.name} - ${plugin.cause?.getMessage()}"
}

println "\n--- Plugin Dependencies Check ---"
pluginManager.getPlugins().findAll { !it.isEnabled() }.each { plugin ->
    plugin.getDependencies().each { dep ->
        def depPlugin = pluginManager.getPlugin(dep.shortName)
        if (depPlugin == null) {
            println "MISSING DEPENDENCY: ${plugin.shortName} requires ${dep.shortName} (${dep.version})"
        }
    }
}

println "\n=== Check Complete ==="