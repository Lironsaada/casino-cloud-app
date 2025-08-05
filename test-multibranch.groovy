import jenkins.model.Jenkins
import org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject

println "=== Testing Multibranch Pipeline Functionality ==="

def jenkins = Jenkins.getInstance()

// Test if we can create a multibranch project class
try {
    def testProject = new WorkflowMultiBranchProject(jenkins, 'test-multibranch')
    println "✅ WorkflowMultiBranchProject can be instantiated"
    
    // Check if Configuration as Code plugin is working
    def casc = jenkins.getExtensionList("io.jenkins.plugins.casc.ConfigurationAsCode")
    if (casc.size() > 0) {
        println "✅ Configuration as Code plugin is loaded and working"
    } else {
        println "⚠️ Configuration as Code plugin not found"
    }
    
    // Check matrix auth
    def matrixAuth = jenkins.getDescriptor("hudson.security.GlobalMatrixAuthorizationStrategy")
    if (matrixAuth != null) {
        println "✅ Matrix Authorization Strategy is available"
    } else {
        println "⚠️ Matrix Authorization Strategy not found"
    }
    
} catch (Exception e) {
    println "❌ Error testing multibranch functionality: ${e.getMessage()}"
}

println "=== Test Complete ==="