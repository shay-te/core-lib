from datetime import datetime

from core_lib.data_transform.helpers import get_dict_attr
from core_lib_generator.file_generators.template_generator import TemplateGenerator


class LicenseGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        author = get_dict_attr(yaml_data, 'author')
        copy_right = f'Copyright {datetime.utcnow().year} {author}'
        return template_content.replace('# template_copyright', copy_right)

    def get_template_file(self, yaml_data: dict) -> str:
        if yaml_data['license'] == 'MIT':
            return 'template_core_lib/LICENSE_MIT'
        elif yaml_data['license'] == 'APACHE_LICENSE_2':
            return 'template_core_lib/LICENSE_Apache-2'
        elif yaml_data['license'] == 'MOZILLA_PUBLIC_LICENSE_2':
            return 'template_core_lib/LICENSE_MPL-2'
