"""gunicorn inside the production container, reachable only through Caddy."""

bind = "0.0.0.0:8000"
workers = 2
worker_class = "gthread"
threads = 2
timeout = 30
worker_tmp_dir = "/dev/shm"
control_socket_disable = True

# No access log (URLs can hold reset keys). Error logs use the same allow-listed
# format as Django, because gunicorn's own messages include URLs and IPs.
accesslog = None
logconfig_dict = {
    "formatters": {"safe": {"()": "apps.core.error_reporting.SafeFormatter"}},
    "handlers": {"safe": {"class": "logging.StreamHandler", "formatter": "safe"}},
    "root": {"handlers": ["safe"], "level": "INFO"},
    "loggers": {
        "gunicorn.error": {"handlers": ["safe"], "level": "INFO", "propagate": False},
    },
}
