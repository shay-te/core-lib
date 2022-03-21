import enum

from core_lib.helpers.shell_utils import input_str, input_yes_no
from core_lib.helpers.string import any_to_camel


class DataAccessTypes(enum.Enum):
    __order__ = 'CRUD CRUDSoftDelete CRUDSoftDeleteToken'
    CRUD = 1
    CRUDSoftDelete = 2
    CRUDSoftDeleteToken = 3


def _generate_data_access_config(
    name: str,
    entity_name: str,
    db_conn: str,
    crud: bool = False,
    crud_soft_delete: bool = False,
    crud_soft_delete_token: bool = False,
) -> dict:
    if crud_soft_delete_token:
        return {
            'name': name,
            'entity': entity_name,
            'db_connection': db_conn,
            'is_crud': True,
            'is_crud_soft_delete': True,
            'is_crud_soft_delete_token': True,
        }
    elif crud_soft_delete:
        return {
            'name': name,
            'entity': entity_name,
            'db_connection': db_conn,
            'is_crud': True,
            'is_crud_soft_delete': True,
        }
    elif crud:
        return {
            'name': name,
            'entity': entity_name,
            'db_connection': db_conn,
            'is_crud': True,
        }
    else:
        return {
            'name': name,
            'entity': entity_name,
            'db_connection': db_conn,
        }


def generate_data_access_template(db_entities: dict) -> dict:
    data_access = {}
    for db_conn in db_entities:
        for entity in db_entities[db_conn]:
            if entity == 'migrate':
                continue
            default = (
                f'{entity.capitalize()}DataAccess' if f'{entity.capitalize()}DataAccess' not in data_access else None
            )
            data_access_name = any_to_camel(
                input_str(
                    f'Please enter the name of the data access you\'d want to create for entity `{entity}` (DB Connection: {db_conn})',
                    default,
                )
            )
            while data_access_name in data_access:
                data_access_name = any_to_camel(
                    input_str(
                        f'Data access with name `{data_access_name}` already present, please enter another namefor entity `{entity}` (DB Connection: {db_conn})',
                        default,
                    )
                )
            if db_entities[db_conn][entity]['is_soft_delete'] and db_entities[db_conn][entity]['is_soft_delete_token']:
                is_crud_soft_delete_token = input_yes_no(
                    'Do you want to implement CRUD Soft Delete Token on your data access?', True
                )
                if is_crud_soft_delete_token:
                    data_access[data_access_name] = _generate_data_access_config(
                        data_access_name, entity, db_conn, True, True, True
                    )
                else:
                    data_access[data_access_name] = _generate_data_access_config(data_access_name, entity, db_conn)
            elif (
                db_entities[db_conn][entity]['is_soft_delete']
                and not db_entities[db_conn][entity]['is_soft_delete_token']
            ):
                is_crud_soft_delete = input_yes_no(
                    'Do you want to implement CRUD Soft Delete on your data access?', True
                )
                if is_crud_soft_delete:
                    data_access[data_access_name] = _generate_data_access_config(
                        data_access_name, entity, db_conn, True, True
                    )
                else:
                    data_access[data_access_name] = _generate_data_access_config(data_access_name, entity, db_conn)
            else:
                is_crud = input_yes_no('Do you want to implement CRUD on your data access?', True)
                if is_crud:
                    data_access[data_access_name] = _generate_data_access_config(
                        data_access_name, entity, db_conn, True
                    )
                else:
                    data_access[data_access_name] = _generate_data_access_config(data_access_name, entity, db_conn)
    print(f'{list(data_access.keys())} created')
    return data_access
