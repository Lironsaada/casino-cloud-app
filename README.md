# Casino Cloud App

> **⚡ SCM POLLING TEST ACTIVE** - verifying 1-minute automatic build triggers

## Bootstrap Commands

```bash
# Install Jenkins via Helm
helm repo add jenkins https://charts.jenkins.io
helm repo update
kubectl create namespace cicd
helm install jenkins jenkins/jenkins -n cicd -f jenkins/casc/jenkins.yaml --set-file controller.initScripts."plugins\.txt"=jenkins/plugins.txt

# Add credentials (manual via Jenkins UI)
# - dockerhub-creds (username/password)
# - kubeconfig-yourcluster (file)
# - git-creds (PAT if needed)

# Run seed job to create pipeline
kubectl exec -n cicd jenkins-0 -- java -jar /var/jenkins_home/war/WEB-INF/jenkins-cli.jar -s http://localhost:8080 build jenkins/jobs/seed

# Install Argo CD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl apply -f argocd/app-of-apps.yaml

# Apply observability and MongoDB
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
kubectl apply -f k8s/namespaces.yaml
helm install mongodb bitnami/mongodb -n database -f k8s/mongo/helm-values.yaml
helm install kube-prometheus prometheus-community/kube-prometheus-stack -n observability -f monitoring/kube-prometheus-values.yaml
```