from abc import ABC, abstractmethod


class TemplateGenerate(ABC):
    @abstractmethod
    def handle(self, template_path: str, yaml_data: dict):
        pass
