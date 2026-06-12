# Python 3.12 Migration Assessment Report

**Project:** simple-django-project (kiro-django-demo-app)  
**Migration:** Python 3.7.2 / Django 1.11.29 → Python 3.12.x / Django 4.2.13 LTS  
**Date:** June 2026

---

## 1. Environment Analysis

### Current State
| Item | Version |
|---|---|
| Python | 3.7.2 |
| Django | 1.11.29 (EOL: April 2020) |
| Database | MySQL via mysqlclient / PyMySQL |
| Search | django-haystack + Whoosh |

### Target State
| Item | Version |
|---|---|
| Python | 3.12.x |
| Django | 4.2.13 (LTS, supported until April 2026) |
| Database | MySQL via mysqlclient 2.2.4 / PyMySQL 1.1.1 |
| Search | django-haystack 3.3.0 + Whoosh 2.7.4 |

---

## 2. Dependency Compatibility Matrix

| Package | Old Version | New Version | Status | Reason |
|---|---|---|---|---|
| Django | 1.11.29 | 4.2.13 | 🔴 **Breaking** | EOL, `url()` removed, many deprecations |
| mysqlclient | 1.4.2.post1 | 2.2.4 | 🔴 **Breaking** | Won't compile on Py 3.12 |
| django-haystack | 2.8.1 | 3.3.0 | 🔴 **Breaking** | Incompatible with Django 4.x |
| django-phonenumber-field | 2.2.0 | 7.3.0 | 🔴 **Breaking** | Incompatible with Django 4.x |
| cryptography | 2.5 | 42.0.8 | 🔴 **Breaking** | Won't build on Py 3.12 |
| PyMySQL | 0.9.3 | 1.1.1 | 🟡 **Upgrade** | Old, minor incompatibilities |
| requests | 2.21.0 | 2.32.3 | 🟡 **Upgrade** | Security fixes |
| urllib3 | 1.24.2 | 2.2.2 | 🟡 **Upgrade** | API changes in v2 |
| PyJWT | 1.7.1 | 2.8.0 | 🟡 **Upgrade** | API changed in v2 |
| phonenumbers | 8.10.6 | 8.13.39 | 🟡 **Upgrade** | Data updates |
| pytz | 2018.7 | 2024.1 | 🟡 **Upgrade** | Timezone data |
| lxml | 4.2.5 | 5.2.2 | 🟡 **Upgrade** | Py 3.12 wheels available |
| openpyxl | 2.5.12 | 3.1.5 | 🟡 **Upgrade** | API updates |
| Whoosh | 2.7.4 | 2.7.4 | 🟢 **Keep** | Still compatible |
| enum34 | 1.1.6 | **REMOVED** | 🔴 **Breaks Py 3.12** | Python 2 backport |
| six | 1.11.0 | **REMOVED** | 🟡 **Unnecessary** | Py 2/3 shim |
| future | 0.17.1 | **REMOVED** | 🟡 **Unnecessary** | Py 2/3 shim |
| configparser | 3.7.3 | **REMOVED** | 🔴 **Breaks Py 3.12** | Python 2 backport |
| pyOpenSSL | 19.0.0 | **REMOVED** | 🟡 **Unused** | Not imported |
| PySocks | 1.6.8 | **REMOVED** | 🟡 **Unused** | Not imported |
| Babel | 2.6.0 | **REMOVED** | 🟡 **Unused** | Not imported |
| protobuf | 3.6.0 | **REMOVED** | 🟡 **Unused** | Not imported |
| xlrd | 1.2.0 | **REMOVED** | 🟡 **Unused** | Not imported |

---

## 3. Code Changes Summary

### `world/models.py`
| Change | Why |
|---|---|
| Removed `from __future__ import unicode_literals` | Python 2 shim, no-op in Py 3, removed for cleanliness |
| Removed unused imports: `AbstractBaseUser`, `UserManager` | Clean up |
| Fixed `TabError` on `__unicode__` method (tab + spaces mixed) | Syntax error in Py 3 |
| Renamed `__unicode__` → `__str__` | `__unicode__` is Python 2 only; Python 3 uses `__str__` |
| Fixed `MyCustomUserManager.normalize_email()` call → `self.normalize_email()` | Class method called via instance is fine but `self` is idiomatic |

### `world/urls.py`
| Change | Why |
|---|---|
| `from django.conf.urls import url` → `from django.urls import path, re_path` | `django.conf.urls.url` removed in Django 4.0 |
| All `url(r'^...$', ...)` → `path('...', ...)` | Modern Django URL routing |
| Country pattern kept as `re_path()` | Contains regex `[\w\W]+` for special chars in country names |

### `panorbit/urls.py`
| Change | Why |
|---|---|
| `from django.conf.urls import url, include` → `from django.urls import path, include` | `django.conf.urls.url` removed in Django 4.0 |
| `url(r'^admin/', ...)` → `path('admin/', ...)` | Modern pattern |

### `panorbit/settings.py`
| Change | Why |
|---|---|
| `from pathlib import Path; BASE_DIR = Path(...).resolve().parent.parent` | Modern Django 3.1+ pattern replacing `os.path` |
| `USE_L10N` removed | Deprecated in Django 4.0, raises `RemovedInDjango50Warning` |
| `DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'` added | Silences Django 3.2+ warning about implicit primary key type |
| Template `DIRS` updated to use `BASE_DIR / 'templates'` | `pathlib` style |
| `STATICFILES_DIRS` updated to use `BASE_DIR / 'static'` | `pathlib` style |

### `manage.py`
| Change | Why |
|---|---|
| Wrapped in `main()` function | Modern Django 3.x+ pattern |
| `raise ImportError(...) from exc` | PEP 3134 exception chaining, proper Py 3 style |
| Removed Python 2 double try/except | Not needed in Py 3 |

---

## 4. Functional Impact Assessment

| Feature | Impact | Notes |
|---|---|---|
| Login / OTP flow | ✅ None | No changes to logic |
| Signup | ✅ None | No changes to logic |
| Search (Haystack + Whoosh) | 🟡 Minor | `rebuild_index` required after upgrade |
| Country detail page | ✅ None | No changes |
| Admin panel | ✅ None | Django admin works the same |
| MySQL connection | 🟡 Minor | PyMySQL 1.1.1 still used via `__init__.py` |
| Static files | ✅ None | Paths updated to pathlib, same behaviour |

---

## 5. Step-by-Step Upgrade Procedure

```bash
# 1. Ensure Python 3.12 is installed
python3.12 --version

# 2. Create fresh virtualenv
virtualenv -p python3.12 envs
source envs/bin/activate

# 3. Install upgraded dependencies
pip install -r requirements.txt

# 4. Set your DB credentials in panorbit/settings.py

# 5. Load world.sql into MySQL (if not already done)
mysql -u root -p < world.sql

# 6. Run migrations
python manage.py migrate

# 7. Rebuild search index
python manage.py rebuild_index

# 8. Run tests
python manage.py test world

# 9. Start server
python manage.py runserver 0:8001
```

---

## 6. Rollback Plan

```bash
# Option A — Git revert
git log --oneline
git checkout <pre-migration-commit-sha>
virtualenv -p python3.7 envs_old
source envs_old/bin/activate
pip install -r requirements.txt   # installs old versions

# Option B — Branch-based
git checkout -b python37-legacy <pre-migration-sha>
```

---

## 7. Known Remaining Warnings (non-breaking)

- `django-haystack 3.3.0` emits a deprecation notice about Whoosh backend on Django 4.2 — functional but noted for future consideration (switch to Elasticsearch or Typesense for production).
- `PyMySQL` still used via `panorbit/__init__.py` `pymysql.install_as_MySQLdb()` — this is intentional as a pure-Python fallback. If `mysqlclient` compiles successfully, `PyMySQL` can be removed from `__init__.py`.
