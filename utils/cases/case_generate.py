import os
from common.setting import path_initializer
from utils.cases.case_template import write_testcase_file
from utils.cases.case_control import YamlDataControl
from utils.cases.case_files import get_all_files
from utils.logs.log_control import LOG

class TestCaseAutomaticGeneration:
    def __init__(self):
        self.yaml_case_data = None
        self.file_path = None

    @property
    def yaml_case_path(self) -> str:
        """ 返回 yaml 用例文件路径 """
        return path_initializer.yaml_path

    @property
    def yaml_filename(self) -> str:
        """
        Generate dynamic YAML paths
        :return: 01_register/001_add_new_user.yaml
        """
        return os.path.relpath(self.file_path, start=self.yaml_case_path)

    @property
    def py_case_path(self) -> str:
        """ 返回 pytest 用例代码路径 """
        return path_initializer.cases_path

    @property
    def py_filename(self) -> str:
        """
        Convert the yaml file to py file.
        :return: 01_register/test_001_add_new_user.py
        """
        relative_path = self.yaml_filename.replace(".yaml", ".py")
        basename = os.path.basename(relative_path)
        dirname = os.path.dirname(relative_path)
        if not basename.startswith("test_"):
            basename = 'test_' + basename
        return os.path.join(dirname, basename)

    @property
    def py_basename(self) -> str:
        """_summary_

        Returns:
            str: _description_
        """
        return os.path.basename(self.py_filename)

    @property
    def testcase_func_title(self) -> str:
        """
        函数名称
        :return:
        """
        return os.path.splitext(self.py_basename)[0]

    @property
    def testcase_class_title(self) -> str:
        """
        自动生成类名称
        :return: sup_apply_list --> SupApplyList
        """
        return "".join(n.title() for n in self.testcase_func_title.split("_"))

    @property
    def testcase_full_path(self) -> str:
        """
        根据 yaml 中的用例，生成对应 testCase 层代码的路径
        :return: D:\\Project\\test_case\\test_case_demo.py
        """
        return os.path.join(self.py_case_path, self.py_filename)

    def mk_dir(self) -> None:
        """判断生成自动化代码的文件夹路径是否存在，如果不存在，则自动创建"""
        _case_dir_path = os.path.split(self.testcase_full_path)[0]
        if not os.path.exists(_case_dir_path):
            os.makedirs(_case_dir_path)

    @property
    def allure_epic(self) -> str:
        _allure_epic = self.yaml_case_data.get("case_common").get("allureEpic")
        assert _allure_epic is not None, (
            "用例中 allureEpic 为必填项，请检查用例内容, 用例路径：'%s'"
            % self.file_path
        )
        return _allure_epic

    @property
    def allure_feature(self) -> str:
        _allure_feature = self.yaml_case_data.get("case_common").get("allureFeature")
        assert _allure_feature is not None, (
            "用例中 allureFeature 为必填项，请检查用例内容, 用例路径：'%s'"
            % self.file_path
        )
        return _allure_feature

    @property
    def allure_story(self) -> str:
        _allure_story = self.yaml_case_data.get("case_common").get("allureStory")
        assert _allure_story is not None, (
            "用例中 allureStory 为必填项，请检查用例内容, 用例路径：'%s'"
            % self.file_path
        )
        return _allure_story

    def get_case_automatic(self) -> None:
        """Automatically generate test code.
        """

        all_file_path = get_all_files(self.yaml_case_path)
        for file in all_file_path:
            self.file_path = file
            self.mk_dir()
            self.yaml_case_data = YamlDataControl(file).load_yaml_data()
            LOG.debug(f"正在生成测试代码：\n"
                    f"    allure_epic: {self.allure_epic},\n"
                    f"    allure_feature: {self.allure_feature},\n"
                    f"    class_title: {self.testcase_class_title},\n"
                    f"    func_title: {self.testcase_func_title},\n"
                    f"    case_path: {self.testcase_full_path},\n"
                    f"    yaml_path: {self.yaml_filename},\n"
                    f"    file_name: {self.py_basename},\n"
                    f"    allure_story: {self.allure_story}")
            write_testcase_file(
                allure_epic=self.allure_epic,
                allure_feature=self.allure_feature,
                class_title=self.testcase_class_title,
                func_title=self.testcase_func_title,
                case_path=self.testcase_full_path,
                yaml_path=self.yaml_filename,
                file_name=self.py_basename,
                allure_story=self.allure_story,
            )
