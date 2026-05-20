# -*- coding: utf-8 -*-
import multiprocessing
import os

bind = "0.0.0.0:" + os.environ.get("PORT", "5000")

# 4 workers or CPU based
workers = int(os.environ.get("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))

timeout = int(os.environ.get("WEB_TIMEOUT", 30))

# Mitigate memory leaks by restarting workers periodically
max_requests = 1000
max_requests_jitter = 50

# Log config (outputs to stdout/stderr for container runtime compatibility)
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Structured JSON Access Log including Flask Request correlation ID
access_log_format = '{"type": "access", "timestamp": "%(t)s", "remote_ip": "%(h)s", "method": "%(m)s", "path": "%(r)s", "status": "%(s)s", "bytes_sent": %(b)s, "duration_ms": %(D)s, "request_id": "%({X-Request-ID}i)s"}'
