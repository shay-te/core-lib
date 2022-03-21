from pytimeparse import parse

from core_lib.helpers.shell_utils import input_str
from core_lib.helpers.string import any_to_camel


def generate_job_template() -> dict:
    name = input_str('Enter the name of the job', 'my_job')
    class_name = any_to_camel(input_str('Please enter the Class Name for the job (UpdateCache)'))
    initial_delay = input_str(
        'Please set the initial delay for the job (boot, startup, 1s, 1m, 1h, 1h30m ...)', 'startup'
    )
    if initial_delay in ['boot', 'startup']:
        initial_delay = '0s'
    while parse(initial_delay) is None:
        initial_delay = input_str(
            'Please input a relevant value for initial delay (boot, startup, 1s, 1m, 2m ...)', '1m'
        )
    frequency = input_str('Please set the frequency of the job (1s, 1m, 1h, 1h30m ...)', '', True)
    while frequency and parse(frequency) is None:
        frequency = input_str('Please input a relevant value for frequency (1s, 1m, 1h, 1h30m ...)', '', True)
    print(f'{name} job created')
    return {
        name: {
            'initial_delay': initial_delay,
            'frequency': frequency,
            'handler': {'_target_': f'core_lib.jobs.{class_name}'},
        }
    }
