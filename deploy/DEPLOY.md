# Server Deployment Guide

## Prerequisites on the server
- Ubuntu 22.04 / 24.04
- Python 3.12
- MySQL 8
- Nginx

---

## 1. Clone the repo

```bash
cd /var/www
sudo git clone https://github.com/shivududeshi/kiro-django-demo-app.git
sudo chown -R $USER:$USER /var/www/kiro-django-demo-app
cd /var/www/kiro-django-demo-app
```

## 2. Create virtualenv and install packages

```bash
python3.12 -m venv envs
source envs/bin/activate
pip install -r requirements.txt
```

## 3. Create the .env file

```bash
cp .env.example .env
nano .env   # fill in your real values
```

Minimum required values:
```
DJANGO_SECRET_KEY=<generate a long random string>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<your-server-ip or domain>
DB_PASSWORD=<your mysql password>
```

Generate a secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 4. Load the database

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS world CHARACTER SET utf8mb4;"
mysql -u root -p world < world.sql
```

## 5. Run migrations and collect static files

```bash
source envs/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py rebuild_index --noinput
```

## 6. Create log directory

```bash
sudo mkdir -p /var/log/panorbit
sudo chown www-data:www-data /var/log/panorbit
```

## 7. Install systemd service

Edit `deploy/panorbit.service` — replace `/path/to/simple-django-project` with `/var/www/kiro-django-demo-app`

```bash
sudo cp deploy/panorbit.service /etc/systemd/system/panorbit.service
sudo systemctl daemon-reload
sudo systemctl enable panorbit
sudo systemctl start panorbit
sudo systemctl status panorbit    # should show: active (running)
```

## 8. Configure Nginx

Edit `deploy/nginx.conf` — replace:
- `/path/to/simple-django-project` → `/var/www/kiro-django-demo-app`
- `your-domain.com your-server-ip` → your actual domain or IP

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/panorbit
sudo ln -s /etc/nginx/sites-available/panorbit /etc/nginx/sites-enabled/
sudo nginx -t                     # test config — must say "ok"
sudo systemctl reload nginx
```

## 9. Verify

```bash
# Check Gunicorn is running
sudo systemctl status panorbit

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/panorbit/error.log

# Test the app
curl http://your-server-ip/login
```

Open http://your-server-ip in browser. Done.

---

## OTP for demo

For the demo, the OTP is printed to Gunicorn's log (console backend):

```bash
sudo journalctl -u panorbit -f
# or
sudo tail -f /var/log/panorbit/error.log
```

When someone clicks "Send OTP", the code appears in the log. Copy and paste it.

To switch to real email OTP later, set these in `.env`:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```
Then restart: `sudo systemctl restart panorbit`

---

## Useful commands

```bash
# Restart app after code changes
sudo systemctl restart panorbit

# View live logs
sudo journalctl -u panorbit -f

# Check Nginx config
sudo nginx -t

# Reload Nginx (no downtime)
sudo systemctl reload nginx
```
