import enum

from core_lib.helpers.shell_utils import input_bool, input_str, input_int, input_enum, input_yes_no


def generate_db_entity_template(db: dict) -> dict:
    entities = {}
    for db_conn in db:
        if db[db_conn]['config']['url']['protocol'] == 'mongodb':
            continue
        entities.setdefault(db_conn, {})

        def is_exists(user_input: str):
            return False if user_input in entities[db_conn] else True

        add_entity = input_yes_no(f'Do you want to add entities to `{db_conn}` db connection?', True)
        while add_entity:
            is_soft_delete = False
            is_soft_delete_token = False
            entity_name = input_str(
                'Enter the name of the database entity you\'d like to create', None, False, is_exists
            )
            columns = {}
            add_columns = input_yes_no(f'Do you want to add columns to `{entity_name}` entity?', True)
            while add_columns:
                column_name = input_str(f'Enter the name of column')
                column_type = input_enum(
                    DBDatatypes,
                    f'From the following list, select the relevant number for datatype',
                    DBDatatypes.VARCHAR.value,
                )
                if column_type == DBDatatypes.INTEGER.value:
                    column_default = input_int(f'Enter the default value of column', 0)
                elif column_type == DBDatatypes.VARCHAR.value:
                    column_default = input_str(f'Enter the default value of column', '', True)
                else:
                    column_default = input_bool(
                        f'Enter the default value of column (true, false, 0(false), 1(true))', 'true'
                    )

                columns[column_name] = {
                    'type': DBDatatypes(column_type).name,
                    'default': column_default,
                }
                add_columns = input_yes_no(f'Do you want to add another column to `{entity_name}` entity?', True)
            is_soft_delete = input_yes_no('Do you want to implement Soft Delete?', False)
            if is_soft_delete:
                is_soft_delete_token = input_yes_no('Do you want to implement Soft Delete Token?', False)
            add_entity = input_yes_no(f'Do you want to add another entity to `{db_conn}`?', False)
            entities[db_conn][entity_name] = {
                'db_connection': db_conn,
                'columns': columns,
                'is_soft_delete': is_soft_delete,
                'is_soft_delete_token': is_soft_delete_token,
            }
        migrate = input_yes_no(f'Do you want to create a migration for `{db_conn}` entities?', False)
        entities[db_conn]['migrate'] = migrate
    return entities


class DBDatatypes(enum.Enum):
    __order__ = 'INTEGER VARCHAR BOOLEAN'
    INTEGER = 1
    VARCHAR = 2
    BOOLEAN = 3
