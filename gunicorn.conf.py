"""
Gunicorn configuration for Roboto SAI
Optimized for high-performance operations with increased resources
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
max_requests = 10000
max_requests_jitter = 1000
timeout = 300  # Increased timeout for heavy initialization
graceful_timeout = 120
keepalive = 5

# Performance tuning
preload_app = False  # Set to False to avoid memory issues during initialization
reuse_port = True
reload = True

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'roboto_sai'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Memory optimization
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190
