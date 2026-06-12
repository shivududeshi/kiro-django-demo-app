# Jenkins CI/CD Setup Guide — kiro-django-demo-app

## Prerequisites (one-time server setup)

> **Important:** The Jenkins agent must be configured to run as the `ubuntu` user.
> All deployment commands run directly as `ubuntu` — no `sudo`, no separate jenkins user.

Run these commands on the Ubuntu server **before** the first Jenkins build.

```bash
# 1. Create the app directory (ubuntu already owns it)
sudo mkdir -p /var/www/kiro-django-demo-app
sudo chown -R ubuntu:ubuntu /var/www/kiro-django-demo-app

# 2. Install the systemd service
sudo cp deploy/kiro-django-demo-app.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable kiro-django-demo-app

# 3. Allow ubuntu to manage the app service without a password prompt
sudo tee /etc/sudoers.d/ubuntu-service > /dev/null <<'EOF'
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl restart kiro-django-demo-app, /bin/systemctl is-active kiro-django-demo-app, /bin/systemctl status kiro-django-demo-app
EOF
```

---

## Step 1 — Add SSH Credential

1. Go to **Manage Jenkins → Credentials → System → Global credentials**
2. Click **Add Credentials**
3. Fill in:
   - Kind: `SSH Username with private key`
   - ID: `jenkins-agent-ssh-key`
   - Username: `ubuntu`
   - Private Key: paste the private key for the ubuntu user
4. Click **Save**

---

## Step 2 — Create the Pipeline Job

1. Click **New Item**
2. Enter name: `kiro-django-demo-app`
3. Select **Pipeline** → click **OK**

---

## Step 3 — Configure the Job

In the job configuration page:

### General
- ✅ Check **GitHub project**
- Project URL: `https://github.com/shivududeshi/kiro-django-demo-app`

### Pipeline
- Definition: **Pipeline script from SCM**
- SCM: **Git**
- Repository URL: `https://github.com/shivududeshi/kiro-django-demo-app`
- Branch: `*/master`
- Script Path: `Jenkinsfile`

Click **Save**

---

## Step 4 — Run the Build

1. Click **Build Now**
2. Click the build number → **Console Output** to watch live

---

## Expected Console Output

```
>>> Checking out source code from GitHub...
>>> Creating virtual environment...
>>> Installing requirements...
>>> Running Django system check...
System check identified no issues (0 silenced).
>>> [1/4] Copying code to /var/www/kiro-django-demo-app...
>>> [2/4] Installing dependencies...
>>> [3/4] Restarting application service...
>>> [4/4] Verifying application is running...
✅ Service kiro-django-demo-app is running
>>> Deployment complete — app accessible at http://<server-ip>:8000
```

Build result: **SUCCESS** ✅

---

## Demo Success Checklist

| # | Check | How to verify |
|---|-------|---------------|
| 1 | Code checked out from GitHub | Stage `get_code` shows green |
| 2 | Virtual environment created | Stage `build` shows green |
| 3 | Dependencies installed | Stage `build` shows green |
| 4 | App deployed | Stage `deploy` shows green |
| 5 | App accessible on port 8000 | `curl http://<server-ip>:8000` returns HTML |
| 6 | Build shows SUCCESS | Jenkins dashboard shows blue/green ball |

---

## Troubleshooting

**Service fails to start**
```bash
sudo systemctl status kiro-django-demo-app
sudo journalctl -u kiro-django-demo-app -n 50
```

**Permission denied on rsync/systemctl**
```bash
# Verify sudoers entry is correct
sudo visudo -f /etc/sudoers.d/jenkins-deploy
```

**Django check fails**
```bash
# Run manually to see the error
cd /var/www/kiro-django-demo-app
./envs/bin/python manage.py check
```
