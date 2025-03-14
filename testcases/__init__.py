from common.setting import path_initializer
from utils.cases.case_files import get_all_files
from utils.caches.cache_control import CacheControl
from utils.cases.case_analysis import CaseData
from utils.logs.log_control import LOG


def write_case_process():
    """ 获取所有用例，写入用例缓存池中 """

    for file_path in get_all_files(path_initializer.yaml_path):
        case_process = CaseData(file_path).case_process(case_id_switch=True)
        for case in case_process:
            for case_id, case_info in case.items():
                if case_id in CacheControl.get_cache():
                    raise ValueError(
                        f"Duplicate case ID detected: {case_id}\n"
                        f"File path: {file_path}"
                    )
                CacheControl.update_cache(cache_name=case_id, value=case_info)
    LOG.info("\nWrite all testcases to the testcase pool successfully.")


write_case_process()