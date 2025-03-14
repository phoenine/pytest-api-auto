import os
import traceback
import pytest
from models import project_info
from models.models import NotificationType
from utils.logs.log_control import LOG
from utils.allures.allure_reports import AllureFileReport
from utils.cases.case_generate import TestCaseAutomaticGeneration
from utils.notify.lark import LarkChatBot

def run():
    try:
        LOG.info(
            """
        $$$$$$$\  $$\   $$\  $$$$$$\  $$$$$$$$\
        $$  __$$\ $$ |  $$ |$$  __$$\ $$  _____|
        $$ |  $$ |$$ |  $$ |$$ /  $$ |$$ |
        $$$$$$$  |$$$$$$$$ |$$ |  $$ |$$$$$\
        $$  ____/ $$  __$$ |$$ |  $$ |$$  __|
        $$ |      $$ |  $$ |$$ |  $$ |$$ |
        $$ |      $$ |  $$ | $$$$$$  |$$$$$$$$\
        \__|      \__|  \__| \______/ \________|
                  开始执行{}项目...
                """.format(project_info.project_name)
        )

        # 判断现有的测试用例，如果未生成测试代码，则自动生成
        TestCaseAutomaticGeneration().get_case_automatic()

        pytest.main(['-s', '-W', 'ignore:Module already imported:pytest.PytestWarning',
                     '--alluredir', './reports/tmp'])
        """
                   --reruns: 失败重跑次数
                   --count: 重复执行次数
                   -v: 显示错误位置以及错误的详细信息
                   -s: 等价于 pytest --capture=no 可以捕获print函数的输出
                   -q: 简化输出信息
                   -m: 运行指定标签的测试用例
                   -x: 一旦错误，则停止运行
                   --maxfail: 设置最大失败次数，当超出这个阈值时，则不会在执行测试用例
                    "--reruns=3", "--reruns-delay=2"
                   """
        os.system(r"allure generate ./reports/tmp -o ./reports/html --clean")
        allure_data = AllureFileReport().cases_count()
        LOG.info(allure_data)
        if project_info.notification_type == NotificationType.LARK.value:
            LOG.info("开始发送测试报告")
            LarkChatBot(allure_data).post()
        os.system(f"nohup allure serve ./reports/tmp -h 0.0.0.0 -p 39998 > allure.log 2>&1 &")
        # os.system(f"allure serve ./reports/tmp")
    except Exception:
        e = traceback.format_exc()
        raise


if __name__ == '__main__':
    run()
