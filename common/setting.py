import os
from pathlib import Path
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    print("Could not load .env because python-dotenv not found.")
else:
    # 加载 .env 文件
    load_dotenv()


class PathInitializer:
    """文件路径初始化"""

    def __init__(self):
        self._initialize_paths()
        self._create_directories()
        self._create_log_files()

    def _initialize_paths(self):
        self.root_path = Path(os.getenv("PROJECT_ROOT", os.getcwd())).resolve()
        self.cases_path = self.root_path / "testcases"
        self.yaml_path = self.root_path / "data"
        self.files_path = self.root_path / "files"
        self.logs_path = self.root_path / "logs"
        self.reports_path = self.root_path / "reports"
        self.tmp_path = self.reports_path / "tmp"
        self.allure_report = self.reports_path / "html" / "data" / "test-cases"
        self.case_summary = self.reports_path / "html" / "widgets" / "summary.json"
        self.config = self.root_path / "common" / "config.yaml"
        self.log_all = self.logs_path / "logs.log"
        self.log_err = self.logs_path / "error.log"

    def _create_directory(self, path):
        path.mkdir(parents=True, exist_ok=True)

    def _create_log_file(self, path):
        path.touch(exist_ok=True)

    def _create_directories(self):
        self._create_directory(self.logs_path)
        self._create_directory(self.reports_path)
        self._create_directory(self.tmp_path)

    def _create_log_files(self):
        self._create_log_file(self.log_all)
        self._create_log_file(self.log_err)


path_initializer = PathInitializer()
