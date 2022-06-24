import enum

from core_lib.data_transform.helpers import get_dict_attr
from core_lib.helpers.shell_utils import input_bool, input_str, input_int, input_enum, input_yes_no, input_list
from core_lib_generator.generator_utils.helpers import is_exists


def generate_db_entity_template(db: dict) -> list:
    entities = []

    def is_exists_entity(user_input: str) -> bool:
        for entity in entities:
            if entity.get('key') == user_input and entity.get('db_connection') == db_conn:
                return False
        return True
    db_conn_list = []
    for db_conn in db:
        db_conn_list.append(db_conn)
    add_entity = True
    while add_entity:
        db_conn = input_list(db_conn_list, 'Select the Connection to create Entity for')
        is_soft_delete = False
        is_soft_delete_token = False
        entity_name = input_str(
            'Enter the name of the database entity you\'d like to create', None, False, is_exists_entity
        )
        columns = []

        def is_exists_columns(user_input: str) -> bool:
            return is_exists(user_input, columns)
        add_columns = input_yes_no(f'Do you want to add columns to `{entity_name}` entity?', True)
        while add_columns:
            column_name = input_str(f'Enter the name of column', None, False, is_exists_columns)
            column_type = input_enum(
                DBDatatypes,
                f'From the following list, select the relevant number for datatype',
                DBDatatypes.VARCHAR.value,
            )
            if column_type == DBDatatypes.INTEGER.value:
                column_default = input_int(f'Enter the default value of column', None, True)
            elif column_type == DBDatatypes.VARCHAR.value:
                column_default = input_str(f'Enter the default value of column', None, True, None, '', True)
            else:
                column_default = input_bool(
                    f'Enter the default value of column (true, false, 0(false), 1(true))', None, True
                )
            nullable = input_yes_no('Do you want the column to be nullable', False)

            columns.append(
                {
                    'key': column_name,
                    'type': DBDatatypes(column_type).name,
                    'default': column_default,
                    'nullable': nullable,
                }
            )
            add_columns = input_yes_no(f'Do you want to add another column to `{entity_name}` entity?', True)
        is_soft_delete = input_yes_no('Do you want to implement Soft Delete?', False)
        if is_soft_delete:
            is_soft_delete_token = input_yes_no('Do you want to implement Soft Delete Token?', False)
        add_entity = input_yes_no(f'Do you want to add another entity?', False)
        entities.append(
            {
                'key': entity_name,
                'db_connection': db_conn,
                'columns': columns,
                'is_soft_delete': is_soft_delete,
                'is_soft_delete_token': is_soft_delete_token,
            }
        )
    return entities


class DBDatatypes(enum.Enum):
    __order__ = 'INTEGER VARCHAR BOOLEAN'
    INTEGER = 1
    VARCHAR = 2
    BOOLEAN = 3
