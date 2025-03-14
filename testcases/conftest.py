import os
import pytest
import time
import allure  # type: ignore
from common.setting import path_initializer
from utils.cases.case_analysis import CaseData
from utils.caches.cache_control import CacheControl
from utils.requests.request_control import RequestControl
from utils.logs.log_control import LOG
from utils.allures.allure_attach import (
    allure_step_with_attach,
    allure_step_without_attach,
)


@pytest.fixture(scope="session", autouse=True)
def clear_report():
    """ Clear allure data before running """

    try:
        for file in os.listdir(path_initializer.tmp_path):
            if "json" in file or "txt" in file:
                os.remove(os.path.join(path_initializer.tmp_path, file))
        LOG.info("Clear allure data successfully.")
    except Exception as e:
        LOG.error("Clear allure data failed, error: ", e)


@pytest.fixture(scope="session", autouse=True)
def work_login_init() -> None:
    """
    Execute login case and obtain access token.
    Returns:
        str: Access token obtained from the login process.
    """

    login_yaml = CaseData(os.path.join(path_initializer.yaml_path, '01_login', '001_login_common.yaml')).case_process()[0]
    res, _ = RequestControl(login_yaml).http_request()
    if res.get('data'):
        token = 'Bearer ' + res['data']
        CacheControl.update_cache(cache_name='access_token', value=token)
    else:
        LOG.error("Login case failed or was not executed, unable to get token information.")
        raise



@pytest.fixture(scope="function", autouse=True)
def case_skip(in_data) -> None:
    """ 处理跳过用例 """
    if in_data.is_run is False:
        allure.dynamic.title(in_data.description)
        allure_step_without_attach(f"请求URL: {in_data.url}")
        allure_step_without_attach(f"请求方式: {in_data.method}")
        allure_step_with_attach("请求头: ", in_data.headers)
        allure_step_with_attach("请求数据: ", str(in_data.data))
        allure_step_with_attach("依赖数据: ", str(in_data.dependence_case))
        allure_step_with_attach("预期数据: ", str(in_data.assert_data))
        pytest.skip()


def pytest_terminal_summary(terminalreporter):
    """收集测试结果"""

    _PASSED = len(
        [i for i in terminalreporter.stats.get("passed", []) if i.when != "teardown"]
    )
    _ERROR = len(
        [i for i in terminalreporter.stats.get("error", []) if i.when != "teardown"]
    )
    _FAILED = len(
        [i for i in terminalreporter.stats.get("failed", []) if i.when != "teardown"]
    )
    _SKIPPED = len(
        [i for i in terminalreporter.stats.get("skipped", []) if i.when != "teardown"]
    )
    _TOTAL = terminalreporter._numcollected
    _TIMES = time.time() - terminalreporter._sessionstarttime

    LOG.info(f"成功用例数: {_PASSED}")
    if _ERROR == 0:
        LOG.info(f"异常用例数: {_ERROR}")
    else:
        LOG.error(f"异常用例数: {_ERROR}")
    if _FAILED == 0:
        LOG.info(f"失败用例数: {_FAILED}")
    else:
        LOG.error(f"失败用例数: {_FAILED}")
    LOG.warning(f"跳过用例数: {_SKIPPED}")
    LOG.info("用例执行时长: %.2f" % _TIMES + " s")

    try:
        _RATE = round((_PASSED + _SKIPPED) / _TOTAL * 100, 2)
        LOG.info("用例成功率: %.2f" % _RATE + " %")
    except ZeroDivisionError:
        LOG.error("用例成功率: 0.00 %")


def pytest_collection_modifyitems(items):
    """
    测试用例收集完成时，将收集到的 item 的 name 和 node_id 的中文显示在控制台上
    """
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke")
    config.addinivalue_line("markers", "regression")
