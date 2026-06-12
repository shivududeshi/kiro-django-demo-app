# Gunicorn configuration for production
# Reference: https://docs.gunicorn.org/en/stable/configure.html

import multiprocessing

# Bind to Unix socket — Nginx will proxy to this
bind = "unix:/tmp/panorbit.sock"

# Number of worker processes (2 x CPU cores + 1 is standard)
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class
worker_class = "sync"

# Timeout (seconds)
timeout = 120

# Logging
accesslog = "/var/log/panorbit/access.log"
errorlog  = "/var/log/panorbit/error.log"
loglevel  = "info"

# Process name
proc_name = "panorbit"
