ROLE: You are a senior Jenkins + Helm + ArgoCD engineer.
OUTPUT RULE: Return only the requested files as fenced code blocks with the file path in the code fence info string (e.g., ```groovy:Jenkinsfile). No extra prose.

Goal
Create a single Multibranch Jenkinsfile (at repo root) that implements three pipelines using Helm:

PIPE-01 (feature branches):

Build Docker image (no push).

Run unit tests (Python → pytest).

helm lint and helm template against the app chart.

Post-build: notify Slack/Discord on failures only.

Email: notify on failures and on back-to-green (aka “back from failure”) to managers and the committer.

PIPE-02 (main branch):

Build Docker image.

Run unit tests (pytest).

helm lint + helm template.

helm package the chart.

Push Docker image to Docker Hub.

Push Helm package to Docker Hub (OCI).

Post-build: notify Slack/Discord on failures only.

Email: notify on failures and on back-to-green.

PIPE-03 (CD / GitOps, dev env):

Implement GitOps with Argo CD.

Jenkins updates the image tag in environments/dev/values.yaml, commits to branch release/dev, pushes, and (optionally) opens an MR to main. ArgoCD syncs (no kubectl apply in Jenkins).

Assumptions & fixed IDs (do not change)
Registry & repos:
REGISTRY=docker.io
IMAGE_REPO=your-dockerhub-username/your-app

Helm chart path: helm/app/

Env values path: environments/<env>/values.yaml (dev/staging/prod)

K8s placeholders: KUBE_CONTEXT=your-kube-context, KUBE_NAMESPACE=your-namespace

Git URL placeholder: https://example.com/your/repo.git

Credentials (IDs must match exactly):

DockerHub: dockerhub-creds (username/password or token)

Git PAT (for pushing release branches / MRs): git-creds (Secret text)

Secrets (as Jenkins “Secret text” credentials or string params):

Slack or Discord webhook: chat-webhook

Email recipients (edit placeholders but keep variables):
Managers: managers@example.com
Developer: ${env.CHANGE_AUTHOR_EMAIL ?: env.GIT_COMMITTER_EMAIL ?: 'dev@example.com'}

Behavior details (must implement exactly)
Multibranch compatible: same Jenkinsfile works for feature and main.

Branch detection:

Feature = any branch not main.

Main = branch main.

Python test discovery: run pytest and publish JUnit (**/reports/junit-*.xml) with allowEmptyResults: true.

Helm steps (feature + main):

helm lint helm/app

helm template test-render helm/app -f environments/dev/values.yaml (render check)

Helm package (main only):

helm package helm/app --destination dist/helm

Push Helm package to Docker Hub (OCI):

Use OCI workflow (export HELM_EXPERIMENTAL_OCI=1)

helm registry login $REGISTRY with DockerHub creds

helm push dist/helm/app-*.tgz oci://docker.io/your-dockerhub-username/helm

Docker image tagging (main):

Tag ${YYYYMMDD}-${shortsha} and latest

GitOps (PIPE-03 dev):

Param DEPLOY_ENV ∈ ['', 'dev','staging','prod'] (CD triggers only if set; scope: dev required)

Param IMAGE_TAG optional; default to ${YYYYMMDD}-${shortsha} of current build if empty

For prod, require input confirmation; for this task implement dev only.

Modify environments/dev/values.yaml: set .image.tag = "<tag>"

Commit on branch release/dev and push with git-creds

(Optional comment) “MR to main required” — include curl template for Git provider API with placeholders

Notifications:

Slack/Discord: send only on FAILURE using chat-webhook. Include job name, branch, build URL, and last 50 lines of log.

Email: send on FAILURE and BACK TO NORMAL (previous build not SUCCESS, current SUCCESS) using emailext.

Plugin policy: Do not install plugins from the pipeline. Add a check stage that verifies required plugins and fails fast with a clear list if missing.

Deliverables (output exactly these files, in this order)
groovy:Jenkinsfile
Copy
Edit
text:jenkins/plugins.txt
Copy
Edit
makefile:Makefile
Copy
Edit
yaml:helm/app/Chart.yaml
Copy
Edit
yaml:helm/app/values.yaml
Copy
Edit
yaml:helm/app/templates/deployment.yaml
Copy
Edit
yaml:helm/app/templates/service.yaml
Copy
Edit
yaml:environments/dev/values.yaml
Copy
Edit
ini:pytest.ini
Copy
Edit
text:requirements.txt
Copy
Edit
python:app/main.py
Copy
Edit
File specifications
Jenkinsfile
options { timestamps(); ansiColor('xterm'); buildDiscarder(logRotator(numToKeepStr: '30')); timeout(time: 60, unit: 'MINUTES') }

parameters { choice(name: 'DEPLOY_ENV', choices: ['', 'dev','staging','prod']); string(name: 'IMAGE_TAG', defaultValue: '') }

Environment: REGISTRY, IMAGE_REPO

Required plugins list: workflow-aggregator, git, git-client, credentials, credentials-binding, pipeline-utility-steps, ssh-agent, docker-workflow, mailer, email-ext

Stages:

Verify plugins (check only, no install; fail with list if missing)

Checkout

Setup Python (use system Python or container; ensure pip install -r requirements.txt)

Lint & Test (pytest, write JUnit to reports/)

Build Image (docker build -t ${IMAGE_REPO}:${TAG} .)

Helm Lint/Template (as above)

Main-only: Login + Push image + helm package + helm push (OCI)

CD (when DEPLOY_ENV == 'dev'): bump environments/dev/values.yaml .image.tag, commit & push release/dev with git-creds

Tagging logic: shortSha=$(git rev-parse --short=7 HEAD); dateTag=$(date +%Y%m%d); TAG="${dateTag}-${shortSha}"

Post:

failure { send Slack/Discord webhook payload + emailext to managers + developer }

success { if previous not SUCCESS → emailext “back to normal” }

always { junit publish; cleanWs() }

jenkins/plugins.txt
Pin stable versions (no latest):
workflow-aggregator, git, git-client, credentials, credentials-binding, pipeline-utility-steps, ssh-agent, docker-workflow, mailer, email-ext

Makefile
Targets used by pipeline:

lint (optional placeholder)

test → run pytest -q --junitxml=reports/junit-results.xml

image → docker build -t $(IMAGE) .

helm-lint → helm lint helm/app

helm-template → helm template test-render helm/app -f environments/dev/values.yaml

helm-package → helm package helm/app -d dist/helm

helm-push (OCI) → export HELM_EXPERIMENTAL_OCI=1; login and helm push dist/helm/*.tgz oci://docker.io/your-dockerhub-username/helm

Helm chart (minimal runnable)
Chart.yaml, values.yaml, templates/deployment.yaml, templates/service.yaml
Deployment uses:

image: {{ .Values.image.repository }}:{{ .Values.image.tag }}

probes on /healthz

namespace via release (no hardcode)

values.yaml contains:

yaml
Copy
Edit
image:
  repository: your-dockerhub-username/your-app
  tag: latest
  pullPolicy: IfNotPresent
service:
  type: ClusterIP
  port: 8000
environments/dev/values.yaml
Override at least .image.tag: dev-PLACEHOLDER

pytest.ini, requirements.txt, app/main.py
Minimal Flask app with /healthz returning 200.

pytest single test for /healthz.

Acceptance checklist (must self-verify before printing)
One Jenkinsfile implements PIPE-01, PIPE-02, PIPE-03(dev GitOps) exactly as described.

Helm steps present in both pipelines; package + OCI push only on main.

Slack/Discord only on failures; email on failures and back-to-green.

Plugins pinned in jenkins/plugins.txt.

All 11 files emitted, paths correct, no extra text.
