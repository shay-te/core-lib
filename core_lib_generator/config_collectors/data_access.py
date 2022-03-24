import enum

from core_lib.helpers.shell_utils import input_str, input_yes_no
from core_lib.helpers.string import any_to_camel


def generate_data_access_template(db_entities: dict) -> dict:
    data_access = {}

    def is_exists(user_input: str):
        return False if user_input in data_access else True

    for db_conn in db_entities:
        for entity in db_entities[db_conn]:
            if entity == 'migrate':
                continue
            default = (
                f'{any_to_camel(entity)}DataAccess' if f'{any_to_camel(entity)}DataAccess' not in data_access else None
            )
            data_access_name = any_to_camel(
                input_str(
                    f'What is the name of the data access? (Database connection: {db_conn}, Entity: {entity})',
                    default,
                    False,
                    is_exists,
                )
            )
            is_crud_soft_delete_token = False
            is_crud_soft_delete = False
            if db_entities[db_conn][entity]['is_soft_delete'] and db_entities[db_conn][entity]['is_soft_delete_token']:
                is_crud_soft_delete_token = input_yes_no(
                    'Do you want to implement CRUD Soft Delete Token on your data access?', False
                )
                is_crud_soft_delete = is_crud_soft_delete_token
                is_crud = is_crud_soft_delete_token
            elif (
                db_entities[db_conn][entity]['is_soft_delete']
                and not db_entities[db_conn][entity]['is_soft_delete_token']
            ):
                is_crud_soft_delete = input_yes_no(
                    'Do you want to implement CRUD Soft Delete on your data access?', False
                )
                is_crud = is_crud_soft_delete
            else:
                is_crud = input_yes_no('Do you want to implement CRUD on your data access?', False)

            data_access[data_access_name] = _generate_data_access_config(
                entity, db_conn, is_crud, is_crud_soft_delete, is_crud_soft_delete_token
            )
    print(f'{list(data_access.keys())} created')
    return data_access


class DataAccessTypes(enum.Enum):
    __order__ = 'CRUD CRUDSoftDelete CRUDSoftDeleteToken'
    CRUD = 1
    CRUDSoftDelete = 2
    CRUDSoftDeleteToken = 3


def _generate_data_access_config(
    entity_name: str,
    db_conn: str,
    crud: bool = False,
    crud_soft_delete: bool = False,
    crud_soft_delete_token: bool = False,
) -> dict:
    if crud_soft_delete_token:
        return {
            'entity': entity_name,
            'db_connection': db_conn,
            'is_crud': True,
            'is_crud_soft_delete': True,
            'is_crud_soft_delete_token': True,
        }
    elif crud_soft_delete:
        return {
            'entity': entity_name,
            'db_connection': db_conn,
            'is_crud': True,
            'is_crud_soft_delete': True,
        }
    elif crud:
        return {
            'entity': entity_name,
            'db_connection': db_conn,
            'is_crud': True,
        }
    else:
        return {
            'entity': entity_name,
            'db_connection': db_conn,
        }
