import re
import datetime
import random
import string
from random import randint
from faker import Faker
from utils.logs.log_control import LOG
from utils.caches.cache_control import CacheControl


class CommonContext:
    def __init__(self):
        self.f = Faker(locale="en_US")

    @property
    def faker_app_name(self) -> str:
        length = random.randint(1, 26)
        # characters = string.ascii_letters + string.digits + string.punctuation
        characters = string.ascii_letters + string.digits
        return 'app_' + ''.join(self.f.random.choice(characters) for _ in range(length))

    @property
    def faker_app_description(self) -> str:
        return 'app_description_' + self.f.password(length=random.randint(8, 239), special_chars=False, digits=True, upper_case=True, lower_case=True)

    @property
    def faker_app_icon(self) -> str:
        return './appIcons/appIcon' + str(random.randint(1, 36)) + '.svg'

    @property
    def faker_dataset_name(self) -> str:
        length = random.randint(1, 12)
        characters = string.ascii_letters + string.digits
        return 'dataset_' + ''.join(self.f.random.choice(characters) for _ in range(length))

    @property
    def host(self) -> str:
        """ 获取项目域名 """
        from models import project_info
        return project_info.host

    @classmethod
    def get_current_time(self) -> datetime.datetime:
        """ 获取当前时间 """
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def url_replace(target):
    matches = re.findall(r"\$url_params\{(.*?)\}", target)
    if not matches:
        return target
    for match in matches:
        cache_key = match
        cache_value = CacheControl.get_cache(cache_key)
        if cache_value is not None:
            target = target.replace(f"$url_params{{{cache_key}}}", str(cache_value))
        else:
            LOG.warning(f"Warning: Cache not found for key: {cache_key}")
            return target
    return target

def regular_replace(target):
    try:
        regular_pattern = r"\${{(.*?)}}"
        while re.findall(regular_pattern, target):
            key = re.search(regular_pattern, target).group(1)
            target = re.sub(
                regular_pattern, str(getattr(CommonContext(), key)), target, 1
            )
        return target
    except AttributeError:
        LOG.error("未找到对应的替换的数据, 请检查数据是否正确", target)
        raise

def cache_replace(value):
    from utils.caches.cache_control import CacheControl

    """
    通过正则的方式，读取缓存中的内容
    例：$cache{login_init}
    :param value:
    :return:
    """
    matches = re.findall(r"\$cache\{(.*?)\}", value)
    if not matches:
        return value
    for match in matches:
        LOG.debug(f"match_data is : {match}")
        value_types = ["int:", "bool:", "list:", "dict:", "tuple:", "float:"]
        type_prefix = ""
        match_data = match
        if any(match.startswith(prefix) for prefix in value_types):
            type_prefix, match_data = match.split(":", 1)
            LOG.info(f"type_prefix is : {type_prefix}")
            pattern = re.compile(
                r"\'\$cache\{" + value_types.split(":")[0] + ":" + match_data + r"\}\'"
            )
        else:
            pattern = re.compile(
                r"\$cache\{" + match_data.replace("$", "\\$").replace("[", "\\[") + r"\}"
            )
        try:
            cache_data = CacheControl.get_cache(match_data)
            LOG.info(f"当前用例缓存数据为: => {match_data}: {cache_data}")
            # 使用sub方法，替换已经拿到的内容
            value = re.sub(pattern, str(cache_data), value)
        except Exception as e:
            LOG.error(f"Error fetching cache for {match_data}: {e}")
            continue
    return value
