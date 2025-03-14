import ast
from functools import wraps
from typing import Callable, Any, Tuple

from utils.logs.log_control import LOG


def log_decorator(log_enabled: bool):
    """Decorator to log request and response information."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Tuple[Any, Any]:
            res, req = func(*args, **kwargs)
            if log_enabled:
                log_message = (
                    f"\n======================================================\n"
                    f"用例标题: {req.get("description")}\n"
                    f"请求路径: {req.get("url")}\n"
                    f"请求方式: {req.get("method")}\n"
                    f"请求头:   {req.get("headers")}\n"
                    f"请求内容: {req.get("data")}\n"
                    f"接口响应内容: {res}\n"
                    "====================================================="
                )
                is_run = req.get("is_run")
                # 判断正常打印的日志，控制台输出绿色
                if is_run in (True, None):
                    LOG.info(log_message)
                else:
                    # 失败的用例，控制台打印红色
                    LOG.error(log_message)
            return res, req

        return wrapper

    return decorator
