import jenkins.model.*
import hudson.model.*
import org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject
import org.jenkinsci.plugins.workflow.libs.SCMSourceRetriever
import jenkins.branch.BranchSource
import jenkins.plugins.git.GitSCMSource
import com.cloudbees.plugins.credentials.common.StandardUsernamePasswordCredentials
import hudson.plugins.git.BranchSpec
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition

def jenkins = Jenkins.getInstance()

// Create the main multibranch pipeline job
def jobName = "casino-app-pipeline"
def job = jenkins.getItem(jobName)

if (job == null) {
    println "Creating multibranch pipeline job: ${jobName}"
    
    // Create multibranch pipeline
    job = jenkins.createProject(WorkflowMultiBranchProject, jobName)
    job.setDisplayName("Casino App CI/CD Pipeline")
    job.setDescription("Automated CI/CD pipeline for the casino cloud application")
    
    // Configure Git source
    def gitSource = new GitSCMSource("casino-app-repo")
    gitSource.setRemote("https://github.com/your-username/casino-cloud-app.git")
    gitSource.setCredentialsId("git-creds")
    
    def branchSource = new BranchSource(gitSource)
    job.getSourcesList().add(branchSource)
    
    // Set script path to Jenkinsfile
    job.getProjectFactory().setScriptPath("Jenkinsfile")
    
    job.save()
    jenkins.reload()
    
    println "Successfully created multibranch pipeline job: ${jobName}"
} else {
    println "Multibranch pipeline job already exists: ${jobName}"
}

// Create seed job for additional pipeline creation
def seedJobName = "seed-pipeline"
def seedJob = jenkins.getItem(seedJobName)

if (seedJob == null) {
    println "Creating seed job: ${seedJobName}"
    
    seedJob = jenkins.createProject(WorkflowJob, seedJobName)
    seedJob.setDisplayName("Pipeline Seed Job")
    seedJob.setDescription("Job to create additional pipelines using Job DSL")
    
    // Read the seed job groovy script
    def seedScript = """
        node {
            stage('Create Jobs') {
                jobDsl targets: 'jenkins/jobs/seed-job.groovy',
                       removedJobAction: 'IGNORE',
                       removedViewAction: 'IGNORE',
                       lookupStrategy: 'SEED_JOB'
            }
        }
    """
    
    def definition = new CpsFlowDefinition(seedScript, true)
    seedJob.setDefinition(definition)
    
    seedJob.save()
    
    println "Successfully created seed job: ${seedJobName}"
} else {
    println "Seed job already exists: ${seedJobName}"
}

println "Job creation completed successfully!"