import os
import yaml.scanner # type: ignore
from utils.cases.common_control import regular_replace
from utils.logs.log_control import LOG

class YamlDataControl:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_yaml_data(self) -> dict:
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as data:
                try:
                    return yaml.load(data, Loader=yaml.FullLoader)
                except:
                    LOG.error(f"文件解码错误, file path:{self.file_path}")
                    raise
        else:
            LOG.error(f"文件不存在, file path:{self.file_path}")
            raise

    def update_yaml_data(self, key: str, value) -> int:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                lines = [line for line in f if line != '\n']

            with open(self.file_path, 'w', encoding='utf-8') as f:
                flag = 0
                for line in lines:
                    if key in line and '#' not in line:
                        newline = "{0}: {1}".format(line.split(":")[0], value)
                        f.write('%s\n' % newline)
                        flag = 1
                    else:
                        f.write(line)
                return flag
        except (FileNotFoundError, IOError) as e:
            raise IOError(f"File operation error: {e}")

class YamlCaseData(YamlDataControl):
    def load_case_data(self):
        try:
            _yaml_data = self.load_yaml_data()
            re_data = regular_replace(str(_yaml_data))
            return yaml.safe_load(re_data)
        except yaml.scanner.ScannerError as e:
            raise ValueError("YAML format error: " + str(e))

    def load_case_data_list(self) -> list:
        return [data for data in self.load_yaml_data()]

