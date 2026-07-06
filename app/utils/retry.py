import asyncio
import httpx
import functools
from typing import Callable, TypeVar, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

T = TypeVar('T')

class SwiggyRetryableError(Exception):
    pass

def is_retryable_error(exception: Exception) -> bool:
    if isinstance(exception, (asyncio.TimeoutError, httpx.TimeoutException)):
        return True

    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code >= 500 or exception.response.status_code in (429, 408)
    
    return isinstance(exception, SwiggyRetryableError)

def retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 1.5,
    retryable_errors: tuple = None
):

    if retryable_errors is None:
        retryable_errors = (Exception,)

    def decorator(func: Callable[...,Any]):
        @retry(
            stop = stop_after_attempt(max_retries),
            wait = wait_exponential(multiplier=1, min=1, max=10),
            retry = retry_if_exception_type(retryable_errors),
            reraise=True,
        )

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return async_wrapper

    return decorator