#!/usr/bin/env python
import logging
import os
from core_lib.alembic.alembic import Alembic
from hydra import compose, initialize
from core_lib_template.core_lib_generate import CoreLibGenerate
import click

from core_lib.helpers.validation import is_int


def list_to_string(lst: list):
    name = ''
    for n in lst:
        name = name + n + ' '
    return name


def on_create(value):
    CoreLibGenerate().new(list_to_string(value))


def on_generate(value):
    CoreLibGenerate().generate(list_to_string(value))



def get_rev_options():
    choices = ['head', 'base', 'new']
    for i in range(-10, 11):
        if i != 0:
            choices.append(str(i))
            if i > 0:
                choices.append(f'+{str(i)}')
    return choices


def load_config():
    path_cwd = os.getcwd()
    path_folder = os.path.dirname(os.path.abspath(__file__))
    path_rel = os.path.relpath(path_cwd, path_folder)
    # initialize(config_path=os.path.join(path_rel))
    initialize(config_path=path_rel)
    return compose('core_lib_config.yaml')

#
# def main():
#     parser = argparse.ArgumentParser(description="Core-Lib")
#     g = parser.add_mutually_exclusive_group()
#     g.add_argument('-c', '--create', nargs=1, help='Create new core-lib')
#     g.add_argument('-g', '--generate', nargs=1, help='Generate core-lib classes')
#     g.add_argument('-r', '--revision', nargs=1, choices=get_rev_options(), help=f'Database migration.')
#     args = parser.parse_args()
#     if args.create:
#         on_create(args.create)
#     elif args.generate:
#         on_generate(args.generate)
#     elif args.revision:
#         on_revision(args.revision)
#     else:
#         print(parser.print_help())


@click.group()
def main():
    pass

@click.command()
def create():
    click.echo('Initialized the database')

@click.command()
def generate():
    click.echo('Dropped the database')

@click.command()
@click.option('--rev', help=' '.join(get_rev_options()))
@click.option('--name', help='name of new revision')
def migrate(rev, name):
    config = load_config()
    alembic = Alembic(os.path.join(os.getcwd(), config.core_lib_module), config)
    logging.getLogger('alembic').setLevel(logging.INFO)

    if rev == 'head':
        click.echo(f'revision to `{rev}`')
        alembic.upgrade('head')
    elif rev == 'base':
        click.echo(f'revision to `{rev}`')
        alembic.downgrade('base')
    elif is_int(rev):
        click.echo(f'revision to `{rev}`')
        number = int(rev)
        if number >= 0:
            alembic.upgrade('+{}'.format(number))
        else:
            alembic.downgrade(str(number))
    elif rev == 'new':
        if name:
            click.echo(f'new revision named `{name}`')
            click.echo(f'\n\n\n------------{os.environ["POSTGRES_USER"]}')
            alembic.create_migration(name)
        else:
            click.echo(f'--name parameter is mandatory when creating a new revision')

main.add_command(create)
main.add_command(generate)
main.add_command(migrate)
