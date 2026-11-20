import logging
import sys
import json
from app.core.request_context import request_id_ctx
from app.core.config import settings

logger = logging.getLogger("assistant")

logger.setLevel(logging.INFO)

def log_json(**kwargs):
    request_id = request_id_ctx.get(None)
    if request_id is not None:
        kwargs.setdefault(
            "request_id", request_id
        )
    logger.info(
        json.dumps(kwargs)
    )

def log_exception(exception: Exception, **kwargs):
    kwargs["event"] = "exception"
    kwargs["error"] = type(exception).__name__
    kwargs["message"] = str(exception)

    log_json(**kwargs)

def log_debug(**kwargs):
    if settings.DEBUG:
        log_json(
            level = "DEBUG",
            **kwargs
        )

def log_info(**kwargs):
    log_json(
        level = "INFO",
        **kwargs
    )

handler = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter(
    "%(message)s"
)

handler.setFormatter(formatter)

logger.handlers.clear()
logger.addHandler(handler)
logger.propagate = False
