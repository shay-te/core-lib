#!/usr/bin/env python
import argparse
import logging
import os
from typing import Callable

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

    command = value.pop(0)
    logger.info(f'revision to `{command}`')

    if command == 'head':
        alembic.upgrade('head')
    elif command == 'base':
        alembic.downgrade('base')
    elif command == 'list':
        alembic.history()
    elif is_int(command):
        number = int(command)
        if number >= 0:
            alembic.upgrade(f'+{number}')
        else:
            alembic.downgrade(f'{number}')
    elif command == 'new':
        name = list_to_string(value)
        logger.info('creating new migrating named: `{}`'.format(name))
        alembic.create_migration(name)
    else:
        logger.error(f'unknown command `{command}`')


def get_rev_options() -> list:
    choices = ['head', 'base']
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
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Core-Lib")
    g = parser.add_mutually_exclusive_group()
    g.add_argument('-g', '--generate', nargs=1, help='Generate Core-Lib classes from YAML file')
    subparsers = parser.add_subparsers(dest='command')
    rev = subparsers.add_parser('rev', help='migration revision')
    rev.add_argument(
        '-m',
        '--migrate',
        help='Existing migration select from the list',
        choices=get_rev_options(),
        nargs=1,
    )
    rev.add_argument(
        '-n',
        '--new',
        help='New migration name to be created',
        nargs=1,
    )
    rev.add_argument(
        '-l',
        '--list',
        help='List of revisions',
        nargs='?',
        const='list'
    )
    args = parser.parse_args()
    if args.command == 'rev':
        if args.migrate:
            on_revision(args.migrate)
        elif args.new:
            on_revision(['new', args.new[0]])
        else:
            on_revision(['list'])
    elif args.generate:
        on_generate(args.generate)
    elif args.revision:
        on_revision(args.revision)
    else:
        print(parser.print_help())


if __name__ == '__main__':
    main()
