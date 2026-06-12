# Jenkins Job Setup Guide

Jenkins URL: http://13.201.40.146:8080/

---

## Pre-requisites on the server (run once as ubuntu user)

```bash
# 1. Create app directory
sudo mkdir -p /var/www/kiro-django-demo-app
sudo chown ubuntu:ubuntu /var/www/kiro-django-demo-app

# 2. Create log directory for Gunicorn
sudo mkdir -p /var/log/panorbit
sudo chown ubuntu:ubuntu /var/log/panorbit

# 3. Copy systemd service file
sudo cp /var/www/kiro-django-demo-app/deploy/panorbit.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable panorbit

# 4. Copy Nginx config
sudo cp /var/www/kiro-django-demo-app/deploy/nginx.conf /etc/nginx/sites-available/panorbit
sudo ln -sf /etc/nginx/sites-available/panorbit /etc/nginx/sites-enabled/panorbit
sudo rm -f /etc/nginx/sites-enabled/default   # remove default site
sudo nginx -t
sudo systemctl reload nginx

# 5. Create .env file with real secrets
nano /var/www/kiro-django-demo-app/.env
# Paste contents from .env.example and fill in real values

# 6. Allow ubuntu user to run deploy commands without password prompt
sudo visudo
# Add this line at the bottom:
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl restart panorbit, /bin/systemctl reload nginx, /bin/systemctl status panorbit, /usr/bin/nginx, /bin/mkdir, /bin/chown, /usr/bin/rsync
```

---

## Step 1 — Install required Jenkins plugins

Go to: Jenkins → Manage Jenkins → Plugins → Available

Install:
- **Git plugin** (usually pre-installed)
- **Pipeline** (usually pre-installed)
- **SSH Agent Plugin**
- **Credentials Binding Plugin**

---

## Step 2 — Add SSH credential in Jenkins

Since Jenkins agent IS the deployment server (same node), the pipeline runs
directly on the machine — no SSH needed for deployment.
The `jenkins-agent-ssh-key` credential is used for Jenkins agent connection only.

Go to: Jenkins → Manage Jenkins → Credentials → (global) → Add Credentials

| Field | Value |
|---|---|
| Kind | SSH Username with private key |
| ID | `jenkins-agent-ssh-key` |
| Username | `ubuntu` |
| Private Key | paste the private key content |

---

## Step 3 — Create the Pipeline job

1. Go to: http://13.201.40.146:8080/
2. Click **"New Item"**
3. Enter name: `kiro-django-demo-app`
4. Select **"Pipeline"** → click **OK**

---

## Step 4 — Configure the Pipeline job

### General section
- ✅ Check **"GitHub project"**
- Project URL: `https://github.com/shivududeshi/kiro-django-demo-app`

### Build Triggers section
- ✅ Check **"Poll SCM"**
- Schedule: `H/5 * * * *`  ← checks GitHub every 5 minutes
- OR set up a GitHub webhook (see Step 5)

### Pipeline section
- Definition: **Pipeline script from SCM**
- SCM: **Git**
- Repository URL: `https://github.com/shivududeshi/kiro-django-demo-app`
- Branch: `*/master`
- Script Path: `Jenkinsfile`

Click **Save**.

---

## Step 5 — (Optional) GitHub Webhook for instant builds

Instead of polling, trigger builds instantly on every git push.

1. Go to your GitHub repo → Settings → Webhooks → Add webhook
2. Payload URL: `http://13.201.40.146:8080/github-webhook/`
3. Content type: `application/json`
4. Events: **Just the push event**
5. Click **Add webhook**

In Jenkins job → Build Triggers → ✅ **GitHub hook trigger for GITScm polling**

---

## Step 6 — Run the pipeline

1. Go to job: `kiro-django-demo-app`
2. Click **"Build Now"**
3. Click the build number → **Console Output** to watch live logs

Expected output:
```
>>> Checking out source code from GitHub...   ✅
>>> Dependencies installed successfully        ✅
>>> Running Django system check...             ✅
>>> Deploying application...                   ✅
  [1/6] Syncing code...
  [2/6] Setting ownership...
  [3/6] Installing dependencies...
  [4/6] Running migrations...
  [5/6] Restarting Gunicorn...
  [6/6] Reloading Nginx...
Deployment complete ✅
App running at: http://13.201.40.146
```

---

## Pipeline Flow Summary

```
Git push to master
      ↓
Jenkins detects change (webhook or poll)
      ↓
Stage 1: Get Code    — git checkout from GitHub
      ↓
Stage 2: Build       — pip install, django check, tests
      ↓
Stage 3: Deploy      — rsync code, migrate, collectstatic,
                       restart Gunicorn, reload Nginx
      ↓
App live at http://13.201.40.146
```

---

## Troubleshooting

```bash
# Check Gunicorn status
sudo systemctl status panorbit

# View live app logs
sudo journalctl -u panorbit -f

# Check Nginx config
sudo nginx -t

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Check Gunicorn logs
sudo tail -f /var/log/panorbit/error.log
```
