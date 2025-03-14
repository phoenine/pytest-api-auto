from threading import Lock
from typing import Dict, Any, Optional
from utils.logs.log_control import LOG


class CacheControl:
    _instance = None
    _lock = Lock()
    _cache: Dict[str, Any] = {}

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance._cache = {}
        return cls._instance

    @classmethod
    def get_cache(cls, cache_name: Optional[str] = None) -> Any:
        """获取缓存数据"""
        with cls._lock:
            if cache_name is None:
                return cls._cache.copy()
            LOG.info(f"获取缓存数据成功，缓存名称：{cache_name}，缓存值：{cls._cache.get(cache_name)}")
            return cls._cache.get(cache_name)

    @classmethod
    def update_cache(cls, cache_name: str, value: Any) -> None:
        """更新缓存数据"""
        with cls._lock:
            cls._cache[cache_name] = value
            LOG.info(f"缓存数据更新成功，缓存名称：{cache_name}，缓存值：{value}")

    @classmethod
    def clear_cache(cls) -> None:
        """清空缓存数据"""
        with cls._lock:
            cls._cache.clear()
            LOG.info("缓存数据清空成功")
