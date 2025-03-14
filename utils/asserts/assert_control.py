import ast
import json
import jsonpath  # type: ignore
from functools import lru_cache
from typing import Any, Dict, Text, Callable
from utils.logs.log_control import LOG
from models.models import AssertMethod
from utils.asserts import assert_utils
from utils.cases.common_control import cache_replace
import types


class AssertControl:
    def __init__(self, request_data: Any, response_data: Any, assert_data: Dict) -> None:
        self.request_data = request_data
        self.response_data = response_data
        self.assert_data = ast.literal_eval(cache_replace(str(assert_data)))

    # @property
    # def get_assert_data(self) -> Dict:
    #     try:
    #         print(self.assert_data)
    #         return ast.literal_eval(cache_replace(str(self.assert_data)))
    #     except (ValueError, SyntaxError) as e:
    #         LOG.error("Invalid assert_data format: {}".format(e))
    #         raise

    @property
    def get_assert_type(self) -> str:
        assert_data = self.assert_data
        if "type" not in assert_data.keys():
            LOG.error(f"断言数据: '{self.assert_data}' 中缺少 `type` 属性")
            raise
        return AssertMethod(assert_data["type"]).name

    @property
    def get_assert_value(self) -> Any:
        assert_data = self.assert_data
        if "value" not in assert_data.keys():
            LOG.error(f"断言数据: '{self.assert_data}' 中缺少 `value` 属性")
            raise
        return assert_data["value"]

    @property
    def get_assert_jsonpath(self) -> str:
        assert_data = self.assert_data
        if "jsonpath" not in assert_data.keys():
            LOG.error(f"断言数据: '{assert_data}' 中缺少 `jsonpath` 属性")
            raise
        return assert_data["jsonpath"]

    @property
    def _assert_response_data(self):
        try:
            if isinstance(self.response_data, str):
                response_json = json.loads(self.response_data)
            elif isinstance(self.response_data, dict):
                response_json = self.response_data
            elif isinstance(self.response_data, list):
                response_json = json.loads(json.dumps(self.response_data))
            else:
                raise ValueError("响应数据类型不支持")
        except json.JSONDecodeError as e:
            raise ValueError(f"响应数据不是有效的 JSON 格式: {e}")
        LOG.debug(f"response_json is : {response_json}")
        try:
            resp_data = jsonpath.jsonpath(response_json, self.get_assert_jsonpath)
            return resp_data[0] if resp_data and len(resp_data) == 1 else resp_data
        except:
            LOG.error(f"jsonpath 数据提取失败，当前语法: {self.get_assert_jsonpath}")
            raise

    @staticmethod
    def _load_module_functions(module) -> Dict[Text, Callable]:
        return {
            name: item
            for name, item in vars(module).items()
            if isinstance(item, types.FunctionType)
        }

    @lru_cache(maxsize=1)
    def _functions_mapping(self) -> Dict[Text, Callable]:
        return self._load_module_functions(assert_utils)

    def _assert(self, actual_value: Any, expect_value: Any) -> None:
        try:
            func = self._functions_mapping()[self.get_assert_type.lower()]
            func(actual_value, expect_value)
        except KeyError:
            raise AssertionError(f"未知的断言类型: {self.get_assert_type}")

    def assert_type_handle(self) -> None:
        if not isinstance(self.get_assert_type, str):
            LOG.error("获取断言失败，目前只支持响应式断言")
            raise
        self._assert(self._assert_response_data, self.get_assert_value)


class Assert(AssertControl):
    def assert_data_list(self) -> list:
        return list(self.assert_data.values())

    def assert_type_handle(self) -> None:
        for assert_item in self.assert_data_list():
            self.assert_data = assert_item
            super().assert_type_handle()

