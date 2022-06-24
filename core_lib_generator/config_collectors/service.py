import enum

from core_lib.helpers.shell_utils import input_str, input_yes_no, input_list
from core_lib.helpers.string import any_to_pascal
from core_lib_generator.generator_utils.helpers import is_exists, input_function


def generate_service_template(data_access: list, ask_cache: bool) -> list:
    service = []

    def is_exists_service(user_input: str):
        return is_exists(user_input, service)

    data_access_list = []
    if data_access:
        for da in data_access:
            data_access_list.append(da['key'])
    add_service = True
    while add_service:
        da_input = input_list(data_access_list, 'Select the Data Access to create service for')
        da_name = data_access_list[da_input]
        service_name = any_to_pascal(
            input_str(
                f'What is the name of the service? [Eg. UpdateService, ChatService]',
                None,
                False,
                is_exists_service,
                'Service name already exists'
            )
        )
        functions = []

        def is_exists_function(user_input: str) -> bool:
            return is_exists(user_input, functions)

        add_function = input_yes_no('Do you want to add a function to your service?', True)
        while add_function:
            functions.append(
                input_function(ask_cache, is_exists_function)
            )
            add_function = input_yes_no('Do you want to add another function to your service?', True)

        service.append(
            {
                'key': service_name,
                'data_access': da_name,
                'functions': functions,
            }
        )
        add_service = input_yes_no('Do you want to add another service?', True)
    return service
