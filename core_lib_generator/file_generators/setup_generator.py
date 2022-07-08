from core_lib.data_transform.helpers import get_dict_attr
from core_lib_generator.file_generators.template_generator import TemplateGenerator


class SetupGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        updated_file = template_content.replace('# template_core_lib_import', f'import {core_lib_name}')
        updated_file = updated_file.replace('# template_core_lib_version', f'version={core_lib_name}.__version__,')
        updated_file = updated_file.replace('template_core_lib', core_lib_name)
        updated_file = updated_file.replace('template_full_name', get_dict_attr(yaml_data, 'author'))
        updated_file = updated_file.replace('template_email', get_dict_attr(yaml_data, 'author_email'))
        updated_file = updated_file.replace('template_description', get_dict_attr(yaml_data, 'description'))
        updated_file = updated_file.replace('template_url', get_dict_attr(yaml_data, 'url'))
        classifiers_list = yaml_data['classifiers']
        classifiers_str = f'classifiers={classifiers_list},'
        updated_file = updated_file.replace('# template_classifiers', classifiers_str)
        if get_dict_attr(yaml_data, 'license') == 'MIT':
            updated_file = updated_file.replace('template_license', 'MIT')
        elif get_dict_attr(yaml_data, 'license') == 'APACHE_LICENSE_2':
            updated_file = updated_file.replace('template_license', 'Apache-2.0')
        elif get_dict_attr(yaml_data, 'license') == 'MOZILLA_PUBLIC_LICENSE_2':
            updated_file = updated_file.replace('template_license', 'MPL-2.0')
        return updated_file

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/setup.py'
