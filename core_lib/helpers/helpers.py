import re
import os
from hydra._internal.hydra import GlobalHydra
from hydra.experimental import compose, initialize


def valid_email(email):
    return bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email))


def compose_configuration(config_dir, config_file, caller_stack_depth=2):
    config_override = os.environ['CONFIG_OVERRIDE'].split(',') if 'CONFIG_OVERRIDE' in os.environ else []
    if config_override:
        print('Overriding configuration with : {}'.format(config_override))
    if GlobalHydra().is_initialized():
        GlobalHydra().clear()
    initialize(config_dir=config_dir, strict=True, caller_stack_depth=caller_stack_depth)
    return compose(config_file, config_override)
