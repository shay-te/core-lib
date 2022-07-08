import enum

from core_lib.helpers.shell_utils import input_str, input_yes_no, input_list
from core_lib.helpers.string import any_to_pascal
from core_lib_generator.generator_utils.helpers import is_exists


def generate_data_access_template(db_entities: list) -> list:
    data_access = []

    def is_exists_data_access(user_input: str):
        return is_exists(user_input, data_access)

    entity_list = []
    if db_entities:
        for entity in db_entities:
            name = entity['key']
            conn = entity['db_connection']
            entity_list.append(f'{name} -> {conn}')
        add_da = True
        while add_da:
            entity_input = input_list(entity_list, 'Select the Entity to create DataAccess for')
            entity_data = db_entities[entity_input]
            entity_name = entity_data.get('key')
            db_conn = entity_data.get('db_connection')
            default = (
                f'{any_to_pascal(entity_name)}DataAccess'
                if is_exists_data_access(f'{any_to_pascal(entity_name)}DataAccess')
                else None
            )
            data_access_name = any_to_pascal(
                input_str(
                    f'What is the name of the data access? (Database connection: {db_conn}, Entity: {entity_name})',
                    default,
                    False,
                    is_exists_data_access,
                )
            )
            functions = []

            def is_exists_function(user_input: str) -> bool:
                return is_exists(user_input, functions)

            add_function = input_yes_no('Do you want to add a function to your data access?', True)
            while add_function:
                functions.append({
                    'key': input_str('What is the name of the function?', None, False, is_exists_function,
                                     'Function with this name already exists')
                })
                add_function = input_yes_no('Do you want to add another function to your data access?', True)
            is_crud_soft_delete_token = False
            is_crud_soft_delete = False
            if entity_data.get('is_soft_delete') and entity_data.get('is_soft_delete_token'):
                is_crud_soft_delete_token = input_yes_no(
                    'Do you want to implement CRUD Soft Delete Token on your data access?', False
                )
                is_crud_soft_delete = is_crud_soft_delete_token
                is_crud = is_crud_soft_delete_token
            elif entity_data.get('is_soft_delete') and not entity_data.get('is_soft_delete_token'):
                is_crud_soft_delete = input_yes_no(
                    'Do you want to implement CRUD Soft Delete on your data access?', False
                )
                is_crud = is_crud_soft_delete
            else:
                is_crud = input_yes_no('Do you want to implement CRUD on your data access?', False)

            data_access.append(
                _generate_data_access_config(
                    data_access_name, functions, entity_name, db_conn, is_crud, is_crud_soft_delete,
                    is_crud_soft_delete_token
                )
            )
            add_da = input_yes_no('Do you want to add another DataAccess?', True)
    return data_access


class DataAccessTypes(enum.Enum):
    __order__ = 'CRUD CRUDSoftDelete CRUDSoftDeleteToken'
    CRUD = 1
    CRUDSoftDelete = 2
    CRUDSoftDeleteToken = 3


def _generate_data_access_config(
        data_access_name: str,
        functions: list,
        entity_name: str,
        db_conn: str,
        crud: bool = False,
        crud_soft_delete: bool = False,
        crud_soft_delete_token: bool = False,
) -> dict:
    config = {
        'key': data_access_name,
        'entity': entity_name,
        'functions': functions,
        'db_connection': db_conn,
    }
    if crud_soft_delete_token:
        config.update({
            'is_crud': True,
            'is_crud_soft_delete': True,
            'is_crud_soft_delete_token': True,
        })
        return config
    elif crud_soft_delete:
        config.update({
            'is_crud': True,
            'is_crud_soft_delete': True,
        })
        return config
    elif crud:
        config.update({
            'is_crud': True,
        })
        return config
    else:
        return config
