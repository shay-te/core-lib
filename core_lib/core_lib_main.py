#!/usr/bin/env python
import argparse
import logging
import os

import hydra
from omegaconf import DictConfig

from core_lib.alembic.alembic import Alembic
from hydra import compose, initialize_config_dir


from core_lib.helpers.validation import is_int
from core_lib_generator.core_lib_generator_from_yaml import CoreLibGenerator
from core_lib_generator.core_lib_config_generate_yaml import get_data_from_user

logger = logging.getLogger(__name__)

hydra.core.global_hydra.GlobalHydra.instance().clear()


def list_to_string(lst: list) -> str:
    return ' '.join(lst)


def on_create():
    get_data_from_user()


def on_generate(value):
    initialize_config_dir(config_dir=os.getcwd())
    CoreLibGenerator(compose(list_to_string(value))).run_all()
    print('Core-Lib Generated!')


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


def get_rev_options() -> list:
    choices = ['head', 'base', 'new']
    for i in range(-10, 11):
        if i != 0:
            choices.append(str(i))
            if i > 0:
                choices.append(f'+{str(i)}')
    return choices


def load_config() -> DictConfig:
    initialize_config_dir(config_dir=os.getcwd())
    return compose('core_lib_config.yaml')


def main():
    parser = argparse.ArgumentParser(description="Core-Lib")
    g = parser.add_mutually_exclusive_group()
    g.add_argument(
        '-c', '--create', action="append_const", const=get_data_from_user, help='Create new Core-Lib YAML file'
    )
    g.add_argument('-g', '--generate', nargs=1, help='Generate Core-Lib classes from YAML file')
    g.add_argument('-r', '--revision', nargs=1, choices=get_rev_options(), help='Database migration.')
    args = parser.parse_args()
    if args.create:
        for func in args.create:
            func()
    elif args.generate:
        on_generate(args.generate)
    elif args.revision:
        on_revision(args.revision)
    else:
        print(parser.print_help())


if __name__ == '__main__':
    main()
