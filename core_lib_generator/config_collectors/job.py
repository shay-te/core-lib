from core_lib.helpers.shell_utils import input_str, input_timeframe
from core_lib.helpers.string import any_to_camel, camel_to_snake


def generate_job_template(core_lib_name: str) -> dict:
    class_name = any_to_camel(input_str('Please enter the Class Name for the job (CamelCase)'))
    snake_class_name = camel_to_snake(class_name)
    initial_delay = input_timeframe(
        'Please set the initial delay for the job (boot, startup, 1s, 1m, 1h, 1h30m ...)', 'startup'
    )
    frequency = input_timeframe('Please set the frequency of the job (1s, 1m, 1h, 1h30m ...)', '', True)
    print(f'{snake_class_name} job created')
    return {
        snake_class_name: {
            'initial_delay': initial_delay,
            'frequency': frequency,
            'handler': {'_target_': f'{camel_to_snake(core_lib_name)}.core_lib.jobs.{snake_class_name}.{class_name}'},
        }
    }
