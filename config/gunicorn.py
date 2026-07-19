import multiprocessing

# Server socket
bind = "0.0.0.0:8000"

# Workers (scale automatically based on CPU)
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class
worker_class = "sync"

# Worker connections
worker_connections = 1000

# Max requests
max_requests = 1000
max_requests_jitter = 50

# Timeout and keepalive tuned to align with nginx proxy_read_timeout (60s)
timeout = 65
keepalive = 5

# Use shared memory for worker temp files to avoid disk I/O bottlenecks
worker_tmp_dir = "/dev/shm"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "4work-[%(proc_num)s]"

preload_app = True
