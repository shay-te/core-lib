from abc import ABC, abstractmethod


class TemplateGenerate(ABC):
    @abstractmethod
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        pass

    @abstractmethod
    def get_template_file(self, yaml_data: dict) -> str:
        pass
