# simple-django-project

> **Python 3.12 / Django 4.2 LTS** — migrated from Python 3.7.2 / Django 1.11.29

## Installation

### Prerequisites

#### 1. Install Python 3.12
Install `python-3.12.x` and `pip`. Follow the steps from the reference document based on your OS.
Reference: [https://docs.python-guide.org/starting/installation/](https://docs.python-guide.org/starting/installation/)

#### 2. Install MySQL
Install `mysql-8.x`. Reference: [https://dev.mysql.com/doc/refman/8.0/en/](https://dev.mysql.com/doc/refman/8.0/en/)

#### 3. Setup virtual environment
```bash
# Install virtual environment
pip install virtualenv

# Create virtual environment
virtualenv -p python3.12 envs

# Activate virtual environment (Linux/macOS)
source envs/bin/activate

# Activate virtual environment (Windows)
envs\Scripts\activate
```

#### 4. Clone git repository
```bash
git clone "https://github.com/shivududeshi/kiro-django-demo-app.git"
cd kiro-django-demo-app
```

#### 5. Install requirements
```bash
pip install -r requirements.txt
```

#### 6. Load sample data into MySQL
```bash
# Open mysql shell
mysql -u <mysql-user> -p

# Give the absolute path of the file
mysql> source ~/kiro-django-demo-app/world.sql
mysql> exit;
```

#### 7. Edit project settings
```bash
# Open settings file
vim panorbit/settings.py

# Edit Database section with your MySQL credentials:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'world',
        'USER': '<mysql-user>',
        'PASSWORD': '<mysql-password>',
        'HOST': '<mysql-host>',
        'PORT': '<mysql-port>',
    }
}

# Edit email section:
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = '<your-email>'
EMAIL_HOST_PASSWORD = '<your-app-password>'
EMAIL_PORT = 587
```

#### 8. Run the server
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Build search index
python manage.py rebuild_index

# Run the server
python manage.py runserver 0:8001
```

Open [http://localhost:8001](http://localhost:8001) in the browser.

### URLs
- **Signup:** http://localhost:8001/signup
- **Login:** http://localhost:8001/login
- **Home / Search:** http://localhost:8001/
- **Country page:** http://localhost:8001/country/kenya
- **Logout:** http://localhost:8001/logout

---

## Python 3.12 Migration Summary

| Change | Old | New |
|---|---|---|
| Python version | 3.7.2 | 3.12.x |
| Django | 1.11.29 | 4.2.13 (LTS) |
| URL routing | `django.conf.urls.url()` | `django.urls.path()` / `re_path()` |
| `mysqlclient` | 1.4.2.post1 | 2.2.4 |
| `django-haystack` | 2.8.1 | 3.3.0 |
| `django-phonenumber-field` | 2.2.0 | 7.3.0 |
| `cryptography` | 2.5 | 42.0.8 |
| `PyMySQL` | 0.9.3 | 1.1.1 |
| `__unicode__` method | Python 2 style | `__str__` (Python 3) |
| `from __future__ import unicode_literals` | Removed (no-op in Py 3) | — |
| `USE_L10N` setting | Deprecated | Removed (defaults True) |
| `BASE_DIR` | `os.path` | `pathlib.Path` |
| `manage.py` | Old-style try/except | Modern `main()` function |
| Removed packages | `enum34`, `six`, `future`, `configparser` | Not needed in Py 3.12 |

## Rollback Plan

If you need to revert to the Python 3.7 / Django 1.11 setup:

```bash
# Checkout the previous commit
git log --oneline       # find the old commit SHA
git checkout <old-sha>

# Recreate old virtualenv
virtualenv -p python3.7 envs_old
source envs_old/bin/activate
pip install -r requirements.txt
```
