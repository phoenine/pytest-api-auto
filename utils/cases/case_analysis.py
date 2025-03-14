import os
from utils.logs.log_control import LOG
from typing import Text, Dict, List, Union, Any
from utils.cases.case_control import YamlCaseData
from models.models import MethodType
from models.models import RequestType
from models.models import TestcaseParams


class CaseDataCheck:
    """ yaml 数据解析, 判断数据填写是否符合规范 """

    def __init__(self, file_path) -> None:
        self._file_path = file_path
        self._case_data = None
        self._case_id = None
        if not os.path.exists(self._file_path):
            LOG.error(f"用例文件不存在！\n文件路径: {self._file_path}")
            raise

    @property
    def get_host(self) -> str:
        """ 获取host信息 """
        _host = self._case_data.get("host", None)
        _url = self._case_data.get("url", None)
        if _url is None or _host is None:
            LOG.error(f"用例中的 url 或者 host 不能为空.")
            LOG.error(f"用例ID: {self._case_id}, 用例路径: {self._file_path}")
            raise
        return _host + _url

    @property
    def get_method(self) -> Text:
        _case_method = self._case_data.get("method", None)
        if _case_method is None:
            LOG.error(f"用例中的 method 不能为空.")
            LOG.error(f"用例ID: {self._case_id}, 用例路径: {self._file_path}")
            raise
        if _case_method.upper() not in MethodType.__members__:
            LOG.error(f"找不到对应的MethodType.")
            LOG.error(f"用例ID: {self._case_id}, 用例路径: {self._file_path}")
            raise
        return _case_method.upper()

    @property
    def get_description(self) -> Text:
        _description = self._case_data.get("description", None)
        if _description is None:
            LOG.error(f"用例中的 description 不能为空.")
            LOG.error(f"用例ID: {self._case_id}, 用例路径: {self._file_path}")
            raise
        return _description

    @property
    def get_headers(self) -> Dict:
        _headers = self._case_data.get("headers", None)
        if _headers is None:
            LOG.error(f"用例中的 headers 不能为空.")
            LOG.error(f"用例ID: {self._case_id}, 用例路径: {self._file_path}")
            raise
        return _headers

    @property
    def get_request_type(self) -> Text:
        _request_type = self._case_data.get("request_type", None)
        if _request_type is None:
            LOG.error(f"用例中的 request_type 不能为空.")
            LOG.error(f"用例ID: {self._case_id}, 用例路径: {self._file_path}")
            raise
        if _request_type.upper() not in RequestType.__members__:
            LOG.error(f"找不到对应的request_type.")
            LOG.error(f"用例ID: {self._case_id}, 用例路径: {self._file_path}")
            raise
        return _request_type

    @property
    def get_assert_data(self) -> Dict:
        _assert = self._case_data.get("assert_data", None)
        if _assert is None:
            LOG.error(f"用例中的 assert 不能为空.")
            LOG.error(f"用例ID: {self._case_id}, 用例路径: {self._file_path}")
            raise
        return _assert

    @property
    def get_is_run(self) -> Union[None, bool]:
        try:
            _is_run = self._case_data.get("is_run")
            if _is_run == 'None':
                return True
            return _is_run
        except KeyError:
            LOG.error(f"用例中未找到 is_run. 用例ID: {self._case_id}")
            raise

    @property
    def get_case_dates(self) -> Any:
        try:
            _data = self._case_data.get("data")
            if _data == 'None':
                return None
            return _data
        except KeyError:
            LOG.error(f"用例中未找到 _data. 用例ID: {self._case_id}")
            raise

    @property
    def get_store_cache(self) ->  Union[List[Dict[Text, Any]], None]:
        try:
            _store_cache = self._case_data.get("store_cache")
            if _store_cache == 'None':
                return None
            return _store_cache
        except KeyError:
            raise KeyError(f"用例中未找到 store_cache. 用例ID: {self._case_id}")

    @property
    def get_is_dependence(self) -> Union[None, bool]:
        try:
            _is_dependence = self._case_data.get("is_dependence")
            if _is_dependence == 'None':
                return False
            return _is_dependence
        except KeyError:
            raise KeyError(f"用例中未找到 is_dependence. 用例ID: {self._case_id}")

    @property
    def get_dependence_case(self) -> Union[List, None]:
        try:
            _dependence_case = self._case_data.get("dependence_case")
            if _dependence_case == 'None':
                return None
            return _dependence_case
        except KeyError:
            raise KeyError(f"用例中未找到 dependence_case. 用例ID: {self._case_id}")

    @property
    def get_teardown(self) -> Union[List, None]:
        try:
            _teardown = self._case_data.get("teardown")
            if _teardown == 'None':
                return None
            return _teardown
        except KeyError:
            raise KeyError(f"用例中未找到 teardown. 用例ID: {self._case_id}")


class CaseData(CaseDataCheck):
    """ Process all test cases from YAML files. """

    def case_process(self, case_id_switch=False):
        dates = YamlCaseData(self._file_path).load_case_data()
        case_lists = []
        for key, values in dates.items():
            if key != 'case_common':
                self._case_id, self._case_data = key, values
                case_date = {
                    'url': self.get_host,
                    'method': self.get_method,
                    'description': self.get_description,
                    'headers': self.get_headers,
                    'request_type': self.get_request_type,
                    'is_run': self.get_is_run,
                    'data': self.get_case_dates,
                    "store_cache": self.get_store_cache,
                    'is_dependence': self.get_is_dependence,
                    'dependence_case': self.get_dependence_case,
                    "assert_data": self.get_assert_data,
                    "teardown": self.get_teardown
                }
                if case_id_switch is True:
                    case_lists.append({key: TestcaseParams(**case_date)})
                else:
                    case_lists.append(TestcaseParams(**case_date))
        return case_lists
