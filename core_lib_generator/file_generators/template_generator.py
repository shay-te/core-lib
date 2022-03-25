from abc import ABC, abstractmethod


class TemplateGenerator(ABC):
    @abstractmethod
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        pass

    @abstractmethod
    def get_template_file(self, yaml_data: dict) -> str:
        pass

    def exclude_init_from_dirs(self) -> list:
        return []
