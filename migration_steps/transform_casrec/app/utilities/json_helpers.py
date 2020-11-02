import os


def get_mapping_file(file_name: str) -> str:
    dirname = os.path.dirname(__file__)
    file_path = os.path.join(dirname, f"../mapping_definitions/{file_name}.json")

    return file_path
