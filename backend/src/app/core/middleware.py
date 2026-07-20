import time
import uuid

from sqlalchemy import exc
from fastapi import Request
from app.core.logging import logger
from app.core.request_context import request_id_ctx
from app.core.logger import log_exception

async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())
    token = request_id_ctx.set(request_id)
    try:
        response = await call_next(request)
    
    except Exception as e:
        log_exception(
            e, path = request.url.path, method = request.method
        )
        raise

    finally:
        request_id_ctx.reset(token)
        
    duration = time.perf_counter() - start
    response.headers["X-Request-ID"] = request_id

    logger.info(
        f"{request.method} "
        f"{request.url.path} "
        f"{response.status_code} "
        f"{duration:.3f}s"
    )

    return response