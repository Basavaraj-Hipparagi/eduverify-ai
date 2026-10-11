# EduVerify AI - Cloud Hosting & Deployment Guide

This guide provides step-by-step instructions to host **EduVerify AI** online so anyone (teachers, evaluators, students, and employers) can access it from their laptops, tablets, or Android phones anywhere in the world.

---

## Deployment Architecture Files in This Project

The repository is already configured with all cloud-native deployment files:

| File | Purpose | Supported Platforms |
| :--- | :--- | :--- |
| `Dockerfile` | Multi-stage production container with Tesseract OCR & OpenCV | Render, Railway, Fly.io, AWS, DigitalOcean |
| `docker-compose.yml` | 1-command container orchestration | Linux VPS, Docker Desktop |
| `Procfile` | WSGI Process definition for cloud buildpacks | Render, Railway, Heroku |
| `render.yaml` | 1-Click Infrastructure-as-Code Blueprint | Render.com |
| `railway.json` | Deployment and health-check configuration | Railway.app |
| `runtime.txt` | Python version lock (`python-3.11.9`) | Cloud Buildpacks |
| `wsgi.py` | Production WSGI entry point | Waitress (Windows), Gunicorn (Linux), cPanel |
| `requirements.txt` | Production dependencies including `gunicorn` and `waitress` | All platforms |

---

## Option 1: Render.com (Recommended — Free & Easy)

Render offers free web service hosting with automatic HTTPS (SSL certificate), which allows the Android PWA app to be installed seamlessly.

### Steps:
1. **Push your project to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for EduVerify AI"
   git branch -M main
   # Link to your GitHub repository
   git remote add origin https://github.com/<your-username>/eduverify-ai.git
   git push -u origin main
   ```

2. **Deploy on Render**:
   - Go to [https://render.com](https://render.com) and log in with GitHub.
   - Click **New +** > **Web Service**.
   - Select **Build and deploy from a Git repository** and connect your `eduverify-ai` repository.
   - In the settings:
     - **Name**: `eduverify-ai`
     - **Region**: Choose the closest region (e.g., Singapore, Frankfurt, Oregon).
     - **Environment**: Select **Docker** (Render will automatically detect `Dockerfile`, ensuring Tesseract OCR is installed!).
     - **Plan**: Select **Free**.
   - Under **Advanced**:
     - Add Environment Variable:
       - `SECRET_KEY`: Enter a random secret key (e.g., `eduverify_prod_sec_2026`).
     - **Health Check Path**: `/api/health`
   - Click **Create Web Service**.

3. **Done!**
   - In 2–3 minutes, Render will build the container and provide a live URL like:
     `https://eduverify-ai.onrender.com`
   - You can share this URL with anyone or open it on your Android phone to install the app!

---

## Option 2: Railway.app

Railway provides ultra-fast deployment directly from GitHub.

### Steps:
1. Push your code to GitHub (as shown above).
2. Go to [https://railway.app](https://railway.app) and sign in.
3. Click **New Project** > **Deploy from GitHub repo**.
4. Select your `eduverify-ai` repository.
5. Railway will automatically read `Dockerfile` and start building.
6. Once deployed, click on the service > **Settings** > **Networking** > **Generate Domain**.
7. Your app is live at `https://eduverify-ai.up.railway.app`!

---

## Option 3: PythonAnywhere (Free Python Hosting)

If you prefer native Python hosting without Docker:

### Steps:
1. Sign up at [https://www.pythonanywhere.com](https://www.pythonanywhere.com).
2. Open a **Bash Console** and clone your repo:
   ```bash
   git clone https://github.com/<your-username>/eduverify-ai.git
   cd eduverify-ai
   pip install --user -r requirements.txt
   ```
3. Go to the **Web** tab:
   - Click **Add a new web app**.
   - Select **Manual configuration** > **Python 3.10** (or 3.11).
   - In **Code**:
     - Source code: `/home/<username>/eduverify-ai`
     - Working directory: `/home/<username>/eduverify-ai`
   - In **WSGI configuration file** (click the link to edit):
     ```python
     import sys
     path = '/home/<username>/eduverify-ai'
     if path not in sys.path:
         sys.path.append(path)
     from app import app as application
     ```
4. Click **Reload <username>.pythonanywhere.com**.
5. Your app is live at `https://<username>.pythonanywhere.com`!

---

## Option 4: Linux VPS (Ubuntu on AWS EC2, DigitalOcean, Linode)

For self-hosting on a custom VPS or institutional server:

### Steps:
1. SSH into your Ubuntu server:
   ```bash
   ssh root@<your-server-ip>
   ```

2. Install system packages:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv git tesseract-ocr libgl1 nginx
   ```

3. Clone and configure:
   ```bash
   git clone https://github.com/<your-username>/eduverify-ai.git /var/www/eduverify
   cd /var/www/eduverify
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt gunicorn
   ```

4. Create systemd service (`/etc/systemd/system/eduverify.service`):
   ```ini
   [Unit]
   Description=EduVerify AI Gunicorn Service
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/eduverify
   Environment="PATH=/var/www/eduverify/venv/bin"
   ExecStart=/var/www/eduverify/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app

   [Install]
   WantedBy=multi-user.target
   ```

5. Start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start eduverify
   sudo systemctl enable eduverify
   ```

6. Configure Nginx reverse proxy with SSL (`certbot`):
   ```nginx
   server {
       server_name yourdomain.com;
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

---

## Option 5: Local Production Mode (Waitress on Windows)

To run in high-performance production mode on your current Windows PC without cloud hosting:

Run the WSGI entrypoint with Waitress:
```powershell
python wsgi.py
```
This serves the application multi-threaded on port 5000 without Flask development server warnings.

---

## Installing the Android App from Cloud URL

Once your application is deployed to any cloud host with HTTPS (e.g., `https://eduverify-ai.onrender.com`):

1. Open the URL in **Google Chrome** on any Android phone.
2. Tap the **Install Mobile App** button on the home screen banner.
3. The app installs immediately to the phone's app drawer with its shield icon and runs in standalone full-screen mode!
