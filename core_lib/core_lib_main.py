#!/usr/bin/env python
import logging
import os
from core_lib.alembic.alembic import Alembic
from hydra import compose, initialize
import click
from dotenv import load_dotenv
from core_lib.helpers.validation import is_int


def list_to_string(lst: list):
    name = ''
    for n in lst:
        name = name + n + ' '
    return name


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
    initialize(config_path=path_rel, version_base='1.1')
    return compose('core_lib_config.yaml')

@click.group()
def main():
    pass


@click.command()
@click.option('--rev', required=True, help=' '.join(get_rev_options()))
@click.option('--name', help='name of new revision')
@click.option('--env_file', help='what environment variable to load, default ".env"')
def migrate(rev, name, env_file):
    load_dotenv(os.path.abspath(env_file or '.env'))
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
            alembic.create_migration(name)
        else:
            click.echo(f'--name parameter is mandatory when creating a new revision')

# @click.command()
# @click.option('--value', help=' '.join(get_rev_options()))
# def create(value):
#     CoreLibGenerate().new(list_to_string(value))
#
# @click.command()
# @click.option('--value', help=' '.join(get_rev_options()))
# def generate(value):
#     CoreLibGenerate().generate(list_to_string(value))
#
# main.add_command(create)
# main.add_command(generate)
main.add_command(migrate)
