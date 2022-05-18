import enum

from core_lib.helpers.shell_utils import input_str, input_yes_no
from core_lib.helpers.string import any_to_pascal


def generate_data_access_template(db_entities: list) -> list:
    data_access = []

    def is_exists(user_input: str):
        for da in data_access:
            if da['key'] == user_input:
                return False
        return True

    if db_entities:
        for entity in db_entities:
            entity_name = entity['key']
            db_conn = entity['db_connection']
            default = (
                f'{any_to_pascal(entity_name)}DataAccess'
                if is_exists(f'{any_to_pascal(entity_name)}DataAccess')
                else None
            )
            data_access_name = any_to_pascal(
                input_str(
                    f'What is the name of the data access? (Database connection: {db_conn}, Entity: {entity_name})',
                    default,
                    False,
                    is_exists,
                )
            )
            is_crud_soft_delete_token = False
            is_crud_soft_delete = False
            if entity.get('is_soft_delete') and entity.get('is_soft_delete_token'):
                is_crud_soft_delete_token = input_yes_no(
                    'Do you want to implement CRUD Soft Delete Token on your data access?', False
                )
                is_crud_soft_delete = is_crud_soft_delete_token
                is_crud = is_crud_soft_delete_token
            elif entity.get('is_soft_delete') and not entity.get('is_soft_delete_token'):
                is_crud_soft_delete = input_yes_no(
                    'Do you want to implement CRUD Soft Delete on your data access?', False
                )
                is_crud = is_crud_soft_delete
            else:
                is_crud = input_yes_no('Do you want to implement CRUD on your data access?', False)

            data_access.append(
                _generate_data_access_config(
                    data_access_name, entity_name, db_conn, is_crud, is_crud_soft_delete, is_crud_soft_delete_token
                )
            )
    return data_access


class DataAccessTypes(enum.Enum):
    __order__ = 'CRUD CRUDSoftDelete CRUDSoftDeleteToken'
    CRUD = 1
    CRUDSoftDelete = 2
    CRUDSoftDeleteToken = 3


def _generate_data_access_config(
    data_access_name: str,
    entity_name: str,
    db_conn: str,
    crud: bool = False,
    crud_soft_delete: bool = False,
    crud_soft_delete_token: bool = False,
) -> dict:
    if crud_soft_delete_token:
        return {
            'key': data_access_name,
            'entity': entity_name,
            'db_connection': db_conn,
            'is_crud': True,
            'is_crud_soft_delete': True,
            'is_crud_soft_delete_token': True,
        }
    elif crud_soft_delete:
        return {
            'key': data_access_name,
            'entity': entity_name,
            'db_connection': db_conn,
            'is_crud': True,
            'is_crud_soft_delete': True,
        }
    elif crud:
        return {
            'key': data_access_name,
            'entity': entity_name,
            'db_connection': db_conn,
            'is_crud': True,
        }
    else:
        return {
            'key': data_access_name,
            'entity': entity_name,
            'db_connection': db_conn,
        }
