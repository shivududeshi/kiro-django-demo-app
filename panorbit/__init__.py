import os

# Install PyMySQL as MySQLdb only when MySQL backend is configured
if os.environ.get('DB_ENGINE', '') != 'django.db.backends.sqlite3':
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass
