import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "/var/log/test-automation/access.log"
errorlog = "/var/log/test-automation/error.log"
loglevel = "info"

# Process naming
proc_name = "test-automation"

# SSL
# keyfile = "/path/to/your/ssl.key"
# certfile = "/path/to/your/ssl.cert"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190 