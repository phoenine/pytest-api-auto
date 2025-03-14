import time
from typing import Callable, Any

from utils.logs.log_control import LOG


def execution_duration(threshold_ms: int) -> Callable:
    """Decorator to measure the execution duration."""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                start_time = time.perf_counter()
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                run_time_ms = (end_time - start_time) * 1000
                if run_time_ms > threshold_ms:
                    LOG.warning(
                        "\n=================================================================================\n"
                        "测试用例执行时间较长, 请关注.\n"
                        "函数运行时间: {:.2f} ms\n"
                        "测试用例相关数据: {}\n"
                        "=================================================================================".format(
                            run_time_ms, result
                        )
                    )
                return result
            except Exception as e:
                LOG.error("执行 %s 时发生错误: %s", func.__name__, str(e))
                raise

        return wrapper

    return decorator
