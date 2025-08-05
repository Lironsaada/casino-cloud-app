import jenkins.model.Jenkins
import org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject
import jenkins.branch.BranchSource
import jenkins.plugins.git.GitSCMSource
import jenkins.branch.DefaultBranchPropertyStrategy
import com.cloudbees.hudson.plugins.folder.computed.DefaultOrphanedItemStrategy
import org.jenkinsci.plugins.workflow.multibranch.BranchJobProperty

println "=== Creating Casino App Multibranch Pipeline ==="

def jenkins = Jenkins.getInstance()

// Remove existing job if it exists
def existingJob = jenkins.getItemByFullName('casino-app')
if (existingJob != null) {
    println "🗑️ Removing existing job: casino-app"
    existingJob.delete()
    Thread.sleep(2000)
}

// Create the multibranch project
def multibranchProject = new WorkflowMultiBranchProject(jenkins, 'casino-app')
multibranchProject.setDisplayName('Casino App - Multibranch Pipeline')
multibranchProject.setDescription('Multibranch pipeline for Casino Cloud Application from GitLab')

// Configure Git SCM source
def gitSCMSource = new GitSCMSource('casino-app-gitlab')
gitSCMSource.setRemote('https://gitlab.com/sela-tracks/1117/students/liron/casino-app.git')

// Include all branches
gitSCMSource.setTraits([
    new jenkins.plugins.git.traits.BranchDiscoveryTrait(),
    new jenkins.plugins.git.traits.CleanBeforeCheckoutTrait(),
    new jenkins.plugins.git.traits.CleanAfterCheckoutTrait()
])

// Create branch source
def branchSource = new BranchSource(gitSCMSource)
branchSource.setStrategy(new DefaultBranchPropertyStrategy(new BranchJobProperty[0]))

// Add the branch source to the project
multibranchProject.getSourcesList().add(branchSource)

// Configure orphaned item strategy
def orphanedStrategy = new DefaultOrphanedItemStrategy(true, "20", "30")
multibranchProject.setOrphanedItemStrategy(orphanedStrategy)

// Set the Jenkinsfile path
def factory = new org.jenkinsci.plugins.workflow.multibranch.WorkflowBranchProjectFactory()
factory.setScriptPath("Jenkinsfile")
multibranchProject.setProjectFactory(factory)

try {
    // Add the project to Jenkins
    jenkins.add(multibranchProject, 'casino-app')
    
    // Save Jenkins configuration
    jenkins.save()
    
    println "✅ Multibranch pipeline 'casino-app' created successfully!"
    println "📋 Display Name: ${multibranchProject.getDisplayName()}"
    println "📝 Description: ${multibranchProject.getDescription()}"
    println "🔗 Repository: https://gitlab.com/sela-tracks/1117/students/liron/casino-app.git"
    
    // Trigger initial scan
    println "🔄 Triggering initial branch scan..."
    multibranchProject.scheduleBuild(0, new hudson.model.Cause.UserIdCause())
    
    println "✅ SUCCESS: Casino-app multibranch pipeline is ready!"
    println "🌐 Access it at: http://localhost:8088/job/casino-app/"
    
} catch (Exception e) {
    println "❌ ERROR: Failed to create multibranch pipeline"
    println "Error: ${e.getMessage()}"
    e.printStackTrace()
}

println "=== Pipeline Creation Complete ==="