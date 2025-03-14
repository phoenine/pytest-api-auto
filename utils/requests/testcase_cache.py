import threading
from typing import List, Any, Text
from jsonpath import jsonpath  # type: ignore
from utils.caches.cache_control import CacheControl
from models.models import StoreCache
from utils.logs.log_control import LOG


class TestcaseCache:
    """ 将用例中的请求或者响应内容存入缓存 """
    def __init__(
        self,
        store_cache: List[StoreCache],
        request_data: Any,
        response_data: Any,
    ):
        self.store_cache = store_cache
        self.request_data = {"data": request_data}
        self.response_data = response_data
        self.cache_lock = threading.Lock()

    def _store_cache(self, cache_name: str, jsonpath_expr: str, data: Any) -> None:
        """Store data into cache based on JSONPath expression."""
        with self.cache_lock:
            try:
                matches = jsonpath(data, jsonpath_expr)
                if matches is False or not matches:
                    LOG.error(f"缓存设置失败, 请检查缓存配置是否正确.")
                    LOG.error(f"请求参数: {data}, 提取的 jsonpath 内容: {jsonpath_expr}")
                    return
                CacheControl.update_cache(
                    cache_name=cache_name,
                    value=matches[0]
                )
            except Exception as e:
                LOG.error(f"缓存存储失败: {str(e)}")
                raise

    def store_request_cache(self, cache_name: Text, jsonpath_expr: Text) -> None:
        """ 将接口的请求参数存入缓存 """
        LOG.debug(f"request_data: {self.request_data}")
        try:
            self._store_cache(cache_name, jsonpath_expr, self.request_data)
        except Exception as e:
            LOG.error(f"存储请求缓存失败: {str(e)}")

    def store_response_cache(self, cache_name: Text, jsonpath_expr: Text) -> None:
        """将响应结果存入缓存"""
        LOG.debug(f"response_data: {self.response_data}")
        try:
            self._store_cache(cache_name, jsonpath_expr, self.response_data)
        except Exception as e:
            LOG.error(f"存储响应缓存失败: {str(e)}")

    def store_caches(self) -> None:
        """Set caches based on store_cache configuration."""
        if self.store_cache:
            for cache in self.store_cache:
                cache_type: str = cache.get("type")
                jsonpath_expr: str = cache.get("jsonpath")
                cache_name: str = cache.get("name")

                store_method = (
                    self.store_request_cache
                    if cache_type == "request"
                    else self.store_response_cache
                )
                try:
                    store_method(cache_name=cache_name, jsonpath_expr=jsonpath_expr)
                except Exception as e:
                    LOG.error(f"存储缓存失败: {str(e)}")
                    continue

