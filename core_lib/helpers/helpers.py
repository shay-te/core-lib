import os
import re
from hydra._internal.hydra import GlobalHydra
from hydra.experimental import compose, initialize


def valid_email(email):
    return bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email))


def compose_configuration(config_dir, config_file, caller_stack_depth=2, config_override: list = []):
    if GlobalHydra().is_initialized():
        GlobalHydra().clear()
    initialize(config_dir=config_dir, strict=True, caller_stack_depth=caller_stack_depth)
    return compose(config_file, config_override)


def compose_to_target_file(source_file, target_file, caller_stack_depth=3, config_override: list = []):
    source_file_name = os.path.basename(source_file)
    config = compose_configuration(source_file[::-len(source_file_name)],
                                   source_file_name,
                                   caller_stack_depth=caller_stack_depth,
                                   config_override=config_override)

    with open(os.path.join(target_file), 'w') as the_compose_file:
        the_compose_file.write(config.pretty())
