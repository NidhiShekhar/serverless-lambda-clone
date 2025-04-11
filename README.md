# Serverless Lambda Execution Platform — Project Overview 

## What is this project?

This project is an open-source re-creation of AWS Lambda's core idea — a platform where users can:
- Upload code (Python / JavaScript)
- Execute that code in isolated environments (like Docker containers or MicroVMs)
- Track execution results, performance, and failures
- Monitor everything live with dashboards


---

## Tech Stack :

| Technology | Purpose | Why this? |
|-----------|---------|-----------|
|FastAPI (Python)| REST API backend | Lightweight, async, Python-native |
|Streamlit (Python)| Web UI for user interaction | fast to build |
|PostgreSQL| Stores function code & execution history | Reliable relational DB, SQL, clean querying |
|Docker| Containerize function execution | Isolation, security, AWS Lambda style |
|Firecracker| MicroVM execution | Real AWS Lambda-like isolation |
|Prometheus| Metrics collection | Time-series monitoring, standard tool |
|Grafana| Live dashboards | Visualization of Prometheus data |
|Docker Compose| Running the whole stack | Easy multi-container orchestration |
|SQLAlchemy| ORM for PostgreSQL | Safe, clean DB queries from Python |

---

## What exactly will this system do?

### User Flow:
1. User goes to Streamlit UI
2. Uploads Python or JS code
3. Chooses language, timeout
4. Hits Deploy

---

### Execution Flow:
1. FastAPI stores the function in PostgreSQL
2. On Execution request → FastAPI runs function:
   - Inside a Docker container (Python or JS image)
   - Or inside Firecracker MicroVM
3. Tracks:
   - Execution Time
   - Success / Failure
   - Output / Error logs
4. Exposes metrics at `/metrics` endpoint (Prometheus friendly)

---

### Monitoring Flow:
- Prometheus scrapes FastAPI metrics
- Grafana visualizes:
   - Execution time per function
   - Error rates
   - Success vs Failures
   - API latency
   - Resource Usage (Optional)

---



## Expected Output of the System:

| Component | Outcome |
|-----------|---------|
|API | Users can create, view, update, execute functions |
|Execution Engine | Each function runs isolated in a container |
|Monitoring | Live Grafana Dashboard showing execution metrics |
|Database | Logs all functions & their execution history |
|UI | Streamlit dashboard  |

---

## What makes this project cool?
- Realistic cloud-like architecture
- End-to-end production-style workflow
- Isolation of user code execution (secure)
- Live observability (like AWS CloudWatch dashboards)
- Ready for future additions like auto-scaling, JWT Auth, Multi-language support

---

## Tools used beyond coding:
- VSCode (for infra files: Prometheus, Grafana, Docker)
- PyCharm (for backend Python development)
- Git + GitHub (version control)
- Docker Compose (one command deploy)

---

## Future Scope:
- Authentication (JWT based)
- Autoscaling executor pool
- Billing / Cost Estimation logic
- Multi-language support beyond Python & JS
- Deploy to a Cloud Provider (AWS/GCP)
- Firecracker deeper integration & performance benchmarks
- Async Execution handling

---

GitHub: [https://github.com/your-username/serverless-lambda-clone](https://github.com/your-username/serverless-lambda-clone)


## High-Level Architecture:

                                    +---------------------------+
                                    |      User (Streamlit UI)  |
                                    +---------------------------+
                                                 |
                                                 |
                                                 v
                                   +--------------------------------+
                                   |         FastAPI Backend        |
                                   |   - Function CRUD API          |
                                   |   - Execution API              |
                                   |   - Prometheus /metrics        |
                                   +--------------------------------+
                                                 |
                   +-----------------------------+------------------------------+
                   |                                                            |
                   v                                                            v
     +-----------------------------+                             +--------------------------------+
     |    PostgreSQL Database      |                             |     Execution Engine            |
     | - Store Function Metadata   |                             | - Docker Containers             |
     | - Execution History         |                             | - Firecracker MicroVM (Optional)|
     +-----------------------------+                             +--------------------------------+
                                                                                   |
                                                                                   |
                                                                                   v
                                                                      +-----------------------------+
                                                                      |   Prometheus Metrics Export  |
                                                                      +-----------------------------+
                                                                                   |
                                                                                   v
                                                                      +-----------------------------+
                                                                      |      Prometheus Server      |
                                                                      | (Scrapes /metrics from API) |
                                                                      +-----------------------------+
                                                                                   |
                                                                                   v
                                                                      +-----------------------------+
                                                                      |        Grafana Dashboard    |
                                                                      | (Visualizes Execution Data) |
                                                                      +-----------------------------+
