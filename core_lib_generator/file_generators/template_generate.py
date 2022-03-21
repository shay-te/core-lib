from abc import ABC, abstractmethod


class TemplateGenerate(ABC):
    @abstractmethod
    def handle(self, template_file: str, yaml_data: dict):
        pass

    @abstractmethod
    def get_template_data(self, yaml_data: dict) -> str:
        pass
