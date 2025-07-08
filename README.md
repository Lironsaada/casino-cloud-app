# 🎰 Casino Cloud App 🎰

A fun, Flask-based casino application running in a Kubernetes environment. Includes Blackjack, Roulette, and Slot Machine games, with persistent user balances, tipping system, and an admin panel.

---

## 🚀 Features

- 🎲 Games: Blackjack, Roulette, Slots
- 👤 User accounts with password & balance
- 💰 Tipping between users
- 🛠 Admin panel for changing balances
- 🧠 Memory persistence via PVC and `users.json`
- �� Dockerized & Kubernetes-ready

---

🗂 Directory Structure

casino-cloud-app/
├── app/                     
│   ├── app.py              
│   ├── blackjack.py        
│   ├── roulette.py         
│   ├── slots.py            
│   ├── templates/          
│   └── users.json       
│
├── infra/
│   ├──   k8s               
│   │     ├── deployment.yaml
│   │     ├── service.yaml
│   │     ├── configmap.yaml
│   │     └── pvc.yaml
│   │   
│   │└── main.tf
│   │ └── outputs.tf
│   │ └── provider.tf
│   │ └── variables.tf
│
├── requirements.txt      
├── Dockerfile           
└── README.md             

---

## 🧪 Running Locally (Dev)

```bash
git clone https://github.com/lironsaada/casino-cloud-app.git
cd casino-cloud-app

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd app
python app.py
App will run on http://localhost:5000.

🐳 Docker Build & Run
bash
Copy
docker build -t lironsaada/casino-app:latest .
docker run -p 5000:5000 lironsaada/casino-app:latest
☸️ Kubernetes Deployment
Make sure your cluster is running.

Apply the Kubernetes manifests:

bash
Copy
kubectl apply -f infra/k8s/
Port-forward to access the app:

bash
Copy
kubectl port-forward svc/casino-service 8080:80
Then open http://localhost:8080

🔒 Admin Password
Default admin password: 12345

⚠️ Notes
The app uses /data/users.json for persistent balances.

Admin and tipping are accessible after login.

Monitoring integration (Prometheus & Grafana) attempted but currently disabled.

📦 Image Repository
Docker Hub - lironsaada/casino-app

✨ Todo
 Add Azure infra via Terraform

 Optional: Finish Prometheus/Grafana metrics

 Improve game UI with Bootstrap

🧑‍💻 Built By
Liron Saada
