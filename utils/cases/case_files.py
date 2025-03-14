import os

def get_all_files(file_path, yaml_data_switch=True) -> list:
    """ 获取指定目录下的所有文件路径 """

    files_list = []
    for root, _, files in os.walk(file_path):
        for file in files:
            full_path = os.path.join(root, file)
            if yaml_data_switch:
                # 获取所有的yaml case
                if file.lower().endswith(('.yaml', '.yml')):
                    files_list.append(full_path)
            else:
                files_list.append(full_path)
    return sorted(files_list)
