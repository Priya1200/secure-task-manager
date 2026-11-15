# Secure Task Management System with Automated DevOps Pipeline

A task management application built with an intentional focus on the **DevOps automation pipeline** around it rather than the application itself — demonstrating a complete path from source code to a running, scalable, self-healing deployment.

> The application layer is kept simple on purpose. The goal of this project is to demonstrate real-world DevOps practices: version control, CI/CD, containerization, orchestration, configuration management, and infrastructure as code — all wired together and working end-to-end.

---

## Why This Project

- Built for a **DevOps & Automation** course, where the evaluation focuses on the pipeline, not the product.
- The planned security layer (login auditing, failed-attempt logging) ties into a parallel **AI in Cybersecurity** course — the same logs are a natural input for an anomaly-detection model later.
- Uses Supabase (Postgres) for the database, since prior familiarity with it meant more time could go toward learning Docker, Jenkins, Kubernetes, Ansible, and Terraform instead of a new database.

---

## Architecture

```
 Developer
     │  git push
     ▼
 GitHub Repository ──────────────► Jenkins (polls every 5 min)
                                         │
                                         ▼
                         ┌─────────────────────────────┐
                         │   Jenkins Pipeline (CI/CD)   │
                         │  Checkout → Install → Test   │
                         │  → Build → Deploy            │
                         └──────────────┬───────────────┘
                                         ▼
                                  Docker Image
                                  (Dockerfile)
                                         ▼
                         ┌─────────────────────────────┐
                         │   Kubernetes (Minikube)      │
                         │  Deployment → ReplicaSet      │
                         │  → Pods (scalable, rolling    │
                         │    updates, rollback)         │
                         └───────────────────────────────┘

 Alongside the pipeline:
   • Ansible   → configures the server/app environment (idempotent playbooks)
   • Terraform → provisions infrastructure declaratively (Docker provider)
```

**Flow in one line:** code is pushed to GitHub → Jenkins detects the change and runs the pipeline → a Docker image is built → Kubernetes deploys it as a set of replicated, self-healing pods — all without manual intervention.

---

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Source control | **Git / GitHub** | Version history, branching, collaboration |
| CI/CD | **Jenkins** | Automated checkout, test, build, and deploy pipeline |
| Containerization | **Docker** | Packages the app and its dependencies into a portable image |
| Orchestration | **Kubernetes (Minikube)** | Runs, scales, updates, and heals containerized app replicas |
| Configuration management | **Ansible** | Automates and standardizes environment/application setup |
| Infrastructure as Code | **Terraform** | Declaratively provisions and scales infrastructure |
| Application | **Python (Flask)** | Lightweight web API |
| Database | **PostgreSQL (Supabase)** | Managed relational data store |

---

## Repository Structure

```
secure-task-manager/
├── Jenkinsfile                 # CI/CD pipeline definition (pipeline-as-code)
├── README.md
├── .gitignore
├── docker-practice/             # Hardened Dockerfile, Flask app, config/flags.json, tests/
├── docker-storage-network/      # Storage & networking experiment notes
├── monitoring/                  # Prometheus, Node Exporter, Grafana (docker-compose)
├── logging/                     # ELK stack, Logstash pipeline, log generator
├── security/
│   └── scan.sh                  # DevSecOps security gate (exit 0 = pass, 1 = fail)
├── selenium-tests/              # Browser UI tests
├── load-tests/                  # Locust load test
├── k8s/
│   └── deployment.yaml          # Kubernetes Deployment manifest (replicas, image, port)
├── ansible/
│   ├── inventory.ini            # Target node(s)
│   └── playbook.yml             # Automated app/environment configuration
└── terraform/
    └── main.tf                  # Infrastructure as Code (Docker provider)
```

---

## Pipeline Stages (Jenkinsfile)

1. **Checkout** — pulls the latest code from GitHub
2. **Install Dependencies** — installs required Python packages
3. **Run Tests** — runs the pytest unit tests (8 tests: routes, feature flags, missing/corrupt flag file fallback)
4. **Security Scan (DevSecOps)** — runs `security/scan.sh`: pip-audit (dependencies), Bandit (code), Gitleaks (secrets), Trivy (container image). Any finding exits non-zero and **blocks the build**
5. **Build** — builds the Docker image and loads it into the Minikube cluster
6. **Deploy to Kubernetes** — `kubectl apply`, rolling restart, and rollout status verification

Triggered via **SCM polling** (`pollSCM('H/5 * * * *')`) rather than a webhook, since Jenkins runs on a local VM without a publicly reachable URL.

---

## Monitoring, Logging and Testing

| Area | Tools | What it shows |
|---|---|---|
| Monitoring | Prometheus, Node Exporter, Grafana | Live host CPU, memory, disk and network metrics (dashboard ID 1860) |
| Centralized logging | Logstash, Elasticsearch, Kibana (ELK 8.11.3) | Request logs parsed with grok into fields and charted in Kibana |
| DevSecOps | pip-audit, Bandit, Gitleaks, Trivy | Findings fixed; hardened image runs as non-root user; gate verified with a failing negative test |
| Feature flags | `docker-practice/config/flags.json` | Features toggled at runtime with no redeploy; safe defaults on a missing or corrupt file |
| UI testing | Selenium (headless Chromium) | 6 browser checks with flags ON and OFF |
| Load testing | Locust | 50 users: 45.66 req/s, p95 35 ms. 300 users: 260.15 req/s, p95 100 ms. 0 failures |

---

## Kubernetes Deployment Strategy

- **Replicas:** starts at 3, demonstrated scaling both up (→5) and down (→2) via `kubectl scale`
- **Rolling updates:** new pods are started and become `Ready` before old pods are terminated — zero downtime
- **Rollback:** `kubectl rollout undo` reverts to the previous revision if an update causes issues

---

## Configuration Management & Infrastructure as Code

- **Ansible** (`ansible/playbook.yml`): installs and configures a web server, deploys a sample page, and is idempotent — re-running it only changes what's actually out of sync.
- **Terraform** (`terraform/main.tf`): provisions a set of containers from the project's Docker image, with the replica count controlled by a single `count` variable — demonstrating declarative, scalable infrastructure that can be planned, applied, and destroyed cleanly.

---

## Getting Started (local environment)

```bash
# Clone the repo
git clone https://github.com/Priya1200/secure-task-manager.git
cd secure-task-manager

# Build and run the containerized app
cd docker-practice
docker build -t sample-flask-app:1.0 .
docker run -d -p 5000:5000 --name flask-container sample-flask-app:1.0

# Deploy to a local Kubernetes cluster (Minikube)
cd ../k8s
minikube start --driver=docker
kubectl apply -f deployment.yaml
kubectl get pods

# Run the Ansible playbook
cd ../ansible
ansible-playbook -i inventory.ini playbook.yml

# Provision infrastructure with Terraform
cd ../terraform
terraform init
terraform plan
terraform apply -auto-approve
```

---

## Status & Next Steps

This repository currently demonstrates the **DevOps pipeline and infrastructure**, fully working end-to-end. The full application layer (authentication, task CRUD endpoints, audit logging, Supabase integration) is the next phase — the pipeline already tests, scans, builds, deploys and observes whatever is added.

- [x] Git workflow (branching, merging)
- [x] Jenkins CI/CD pipeline (tests, security gate, image build, deploy)
- [x] Docker containerization, storage, and networking
- [x] Kubernetes deployment, scaling, rolling updates, rollback
- [x] Jenkins to Kubernetes continuous deployment
- [x] Ansible configuration automation
- [x] Terraform infrastructure as code
- [x] Monitoring with Prometheus and Grafana
- [x] Centralized logging with the ELK stack
- [x] DevSecOps security gate in the pipeline
- [x] Feature flags, unit tests, Selenium UI tests, Locust load tests
- [ ] Flask application logic (auth, tasks, audit logs)
- [ ] Supabase Postgres integration
- [ ] Live cloud deployment (e.g., Render)

---

## Author

**Priya** — DevOps & Automation coursework
