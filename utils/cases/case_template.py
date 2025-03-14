import os
import datetime
from common.setting import path_initializer
from utils.cases.case_control import YamlDataControl


def write_testcase_file(
    allure_epic,
    allure_feature,
    class_title,
    func_title,
    case_path,
    yaml_path,
    file_name,
    allure_story,
):
    """Write testcase python files.

    Args:
        allure_epic (_type_): 项目名称
        allure_feature (_type_): 用例名称
        class_title (_type_): 类名称
        func_title (_type_): 函数名称
        case_path (_type_): pytest 文件路径
        yaml_path (_type_): yaml 文件路径
        file_name (_type_): 文件名称
        allure_story (_type_): _description_
    """
    author = (
        YamlDataControl(path_initializer.config).load_yaml_data().get("tester_name")
    )
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    page = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : {now}
# @Author : {author}

import os
import allure
import pytest
from common.setting import path_initializer
from utils.cases.case_analysis import CaseData
from utils.asserts.assert_control import Assert
from utils.requests.request_control import RequestControl
from utils.requests.teardown_control import TearDownControl


TestData = CaseData(os.path.join(path_initializer.yaml_path, r'{yaml_path}')).case_process()


@allure.epic("{allure_epic}")
@allure.feature("{allure_feature}")
class Test{class_title}:

    @allure.story("{allure_story}")
    @pytest.mark.parametrize('in_data', TestData, ids=[i.description for i in TestData])
    def {func_title}(self, in_data, case_skip):
        """
        :param :
        :return:
        """

        response_data, request_data = RequestControl(in_data).http_request()
        TearDownControl(request_data, response_data).teardown_handle()
        Assert(request_data, response_data, request_data.get("assert_data")).assert_type_handle()


if __name__ == '__main__':
    pytest.main(['{file_name}', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
'''

    with open(case_path, "w", encoding="utf-8") as f:
        f.write(page)
