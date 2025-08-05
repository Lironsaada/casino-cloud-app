import jenkins.model.Jenkins
import com.cloudbees.plugins.credentials.CredentialsScope
import com.cloudbees.plugins.credentials.domains.Domain
import com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl
import hudson.util.Secret

println "=== Setting up GitLab Token Credentials ==="

def jenkins = Jenkins.getInstance()
def domain = Domain.global()
def store = jenkins.getExtensionList('com.cloudbees.plugins.credentials.SystemCredentialsProvider')[0].getStore()

// GitLab credentials setup
def credentialsId = "git-creds"

// For GitLab private repositories, you need either:
// 1. Personal Access Token (recommended)
// 2. Username/Password
// 3. Deploy Token

// Remove existing credentials if any
def existingCreds = store.getCredentials(domain).find { it.id == credentialsId }
if (existingCreds) {
    println "🔄 Removing existing credentials: ${credentialsId}"
    store.removeCredentials(domain, existingCreds)
}

// Option 1: Create credentials with a placeholder token
// Users need to replace 'YOUR_GITLAB_TOKEN' with their actual GitLab Personal Access Token
def gitlabToken = "YOUR_GITLAB_TOKEN"
def gitlabUsername = "oauth2"  // For GitLab, username can be 'oauth2' when using token

def credentials = new UsernamePasswordCredentialsImpl(
    CredentialsScope.GLOBAL,
    credentialsId,
    "GitLab Personal Access Token for casino-app repository",
    gitlabUsername,
    gitlabToken
)

// Add credentials to Jenkins
store.addCredentials(domain, credentials)
jenkins.save()

println "✅ GitLab credentials '${credentialsId}' created"
println "📋 Username: ${gitlabUsername}"
println "🔑 Token: [PROTECTED]"
println ""
println "⚠️  IMPORTANT: To access the private GitLab repository, you need to:"
println "1. Go to GitLab -> Settings -> Access Tokens"
println "2. Create a Personal Access Token with 'read_repository' scope"
println "3. Update Jenkins credentials with the actual token"
println "4. Or update the config.xml file with proper credentials"
println ""
println "🔧 Alternative: Create a GitLab Deploy Token:"
println "1. Go to Project -> Settings -> Repository -> Deploy Tokens"
println "2. Create a deploy token with 'read_repository' scope"
println "3. Use the deploy token username/password in Jenkins"

// List all credentials to verify
println "\n=== All Credentials ==="
store.getCredentials(domain).each { cred ->
    println "ID: ${cred.id}, Description: ${cred.description}"
}

println "=== GitLab Credentials Setup Complete ==="