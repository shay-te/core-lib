from abc import ABC, abstractmethod


class TemplateGenerate(ABC):
    @abstractmethod
    def handle(self, template_file: str, yaml_data: dict, core_lib_name: str):
        pass

    @abstractmethod
    def get_template_file(self, yaml_data: dict) -> str:
        pass
