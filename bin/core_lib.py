#!/usr/bin/env python
import os
import string
import argh

core_lib_file_name = '.core_lib'


def _name_to_safe(inputFilename: str):
    safechars = string.ascii_letters + "_"
    try:
        return ''.join(filter(lambda c: c in safechars, inputFilename.replace('-', '_')))
    except:
        return None


def _new_file(file_path, content: str = ''):
    with open(file_path, "w") as f:
        f.write(content)
        f.close()


def _new_dir(dir_path):
    os.mkdir(dir_path)
    _new_file(os.path.join(dir_path, '__init__.py'))


def _to_camel_case(snake_str):
    return ''.join(x.title() for x in snake_str.split('_'))


def _to_core_lib_class(core_lib_class):
    return """from omegaconf import DictConfig
from core_lib.core_lib import CoreLib


class {}(CoreLib):

    def __init__(self, conf: DictConfig):
        self.config = conf      

""".format(core_lib_class)


current_dir = os.getcwd()


def _create_core_lib(safe_file_name):
    core_lib_dir = os.path.join(current_dir, safe_file_name)

    _new_dir(core_lib_dir)
    _new_file(os.path.join(core_lib_dir, '{}.py'.format(safe_file_name)), _to_core_lib_class(_to_camel_case(safe_file_name)))

    # config
    config_dir = os.path.join(core_lib_dir, 'config')
    _new_dir(config_dir)
    _new_file(os.path.join(config_dir, '{}.yaml'.format(safe_file_name)))

    # data_layers
    data_layers = os.path.join(core_lib_dir, 'data_layers')
    _new_dir(data_layers)
    _new_dir(os.path.join(data_layers, 'data'))
    _new_dir(os.path.join(data_layers, 'data_access'))
    _new_dir(os.path.join(data_layers, 'service'))

    # core_lib file
    _new_file(os.path.join(current_dir, core_lib_file_name))


def _validate_new_core_lib(core_lib_name):
    if os.path.isfile(os.path.join(current_dir, core_lib_file_name)):
        raise ValueError('core_lib already exists in folder')

    if not core_lib_name:
        raise ValueError('core_lib_name not supplied')

    safe_file_name = _name_to_safe(core_lib_name)
    if not safe_file_name:
        raise ValueError('`{}` is not a python safe name'.format(core_lib_name))

    safe_file_name = safe_file_name.strip().lower()
    if not safe_file_name.endswith('core_lib'):
        if not safe_file_name.endswith('_'):
            safe_file_name = '{}_'.format(safe_file_name)
        safe_file_name = '{}core_lib'.format('safe_file_name')
    return safe_file_name


def new(core_lib_name):
    _create_core_lib(_validate_new_core_lib(core_lib_name))


parser = argh.ArghParser()
parser.add_commands([new])

if __name__ == '__main__':
    parser.dispatch()