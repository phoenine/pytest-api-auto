from common.setting import path_initializer
from utils.cases.case_control import YamlDataControl
from models.models import ProjectConfig


_data = YamlDataControl(path_initializer.config).load_yaml_data()
project_info = ProjectConfig(**_data)
