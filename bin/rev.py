#!/usr/bin/env python
import os
import sys

# parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(os.path.join(parent_dir, 'core_lib'))
# sys.path.append(parent_dir)
# print(sys.path)


from hydra.experimental import compose, initialize
from core_lib.alembic.alembic import Alembic
from core_lib.helpers.primitive_utils import is_int

alembic = None

def head():
    alembic.upgrade('head')


def base():
    alembic.downgrade('base')


def new(*args):
    name = ''
    for n in args:
        name = name + n + ' '
    alembic.create_migration(name)


def number(number):
    if number >= 0:
        alembic.upgrade('+{}'.format(number))
    else:
        alembic.downgrade(str(number))


def print_help():
    for key, value in options.items():
        print('`{}`: {}'.format(key, value['help']))


options = {
    'head': {'callback': head, 'help': 'migrate to `head` revision'},
    'base': {'callback': base, 'help': 'migrate to `base` revision'},
    'new': {'callback': new, 'help': 'create new revision'},
    'NUM': {'callback': number, 'help': 'migrate to relative revision by number'},
}


if __name__ == '__main__':
    initialize(config_dir=os.path.join(os.getcwd(), 'config'), strict=True)
    cfg = compose('app_config.yaml')
    alembic = Alembic(os.path.join(os.getcwd(), cfg.core_lib_module), cfg)

    if len(sys.argv) > 1:
        target = None
        command = sys.argv[1]
        parameter = sys.argv[2:]
        if command in options:
            options[command]['callback'](*parameter)
        elif is_int(command):
            number = int(command)
            options['NUM']['callback'](number)
        else:
            print_help()
    else:
        print_help()
