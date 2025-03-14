import ast
import json
from copy import deepcopy
from typing import Dict, Text, Optional
from jsonpath import jsonpath  # type: ignore
from utils.caches.cache_control import CacheControl
from utils.requests.request_control import RequestControl
from models.models import DependentType
from utils.logs.log_control import LOG
from utils.cases.common_control import cache_replace


class DependentControl:
    """处理依赖相关的业务"""

    def __init__(self, yaml_data: Dict) -> None:
        self._yaml_data = yaml_data

    @staticmethod
    def get_cache(case_id: str) -> Dict:
        """获取缓存用例池中的数据，通过 case_id 提取"""
        _cache_data = deepcopy(CacheControl.get_cache(case_id))
        if not _cache_data:
            LOG.error(f"Cache not found for case_id: {case_id}")
            raise ValueError(f"Cache not found for case_id: {case_id}")
        LOG.info(f"{case_id} 已缓存数据: {_cache_data}")
        return _cache_data

    @staticmethod
    def jsonpath_data(obj: dict, expr: str) -> list:
        """通过jsonpath提取依赖的数据"""
        _jsonpath_data = jsonpath(obj, expr)
        if not _jsonpath_data:
            LOG.error(f"jsonpath提取失败. Data: {obj}, JSONPath: {expr}")
            raise ValueError(f"Failed to extract data using JSONPath: {expr}")
        return _jsonpath_data

    def url_replace(
        self,
        replace_key: str,
        jsonpath_dates: dict,
        jsonpath_data: list,
        case_data: dict,
    ) -> None:
        """url中的动态参数替换"""
        if "$url_param" in replace_key:
            case_data["url"] = case_data["url"].replace(
                replace_key, str(jsonpath_data[0])
            )
            jsonpath_dates["$.url"] = case_data["url"]
        else:
            jsonpath_dates[replace_key] = jsonpath_data[0]

    def dependent_data_handler(
        self,
        _jsonpath: Text,
        set_value: Optional[Text],
        replace_key: Optional[Text],
        jsonpath_dates: Dict,
        data: Dict,
        dependent_type: str,
    ) -> None:
        """处理数据替换"""
        jsonpath_data = self.jsonpath_data(data, _jsonpath)

        # 更新缓存
        if set_value:
            CacheControl.update_cache(
                cache_name=set_value,
                value=jsonpath_data[0] if len(jsonpath_data) == 1 else jsonpath_data,
            )

        # 处理替换逻辑
        if replace_key:
            if dependent_type == "response":
                jsonpath_dates[replace_key] = jsonpath_data[0]

            # URL替换逻辑
            self.url_replace(
                replace_key=replace_key,
                jsonpath_dates=jsonpath_dates,
                jsonpath_data=jsonpath_data,
                case_data=data,
            )

    def process_dependence_case(
        self, dependence_case: Dict, jsonpath_dates: Dict
    ) -> None:
        """处理依赖的单个用例"""
        if not dependence_case.get("dependent_data"):
            LOG.warning("No dependent data found.")
            return

        case_id = dependence_case.get("case_id")
        LOG.info(f"Processing dependent case_id: {case_id}")

        # 获取并清理缓存数据
        dependent_data = self.get_cache(case_id)
        dependent_data.store_cache = None

        # 执行依赖用例
        res_data, req_data = RequestControl(dependent_data).http_request(
            dependent_switch=False, update_title=False
        )

        # 处理每个依赖项
        for item in dependence_case["dependent_data"]:
            LOG.info(f"Processing dependent data: {item}")
            data = (
                res_data
                if item["dependent_type"] == DependentType.RESPONSE.value
                else req_data
            )
            self.dependent_data_handler(
                data=data,
                _jsonpath=item.get("jsonpath"),
                set_value=item.get("set_cache"),
                replace_key=item.get("replace_key"),
                jsonpath_dates=jsonpath_dates,
                dependent_type=item.get("dependent_type"),
            )

    def dependence_data(self) -> Optional[Dict]:
        """判断是否有数据依赖并处理"""
        if not self._yaml_data["is_dependence"]:
            return None

        jsonpath_dates = {}
        for dependence_case in self._yaml_data.get("dependence_case", []):
            self.process_dependence_case(dependence_case, jsonpath_dates)
        return jsonpath_dates

    def get_dependent_data(self) -> None:
        """Retrieve and update dependent data."""
        dependent_data = self.dependence_data()
        if not dependent_data:
            return

        def update_nested_dict(d, keys, value):
            """递归更新嵌套字典"""
            for key in keys[:-1]:
                d = d.setdefault(key, {})
            d[keys[-1]] = value

        # 处理每个依赖数据
        for key, value in dependent_data.items():
            keys = key.split(".")
            keys = [
                int(k[1:-1]) if k.startswith("[") and k.endswith("]") else k
                for k in keys
                if k != "$"
            ]
            update_nested_dict(self._yaml_data, keys, value)

        LOG.info(f"Updated data: {json.dumps(self._yaml_data, indent=2)}")

