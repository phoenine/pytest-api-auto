import os
import ast
import io
import json
import allure
from typing import Dict
from requests import request, Response, exceptions
from requests_toolbelt import MultipartEncoder  # type: ignore
from models.models import RequestType
from models.models import TestcaseParams
from utils.requests.testcase_cache import TestcaseCache
from utils.logs.log_control import LOG
from common.setting import path_initializer
from utils.logs.log_decorator import log_decorator
from utils.logs.execute_decorator import execution_duration
from utils.cases.common_control import cache_replace, url_replace
from utils.caches.cache_control import CacheControl
from utils.allures.allure_attach import (
    allure_step_with_attach,
    allure_step_without_attach,
    allure_attach,
)


class RequestControl:
    def __init__(self, yaml_data: TestcaseParams) -> None:
        # Pydantic 模型序列化
        self._yaml_data = json.loads(yaml_data.model_dump_json(indent=2))

    # def request_type_for_none(self, headers: Dict, method: str, **kwargs):
    #     """Send a request with no data."""
    #     _url = self._yaml_data.get("url")
    #     return request(
    #         method=method,
    #         url=url_replace(_url),
    #         headers=headers,
    #         verify=False,
    #         **kwargs,
    #     )

    def handle_response(self, response: Response):
        """Handle the HTTP response"""
        res = {
            "status_code": response.status_code,
            "time": response.elapsed.total_seconds(),
        }

        if response.status_code == 204:
            res["data"] = {"status": "204 No Content"}
            return res
        try:
            res["data"] = response.json()
        except ValueError:
            LOG.error(f"Error processing response: {response.text}")
            res["data"] = response.text
        return res

    def upload_file(self):
        """Prepare file upload data."""
        file_data = {}
        filename = self._yaml_data["data"]["file"]
        file_path = os.path.join(path_initializer.files_path, filename)
        try:
            with open(file_path, "rb") as file:
                file_content = io.BytesIO(file.read())
                file_data["file"] = (filename, file_content, "multipart/form-data")
                allure_attach(source=file_path, name=filename, extension=filename)
                multipart = MultipartEncoder(fields=file_data)
                self._yaml_data["headers"]["Content-Type"] = multipart.content_type
                return multipart
        except FileNotFoundError:
            LOG.error(f"File not found: {file_path}")
            raise

    @log_decorator(True)
    @execution_duration(2000)
    def http_request(
        self, dependent_switch: bool = True, update_title: bool = True, **kwargs
    ):
        """Send HTTP request based on YAML data"""
        if dependent_switch:
            self._handle_dependent_data()
        request_params = self._get_request_params()
        response = self._send_request(request_params, **kwargs)
        response_data = self.handle_response(response)
        self._log_allure_info(response_data, request_params, update_title)
        if request_params.get("store_cache"):
            TestcaseCache(
                store_cache=request_params.get("store_cache"),
                request_data=request_params.get("data"),
                response_data=response_data.get("data"),
            ).store_caches()
        LOG.debug(f"Current cache: {CacheControl.get_cache(cache_name=None)}")
        return response_data.get("data"), self._yaml_data

    def _get_request_params(self):
        """获取请求参数"""
        _url = url_replace(self._yaml_data.get("url"))
        _method = self._yaml_data.get("method")
        _headers = self._yaml_data.get("headers")
        _request_type = self._yaml_data.get("request_type")
        _is_run = self._yaml_data.get("is_run")
        _data = self._yaml_data.get("data")
        _store_cache = self._yaml_data.get("store_cache")
        _dependent_data = self._yaml_data.get("dependence_case")
        _assert = self._yaml_data.get("assert_data")
        # Add token to headers
        _headers["Authorization"] = CacheControl.get_cache("access_token")
        if not _is_run:
            LOG.warning("The testcase is marked as not to run.")
            return None
        if _data:
            _data = ast.literal_eval(cache_replace(str(_data)))
        return {
            "url": _url,
            "method": _method,
            "headers": _headers,
            "request_type": _request_type,
            "data": _data,
            "store_cache": _store_cache,
            "dependent_data": _dependent_data,
            "assert_data": _assert,
        }

    def _handle_dependent_data(self):
        """处理依赖数据"""
        from utils.requests.dependent_control import DependentControl

        DependentControl(self._yaml_data).get_dependent_data()

    def _send_request(self, request_params, **kwargs):
        """发送 HTTP 请求"""
        _url = request_params.get("url")
        _method = request_params.get("method")
        _headers = request_params.get("headers")
        _request_type = request_params.get("request_type")
        _data = request_params.get("data")
        try:
            if _request_type == RequestType.JSON.value:
                res = request(
                    method=_method, url=_url, json=_data, headers=_headers, **kwargs
                )
            elif _request_type == RequestType.FILE.value:
                multipart = self.upload_file()
                res = request(
                    method=_method,
                    url=_url,
                    data=multipart,
                    headers=_headers,
                    **kwargs,
                )
            else:
                LOG.error(f"Unsupported _request_type: {_request_type}")
                raise ValueError(f"Unsupported _request_type: {_request_type}")
        except exceptions.RequestException as e:
            LOG.error(f"Request failed: {e}")
            raise
        return res

    def _log_allure_info(
        self, response_data, request_params, update_title: bool = True
    ):
        """Log information to Allure report with structured format."""
        if update_title:
            allure.dynamic.title(self._yaml_data.get("description"))

        with allure.step("请求信息"):
            allure_step_without_attach(f"请求URL: {request_params.get('url')}")
            allure_step_without_attach(f"请求方式: {request_params.get('method')}")
            allure_step_with_attach("请求头: ", request_params.get("headers"))
            allure_step_with_attach("请求数据: ", request_params.get("data"))

        with allure.step("依赖与预期"):
            allure_step_with_attach("依赖数据: ", request_params.get("dependent_data"))
            allure_step_with_attach("预期数据: ", request_params.get("assert_data"))

        with allure.step("响应信息"):
            allure_step_without_attach(
                f"响应状态码: {response_data.get('status_code')}"
            )
            allure_step_without_attach(f"响应耗时(s): {response_data.get('time')}")
            allure_step_with_attach("响应结果: ", response_data.get("data"))

