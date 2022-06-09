import enum

from core_lib.helpers.shell_utils import input_str, input_yes_no, input_function
from core_lib.helpers.string import any_to_pascal
from core_lib_generator.generator_utils.helpers import is_exists


def generate_service_template(data_access: list) -> list:
    service = []

    def is_exists_service(user_input: str):
        return is_exists(user_input, service)

    if data_access:
        for da in data_access:
            da_name = da['key']
            service_name = any_to_pascal(
                input_str(
                    f'What is the name of the service? (DataAccess: {da_name}) [Eg. UpdateService]',
                    None,
                    False,
                    is_exists_service,
                )
            )
            functions = []

            def is_exists_function(user_input: str) -> bool:
                return is_exists(user_input, functions)

            add_function = input_yes_no('Do you want to add a function to your service?', True)
            while add_function:
                functions.append(
                    input_function(is_exists_function)
                )
                add_function = input_yes_no('Do you want to add another function to your service?', True)

            service.append(
                {
                    'key': service_name,
                    'data_access': da_name,
                    'functions': functions,
                }
            )
    return service
