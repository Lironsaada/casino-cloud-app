multibranchPipelineJob('app-mbp') {
    displayName('Casino App Multibranch Pipeline')
    description('Multibranch pipeline for casino cloud application')
    
    branchSources {
        git {
            id('casino-app-repo')
            remote('https://example.com/your/repo.git')
            credentialsId('git-creds')
            includes('*')
        }
    }
    
    configure { node ->
        node / 'sources' / 'data' / 'jenkins.branch.BranchSource' / 'source' / 'traits' << {
            'jenkins.plugins.git.traits.BranchDiscoveryTrait' {}
        }
    }
    
    factory {
        workflowBranchProjectFactory {
            scriptPath('Jenkinsfile')
        }
    }
    
    orphanedItemStrategy {
        discardOldItems {
            daysToKeep(30)
            numToKeep(-1)
        }
    }
    
    properties {
        disableConcurrentBuilds()
    }
}