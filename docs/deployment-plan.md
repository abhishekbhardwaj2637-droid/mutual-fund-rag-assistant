# Deployment Plan: Mutual Fund FAQ Assistant (RAG Pipeline)

This document details the production deployment strategies for the Mutual Fund FAQ Assistant. The assistant consists of two primary components:
1. **Ingestion Daemon (Scheduler & Scraper)**: Crawls data daily and updates the vector database.
2. **Streamlit UI (Fact Finder Dashboard)**: Serves the glassmorphic chatbot interface.

---

## 📋 Deployment Requirements & Prerequisites

### Server Specifications
- **Operating System**: Windows Server 2019+ or Linux (Ubuntu 22.04 LTS recommended)
- **CPU**: Dual-core CPU (minimum), Quad-core CPU (recommended for concurrent embeddings)
- **RAM**: 4 GB RAM (minimum), 8 GB RAM (recommended to hold BGE SentenceTransformer in memory cache)
- **Storage**: 10 GB SSD space (growth depends on document storage and scraping size)

### Required Software
- Python 3.10 or 3.11 (Python 3.12+ compatible)
- Git (for repository synchronization)
- Reverse Proxy (IIS for Windows, Nginx for Linux)
- SSL Certificate (domain configuration)

---

## 🏢 Option 1: Local / On-Premise Windows Server Deployment (Recommended)

Since the system was designed with a native Windows Task Scheduler script, deploying on Windows Server is the most straightforward on-premise approach.

### Step 1: Clone and Environment Setup
1. Clone the repository to your server:
   ```powershell
   git clone https://github.com/abhishekbhardwaj2637-droid/mutual-fund-rag-assistant.git D:\Apps\mutual-fund-rag-assistant
   ```
2. Set up a dedicated virtual environment:
   ```powershell
   cd D:\Apps\mutual-fund-rag-assistant
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Create a production `.env` file containing API keys and absolute file paths:
   ```env
   GEMINI_API_KEY=your_production_gemini_key
   OPENAI_API_KEY=your_production_openai_key
   VECTOR_DB_DIR=D:/Apps/mutual-fund-rag-assistant/data/vectordb
   DATA_RAW_DIR=D:/Apps/mutual-fund-rag-assistant/data/raw
   DATA_PROCESSED_DIR=D:/Apps/mutual-fund-rag-assistant/data/processed
   CURATED_AMC=HDFC
   ```

### Step 2: Automate Daily Ingestion Scheduler
Register the daily crawlers to update database metrics every day at 10:00 AM IST:
1. Open PowerShell as an **Administrator**.
2. Run the registration script:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force
   .\setup_scheduler.ps1
   ```
3. Open **Windows Task Scheduler** and confirm that `MutualFundFAQ_IngestionPipeline` is active and configured to run under a persistent system account (e.g., `NT AUTHORITY\SYSTEM` or a dedicated service user with log-on-as-service permissions).

### Step 3: Run Streamlit as a Windows Background Service
To ensure the web dashboard stays running in the background and launches automatically on system boot, use **NSSM (Non-Sucking Service Manager)**:
1. Download NSSM from [nssm.cc](https://nssm.cc/) and add it to your System PATH.
2. Open Command Prompt as an Administrator and install the service:
   ```cmd
   nssm install MintFlowAssistant
   ```
3. In the GUI panel, configure the following:
   - **Path**: `D:\Apps\mutual-fund-rag-assistant\.venv\Scripts\python.exe`
   - **Startup directory**: `D:\Apps\mutual-fund-rag-assistant`
   - **Arguments**: `-m streamlit run app.py --server.port 8599 --server.address 127.0.0.1`
4. Set the **Startup type** to `Automatic` and click **Install service**.
5. Start the service:
   ```cmd
   nssm start MintFlowAssistant
   ```

### Step 4: IIS Reverse Proxy & SSL Setup
To expose the app securely over HTTPS (port 443):
1. Install **IIS** with the **Application Request Routing (ARR)** and **URL Rewrite** extensions.
2. Enable Proxy in ARR: Open IIS Manager -> Server Node -> **Application Request Routing Cache** -> **Server Settings** -> Check **Enable proxy**.
3. Create a new IIS website bound to your target domain (e.g., `mintflow.yourdomain.com`).
4. Add a **URL Rewrite Rule** on the website:
   - **Match URL pattern**: `(.*)`
   - **Rewrite URL**: `http://localhost:8599/{R:1}`
5. Request and install an SSL certificate via **Let's Encrypt** (using [wacs.exe](https://www.win-acme.com/)) to bind port 443 automatically.

---

## ☁️ Option 2: Linux Cloud VM Deployment (AWS / Azure / DigitalOcean)

Exposing the dashboard on a Linux Ubuntu instance.

### Step 1: Environment Setup
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git nginx -y

# Clone repo
git clone https://github.com/abhishekbhardwaj2637-droid/mutual-fund-rag-assistant.git /var/www/mutual-fund-rag-assistant
cd /var/www/mutual-fund-rag-assistant

# Virtual Environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Systemd Service Configuration
Create a background service file for Streamlit:
```bash
sudo nano /etc/systemd/system/mintflow.service
```
Paste the configuration:
```ini
[Unit]
Description=MintFlow Mutual Fund FAQ Assistant Streamlit Server
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/mutual-fund-rag-assistant
ExecStart=/var/www/mutual-fund-rag-assistant/.venv/bin/python -m streamlit run app.py --server.port 8599 --server.address 127.0.0.1
Restart=always

[Install]
WantedBy=multi-user.target
```
Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mintflow.service
sudo systemctl start mintflow.service
```

### Step 3: Cron Ingestion Automation
Run the crawlers daily at 10:00 AM IST (4:30 AM UTC):
```bash
sudo crontab -e
```
Add the cron line at the bottom:
```text
30 4 * * * cd /var/www/mutual-fund-rag-assistant && /var/www/mutual-fund-rag-assistant/.venv/bin/python ingestion/run_pipeline.py >> /var/log/mutual-fund-pipeline.log 2>&1
```

### Step 4: Nginx Reverse Proxy with SSL
Create an Nginx configuration file:
```bash
sudo nano /etc/nginx/sites-available/mintflow
```
Configuration:
```nginx
server {
    listen 80;
    server_name mintflow.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8599;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Enable the site and obtain SSL credentials:
```bash
sudo ln -s /etc/nginx/sites-available/mintflow /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Install SSL Certificate
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d mintflow.yourdomain.com
```

---

## ⚡ Option 3: PaaS Deployments (Streamlit Community Cloud / Render)

For rapid, serverless testing:
1. Link your GitHub repository to your **Streamlit Community Cloud** account.
2. Deploy the app specifying the entrypoint: `app.py`.
3. In **Secrets settings**, configure the API keys:
   ```toml
   GEMINI_API_KEY = "your_key"
   OPENAI_API_KEY = "your_key"
   ```
4. **Note on Persistence**: PaaS hosting does not persist local databases across spins. The app will fetch fresh HTML documents and index them to ChromaDB at startup or run in fallback, but for production persistence, Option 1, 2, or 4 is strongly recommended.

---

## 🚂 Option 4: Railway Cloud Deployment (Recommended for Persistence)

Railway offers a great balance between PaaS simplicity and persistent infrastructure, making it ideal for the RAG pipeline since we can persist our Vector DB.

### Prerequisites
1. Push your repository to GitHub.
2. Ensure you have a `railway.json` file in the root (already included in this project) which instructs Railway on how to build and run the Streamlit app.

### Deployment Steps
1. **Create Project**: Go to [Railway.app](https://railway.app), click **New Project** -> **Deploy from GitHub repo**, and select your repository.
2. **Add Environment Variables**: Once the service is created, go to the **Variables** tab and add:
   - `GEMINI_API_KEY` = your_key
   - `OPENAI_API_KEY` = your_key
3. **Configure Persistent Volume**: This is **critical** to prevent the Vector Database from being wiped:
   - Go to the **Volumes** tab in your Railway service settings.
   - Click **Create Volume** (e.g., name it `mintflow-data`).
   - Set the **Mount Path** to `/app/data`.
   - Now, the Vector Database stored in `data/vectordb` will persist across deploys and server restarts.
4. **Deploy**: Railway will automatically use Nixpacks to install Python dependencies from `requirements.txt` and use the `startCommand` defined in `railway.json` to launch the app.
5. **(Optional) Automated Ingestion**: To automate daily data ingestion on Railway, you can create a second service within the same Railway project using a basic Cron job, or manually run `python ingestion/run_pipeline.py` using the Railway CLI.
