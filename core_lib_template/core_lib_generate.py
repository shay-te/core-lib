#!/usr/bin/env python
import os
import logging

import core_lib_template
from core_lib.helpers.command_line import input_yes_no, input_options_list, _to_safe_file_name, input_file_name
from core_lib.helpers.string import snake_to_camel

logger = logging.getLogger(__name__)

core_lib_file_name = 'core_lib_config.yaml'


def _to_test_simple(core_lib_name, core_lib_class_name):
    return """import os
import unittest
from hydra.experimental import initialize, compose
from {core_lib_name}.{core_lib_name} import {core_lib_class_name}


data_dir = os.path.join(os.path.dirname(__file__), 'data')
config_dir = os.path.join(data_dir, 'config')
seed_dir = os.path.join(data_dir, 'seed')
initialize(config_dir=config_dir)

interest_core_lib = {core_lib_class_name}(compose('config.yaml'))


class Test{core_lib_class_name}(unittest.TestCase):

    def test_1(self):
        pass
""".format(core_lib_name=core_lib_name, core_lib_class_name=core_lib_class_name)


def _get_file_contant(file_path: str):
    with open(file_path, 'r') as file:
        return file.read()


def _new_file(file_path, content: str = ''):
    if os.path.isfile(file_path) and os.path.exists(file_path):
        logger.info(f'File already exists {file_path}, Skiping')
    else:
        with open(file_path, "w") as f:
            f.write(content)
            f.close()


def _new_dir(dir_path, init_content: str = ''):
    if os.path.isdir(dir_path) and os.path.exists(dir_path):
        logger.info(f'Directory already exists {dir_path}, Skiping')
    else:
        os.mkdir(dir_path)
        _new_file(os.path.join(dir_path, '__init__.py'), init_content)


def _to_core_lib_class_db():
    return """
        db_data_session = SqlAlchemyDataHandlerRegistry(self.config.core_lib.data.sqlalchemy)
"""


def _to_entity_impl(table_name):
    return """from sqlalchemy import Column, Integer, VARCHAR

from core_lib.data_layers.data.db.sqlalchemy.base import Base


class {}(Base):

    __tablename__ = '{}'

    id = Column(Integer, primary_key=True, nullable=False)


""".format(table_name, snake_to_camel(table_name))


def _to_core_lib_search_path(core_lib_name):
    camel_case_name = snake_to_camel(core_lib_name)
    return """from hydra.plugins.search_path_plugin import SearchPathPlugin
from hydra.core.config_search_path import ConfigSearchPath


class {camel_case_name}SearchPathPlugin(SearchPathPlugin):
    def manipulate_search_path(self, search_path: ConfigSearchPath) -> None:
        assert isinstance(search_path, ConfigSearchPath)
        search_path.append("{core_lib_name}", "pkg://{core_lib_name}.config")
""".format(camel_case_name=camel_case_name, core_lib_name=core_lib_name)


def _to_core_lib_override_config(core_lib_name: str, core_lib_name_simple: str):
    return """# @package _global_
core_lib:
  data:
    sqlalchemy:
      session:
        pool_recycle: 3600
        pool_pre_ping: false

      url:
        protocol: sqlite
#        file: {core_lib_name}.db

      log_queries: false
      create_db: true
  alembic: 
    version_table: {core_lib_name_simple}_alembic_version

""".format(core_lib_name=core_lib_name, core_lib_name_simple=core_lib_name_simple)


def _to_script_mako():
    return """\"\"\"${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

\"\"\"
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}
"""


def _to_core_lib_config(core_lib_config_file, core_lib_test_config_file):
    return """defaults:
  - core_lib
  - {core_lib_config_file}
""".format(core_lib_config_file=core_lib_config_file)

def _to_test_config(core_lib_config_file, core_lib_test_config_file):
    return """defaults:
  - core_lib
  - {core_lib_config_file}
  - {core_lib_test_config_file}
""".format(core_lib_config_file=core_lib_config_file, core_lib_test_config_file=core_lib_test_config_file)

template_path = os.path.dirname(core_lib_template.__file__)
current_dir = os.getcwd()


def _copy_template(template_target_path: str, target_file: str, params: dict):
    file_content_raw = _get_file_contant(template_target_path)
    file_content = file_content_raw.format(**params)
    _new_file(target_file, file_content)


def _deep_copy_template(template_file_relative_path: str, start_dir: str, template_name: str, params: dict):
    template_target_path = os.path.abspath(os.path.join(template_path, template_file_relative_path))
    if not os.path.isfile(template_target_path):
        raise ValueError('`{}` template must lead to an existing file'.format(template_file_relative_path))

    folders = os.path.split(template_file_relative_path)
    target_dir = start_dir
    for folder in folders[:-1]:
        target_dir = os.path.join(target_dir, folder)
        if not os.path.isdir(target_dir):
            _new_dir(target_dir)

    _copy_template(template_target_path, os.path.join(target_dir, template_name), params)


def _create_core_lib(core_lib_name):
    core_lib_name_camel = snake_to_camel(core_lib_name)
    core_lib_dir = os.path.join(current_dir, core_lib_name)

    simple_end_index = core_lib_name.find('_core_lib')
    simple_end_index = simple_end_index if simple_end_index != -1 else core_lib_name.find('core_lib')

    core_lib_name_simple = core_lib_name if simple_end_index == -1 else core_lib_name[:simple_end_index]
    core_lib_name_simple_camel = snake_to_camel(core_lib_name_simple)

    # readme
    _new_file(os.path.join(current_dir, 'README.md'), _get_file_contant(os.path.join(template_path, 'README.md')).format(core_lib_name=core_lib_name_camel))

    # git ignore
    _new_file(os.path.join(current_dir, '.gitignore'), _get_file_contant(os.path.join(template_path, '.gitignore')))

    # core lib ddir
    _new_dir(core_lib_dir)
    _copy_template(os.path.abspath(os.path.join(template_path, os.path.join('template_core_lib.py'))), os.path.join(core_lib_dir, '{}.py'.format(core_lib_name)), {'core_lib_name_camel': core_lib_name_camel})

    # config
    config_dir = os.path.join(core_lib_dir, 'config')
    _new_dir(config_dir)
    _new_file(os.path.join(config_dir, '{}.yaml'.format(core_lib_name)), _to_core_lib_override_config(core_lib_name, core_lib_name_simple))

    # hydra_plugins search path
    hydra_plugin_init_content = ''
    hydra_plugin_dir = os.path.join(current_dir, 'hydra_plugins')
    _new_dir(hydra_plugin_dir, hydra_plugin_init_content)
    core_lib_hydra_plugin_dir = os.path.join(current_dir, 'hydra_plugins', core_lib_name)

    _new_dir(core_lib_hydra_plugin_dir, hydra_plugin_init_content)
    _new_file(os.path.join(core_lib_hydra_plugin_dir, '{}_searchpath.py'.format(core_lib_name)), _to_core_lib_search_path(core_lib_name))

    # tests
    test_dir = os.path.join(current_dir, 'tests')
    _new_dir(test_dir)
    test_data_dir = os.path.join(test_dir, 'data')
    _new_dir(test_data_dir)
    test_config_dir = os.path.join(test_dir, 'config')
    _new_dir(test_config_dir)
    test_config_file = 'test_{}'.format(core_lib_name)
    _new_file(os.path.join(test_config_dir, '{}.yaml'.format(test_config_file)), _to_core_lib_override_config(core_lib_name, core_lib_name_simple))
    _new_file(os.path.join(test_config_dir, 'config.yaml'), _to_test_config(core_lib_name, test_config_file))

    _new_file(os.path.join(test_dir, 'test_{}.py'.format(core_lib_name)), _to_test_simple(core_lib_name, core_lib_name_camel))


    # data_layers
    data_layers = os.path.join(core_lib_dir, 'data_layers')
    _new_dir(data_layers)
    _new_dir(os.path.join(data_layers, 'data'))
    _new_dir(os.path.join(data_layers, 'data', 'db'))
    _new_dir(os.path.join(data_layers, 'data', 'db', 'entities'))
    _new_dir(os.path.join(data_layers, 'data', 'db', 'migrations'))
    _new_file(os.path.join(data_layers, 'data', 'db', 'migrations', 'script.py.mako'), _to_script_mako())

    _new_dir(os.path.join(data_layers, 'data', 'db', 'migrations', 'versions'))

    _new_dir(os.path.join(data_layers, 'data_access'))
    _new_dir(os.path.join(data_layers, 'service'))

    # core_lib file

    _new_file(os.path.join(current_dir, core_lib_file_name), _to_core_lib_config(core_lib_name, test_config_file))


def _validate_new_core_lib(core_lib_name):
    if not core_lib_name:
        raise ValueError('core_lib_name not supplied')

    if os.path.isfile(os.path.join(current_dir, core_lib_name)):
        raise ValueError(f'core_lib `{core_lib_name}` already exists in folder `{current_dir}`')

    safe_file_name = _to_safe_file_name(core_lib_name)
    if not safe_file_name:
        raise ValueError('`{}` is not a python safe name'.format(core_lib_name))

    safe_file_name = safe_file_name.strip().lower()
    if not safe_file_name.endswith('core_lib'):
        if not safe_file_name.endswith('_'):
            safe_file_name = '{}_'.format(safe_file_name)
        safe_file_name = '{}core_lib'.format(safe_file_name)
    return safe_file_name


class CoreLibGenerate(object):
    def new(self, core_lib_name):
        _create_core_lib(_validate_new_core_lib(core_lib_name))

    def generate(self, core_lib_name):
        generate_name = input_file_name('select name')
        options = ['service, data access, entity', 'data access, entity', 'service', 'data access', 'entity']
        what = input_options_list('What would you like to generate', options)
        is_crud = input_yes_no('CRUD  support?', False)
        is_soft = input_yes_no('Soft delete')

        _deep_copy_template(os.path.join('core_lib_template/data_layers', 'data_access', 'template_data_access.py'), os.path.join(current_dir, core_lib_name), '{}.py'.format(generate_name), {})
