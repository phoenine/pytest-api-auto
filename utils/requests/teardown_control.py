from typing import Dict, List
from copy import deepcopy
from jsonpath import jsonpath  # type: ignore
from utils.requests.request_control import RequestControl
from utils.logs.log_control import LOG
from utils.caches.cache_control import CacheControl


class TearDownControl:
    """处理teardown中的请求"""

    def __init__(self, request_data: Dict, response_data: Dict) -> None:
        self._request_data = request_data
        self._response_data = response_data

    def send_request_handler(self, teardown_data: Dict) -> None:
        """处理teardown中的send_request"""
        _case_id = teardown_data.get("case_id")
        _teardown_case = deepcopy(CacheControl.get_cache(_case_id))
        # 跑dependence_case前清理store_cache，避免之前的数据被覆盖
        _teardown_case.store_cache = None
        _teardown_params = teardown_data.get("teardown_data")
        if _teardown_params and isinstance(_teardown_params, list):
            for request_item in _teardown_params:
                _replace_key = request_item.get("replace_key")
                _cache_data = CacheControl.get_cache(request_item.get("cache_data"))
                if not _cache_data:
                    LOG.error(f"Cache not found for case_id: {_case_id}")
                    raise ValueError(
                        "Cache data not found, cannot proceed with teardown"
                    )
                if "$url_param" in _replace_key:
                    _teardown_case.url = _teardown_case.url.replace(
                        _replace_key, _cache_data
                    )
                # 处理依赖类型
                _type = request_item.get("dependent_type")
                if _type not in ["cache", "response", "request"]:
                    LOG.error(
                        f"Invalid dependent_type({_type}) in teardown, please check the case"
                    )
                    raise ValueError(f"Invalid dependent_type({_type}) in teardown")

                #! 根据依赖类型处理, 当前不实现
                # if _type == "cache":
                #     self.dependent_type_cache(teardown_data=request_item)
                # elif _type == "response":
                #     self.dependent_type_response(teardown_data=request_item)
                # elif _type == "request":
                #     self.dependent_type_request(teardown_data=request_item)
        else:
            LOG.error("teardown_data is not a list")
            raise
        RequestControl(_teardown_case).http_request(
            dependent_switch=False, update_title=False
        )

    def teardown_handle(self) -> None:
        """处理teardown中的数据"""

        _teardown_data_list = self._request_data.get("teardown")
        if _teardown_data_list is None:
            LOG.info("No teardown data found, skipping teardown process.")
            return

        if not isinstance(_teardown_data_list, list):
            LOG.error("teardown_data is not a list")
            raise TypeError("teardown_data must be a list of teardown configurations")

        LOG.debug(
            f"Processing teardown data, total teardown requests: {len(_teardown_data_list)}"
        )
        for _teardown_data in _teardown_data_list:
            if not isinstance(_teardown_data, dict):
                LOG.error(
                    f"Invalid teardown data format, expected dict but got {type(_teardown_data)}"
                )
                continue
            self.send_request_handler(teardown_data=_teardown_data)
