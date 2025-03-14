import json
from common.setting import path_initializer
from utils.cases.case_files import get_all_files
from models.models import TestcaseMetrics
from utils.logs.log_control import LOG


class AllureFileReport:
    """allure报告数据清洗, 提取业务数据"""

    @classmethod
    def get_all_tests(cls) -> list:
        """获取所有 allure 报告中执行用例的情况"""

        cases = []
        #! 这里需要检查下是report_path还是reports\html\data\test-cases
        for json_case in get_all_files(
            path_initializer.allure_report, yaml_data_switch=False
        ):
            with open(json_case, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                cases.append(data)
        LOG.debug(f"test cases: {cases}")
        return cases

    def get_failed_case(self) -> list:
        """获取到所有失败的用例标题和用例代码路径"""

        error_cases = []
        for case in self.get_all_tests():
            if case["status"] in ("failed", "broken"):
                error_cases.append((case["name"], case["fullName"]))
        return error_cases

    def get_failed_cases_detail(self) -> str:
        """返回所有失败的测试用例相关内容"""

        failed_cases = self.get_failed_case()
        if not failed_cases:
            return ""
        case_details = [
            "失败用例:\n",
            "        **********************************\n",
            *[f"        {name}:{full_name}\n" for name, full_name in failed_cases],
        ]
        return "".join(case_details)

    @classmethod
    def cases_count(cls) -> dict:
        """统计用例数量"""

        try:
            with open(path_initializer.case_summary, "r", encoding="utf-8") as file:
                data = json.load(file)
            _case_count = data.get("statistic")
            _time = data.get("time")
            keep_keys = ["passed", "failed", "broken", "skipped", "total"]
            run_case_data = {k: v for k, v in _case_count.items() if k in keep_keys}
            if _case_count["total"] == 0:
                run_case_data["pass_rate"] = 0.0
            run_case_data["pass_rate"] = round(
                run_case_data["passed"] / _case_count["total"] * 100, 2
            )
            run_case_data["time"] = (
                None
                if run_case_data["total"] == 0
                else str(round(_time["duration"] / 1000, 2)) + "s"
            )
            return TestcaseMetrics(**run_case_data)
        except FileNotFoundError:
            LOG.error(f"{path_initializer.case_summary} does not exist.")
            return {}
        except Exception as e:
            LOG.error(f"Error reading file: {e}")
            return {}
