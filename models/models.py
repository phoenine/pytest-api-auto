from enum import Enum, unique
from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from typing import Dict, Union, List, Any, Optional


@unique
class NotificationType(Enum):
    """自动化通知方式"""

    DEFAULT = 0
    LARK = 1


@unique
class RequestType(Enum):
    """request请求参数的数据类型"""

    JSON = "JSON"
    FILE = "FILE"
    PARAMS = "PARAMS"
    NONE = "NONE"


@unique
class MethodType(Enum):
    """请求方法类型"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


@unique
class DependentType(Enum):
    """数据依赖相关枚举"""

    REQUEST = "request"
    RESPONSE = "response"


@unique
class AllureAttachmentType(Enum):
    """allure报告的文件类型枚举"""

    TEXT = "txt"
    CSV = "csv"
    HTML = "html"
    YAML = "yaml"
    JSON = "json"
    PNG = "png"
    PDF = "pdf"


@unique
class AssertMethod(Enum):
    """断言类型"""

    EQUAL = "eq"
    NOT_EQUAL = "ne"
    LESS_THAN = "lt"
    GREATER_THAN = "gt"
    LENGTH_EQUAL = "len_eq"
    LENGTH_GT = "len_gt"
    LENGTH_LT = "len_lt"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"


@dataclass
class TestcaseMetrics:
    """用例执行数据"""

    passed: int
    failed: int
    broken: int
    skipped: int
    total: int
    pass_rate: float
    time: str | None = None


class Webhook(BaseModel):
    """Webhook配置"""

    webhook: str


class ProjectConfig(BaseModel):
    """项目配置"""

    project_name: str
    environment: str
    tester_name: str
    host: str
    notification_type: int
    lark_webhook: Webhook
    excel_report: bool


#! 以下是pydantic的数据模型


class StoreCache(BaseModel):
    """缓存数据"""

    type: str
    jsonpath: str
    name: str


class DependentData(BaseModel):
    """依赖数据参数"""

    dependent_type: str
    jsonpath: str
    set_cache: str
    replace_key: Optional[str] = None


class DependentCaseData(BaseModel):
    """依赖用例参数"""

    case_id: str
    dependent_data: List[DependentData] | None = None


class TearDownData(BaseModel):
    """请求参数"""

    dependent_type: str
    jsonpath: str | None = None
    cache_data: str | None = None
    set_cache: str | None = None
    replace_key: str | None = None


class TearDownCaseData(BaseModel):
    """用例后置参数"""

    case_id: str
    teardown_data: List[TearDownData] | None = None


class AssertParam(BaseModel):
    """断言参数"""

    jsonpath: str
    type: AssertMethod
    value: Union[str, int, float, bool]


class TestcaseParams(BaseModel):
    """测试用例参数"""

    url: str
    method: MethodType
    description: str
    headers: Dict
    request_type: RequestType
    assert_data: Dict[str, AssertParam]
    is_run: bool | None = None
    data: Dict | None = None
    store_cache: List[StoreCache] | None = None
    is_dependence: bool | None = None
    dependence_case: List[DependentCaseData] | None = None
    teardown: List[TearDownCaseData] | None = None

    class Config:
        # 添加 json_encoders，用于序列化自定义类型
        json_encoders = {
            AssertParam: lambda v: v.dict(),
            AssertMethod: lambda v: v.value,
        }
