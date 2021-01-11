#!/usr/bin/env python
import argparse
import logging
import os
from core_lib.alembic.alembic import Alembic
from hydra.experimental import compose, initialize_config_dir
from core_lib_template.core_lib_generate import CoreLibGenerate


from core_lib.helpers.validation import is_int

logger = logging.getLogger(__name__)


def list_to_string(lst: list):
    name = ''
    for n in lst:
        name = name + n + ' '
    return name


def on_create(value):
    CoreLibGenerate().new(list_to_string(value))


def on_generate(value):
    CoreLibGenerate().generate(list_to_string(value))


def on_revision(value):
    config = load_config()
    alembic = Alembic(os.path.join(os.getcwd(), config.core_lib_module), config)
    logging.getLogger('alembic').setLevel(logging.INFO)

    logger.info(f'revision to `{value}`')
    command = value.pop(0)

    if command == 'head':
        alembic.upgrade('head')
    elif command == 'base':
        alembic.downgrade('base')
    elif is_int(command):
        number = int(command)
        if number >= 0:
            alembic.upgrade('+{}'.format(number))
        else:
            alembic.downgrade(str(number))
    elif command == 'new':
        name = list_to_string(value)
        logger.info('creating new migrating named: `{}`'.format(name))
        alembic.create_migration(name)


def get_rev_options():
    choices = ['head', 'base', 'new']
    for i in range(-10, 11):
        if i != 0:
            choices.append(str(i))
            if i > 0:
                choices.append(f'+{str(i)}')
    return choices


def load_config():
    # path_cwd = os.getcwd()
    # path_folder = os.path.dirname(os.path.abspath(__file__))
    # path_rel = os.path.relpath(path_cwd, path_folder)
    # initialize(config_path=os.path.join(path_rel))
    initialize_config_dir(config_dir=os.getcwd())
    return compose('core_lib_config.yaml')


def main():
    parser = argparse.ArgumentParser(description="Core-Lib")
    g = parser.add_mutually_exclusive_group()
    g.add_argument('-c', '--create', nargs=1, help='Create new core-lib')
    g.add_argument('-g', '--generate', nargs=1, help='Generate core-lib classes')
    g.add_argument('-r', '--revision', nargs=1, choices=get_rev_options(), help=f'Database migration.')
    args = parser.parse_args()
    if args.create:
        on_create(args.create)
    elif args.generate:
        on_generate(args.generate)
    elif args.revision:
        on_revision(args.revision)
    else:
        print(parser.print_help())


if __name__ == '__main__':
    main()
