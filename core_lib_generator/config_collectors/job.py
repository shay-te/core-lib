from core_lib.helpers.shell_utils import input_str, input_timeframe, input_yes_no
from core_lib.helpers.string import any_to_pascal, camel_to_snake
from core_lib_generator.generator_utils.helpers import is_exists


def generate_job_template(core_lib_name: str) -> list:
    jobs = []
    add_job = True

    def is_exists_jobs(user_input: str) -> bool:
        return is_exists(user_input, jobs)

    while add_job:
        class_name = any_to_pascal(input_str('Please enter the Class Name for the job (CamelCase)', None, False, is_exists_jobs))
        snake_class_name = camel_to_snake(class_name)
        initial_delay = input_timeframe(
            'Please set the initial delay for the job (boot, startup, 1s, 1m, 1h, 1h30m ...)', 'startup'
        )
        frequency = input_timeframe('Please set the frequency of the job (1s, 1m, 1h, 1h30m ...)', '', True)
        add_job = input_yes_no('Do you want to add another job?', False)
        snake_core_lib_name = camel_to_snake(core_lib_name)
        jobs.append(
            {
                'key': snake_class_name,
                'initial_delay': initial_delay,
                'frequency': frequency,
                'handler': {
                    '_target_': f'{snake_core_lib_name}.{snake_core_lib_name}.jobs.{snake_class_name}.{class_name}'
                },
            }
        )
    return jobs
