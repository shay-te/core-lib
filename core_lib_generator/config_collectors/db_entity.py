import enum

from core_lib.helpers.shell_utils import input_bool, input_str, input_int, input_enum, input_yes_no


def generate_db_entity_template(db: dict) -> list:
    entities = []
    for db_conn in db:
        def is_exists(user_input: str):
            for entity in entities:
                if entity['key'] == user_input and entity['db_connection'] == db_conn:
                    return False
            return True

        add_entity = input_yes_no(f'Do you want to add entities to `{db_conn}` db connection?', True)
        while add_entity:
            is_soft_delete = False
            is_soft_delete_token = False
            entity_name = input_str(
                'Enter the name of the database entity you\'d like to create', None, False, is_exists
            )
            columns = []
            if True:
                add_columns = input_yes_no(f'Do you want to add columns to `{entity_name}` entity?', True)

                def is_exists_column(user_input: str):
                    for column in columns:
                        if column['key'] == user_input:
                            return False
                    return True
                while add_columns:
                    column_name = input_str(f'Enter the name of column', None, False, is_exists_column)
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
            add_entity = input_yes_no(f'Do you want to add another entity to `{db_conn}`?', False)
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

# if __name__ == '__main__':
#     print(generate_db_entity_template({'userdb': {'db_connection': 'sql'}}))

if __name__ == '__main__':
    print({'db': input_str(f'Enter the default value of column', None, True, None, '', True)})