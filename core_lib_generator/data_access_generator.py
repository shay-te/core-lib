import os
import shutil

from core_lib.helpers.string import snake_to_camel
from core_lib_generator.generator_file_utils import replace_file_strings, replace_file_line


def _create_data_access(file_name: str, data_access_type: str, core_lib_name: str):
    template_class_name = snake_to_camel(data_access_type).replace('Crud', 'CRUD')
    da_file_name = f'{core_lib_name}/{core_lib_name}/data_layers/data_access/{file_name.lower()}.py'
    if not os.path.isfile(da_file_name):
        shutil.copy(
            f'{core_lib_name}/{core_lib_name}/data_layers/data_access/{data_access_type}.py',
            da_file_name,
        )
        replace_file_strings(
            da_file_name,
            f'{template_class_name}',
            f'{snake_to_camel(file_name)}',
        )


def add_data_access_instances(da_data: dict, core_lib_name: str):
    inst_list = []
    handler_list = []
    filename = f'{core_lib_name}/{core_lib_name}/{core_lib_name}.py'
    replace_file_line(
        filename,
        '# template_data_handlers_imports',
        'from core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry import SqlAlchemyDataHandlerRegistry',
    )
    for name in da_data:
        entity = da_data[name]['entity']
        db_connection = da_data[name]['db_connection']
        inst_str = f'self.{entity.lower()} = {snake_to_camel(name)}({entity.title()}, {db_connection}_session)'
        inst_list.append(inst_str.rjust(len(inst_str) + 8))
        handler_str = f'{db_connection}_session = SqlAlchemyDataHandlerRegistry(self.config.data.{db_connection})'
        handler_list.append(handler_str.rjust(len(handler_str) + 8))
    replace_file_line(filename, '# template_da_instances', '\n'.join(inst_list))
    replace_file_line(filename, '# template_data_handlers', '\n'.join(set(handler_list)))


def generate_data_access(data_access: dict, core_lib_name: str):
    data_access_list = list(data_access.keys())
    for name in data_access_list:
        if 'is_crud_soft_delete_token' in data_access[name]:
            _create_data_access(name, 'template_crud_soft_delete_token_data_access', core_lib_name)
        elif 'is_crud_soft_delete' in data_access[name]:
            _create_data_access(name, 'template_crud_soft_delete_data_access', core_lib_name)
        elif 'is_crud' in data_access[name]:
            _create_data_access(name, 'template_crud_data_access', core_lib_name)
        else:
            _create_data_access(name, 'template_data_access', core_lib_name)
