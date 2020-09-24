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


def _new_dir(dir_path, init_content: str = ''):
    os.mkdir(dir_path)
    _new_file(os.path.join(dir_path, '__init__.py'))


def _to_camel_case(snake_str):
    return ''.join(x.title() for x in snake_str.split('_'))


def _to_core_lib_class(core_lib_name):
    return """from core_lib.data_layers.data.data_helpers import build_url
from core_lib.data_layers.data.handler.db_data_session_factory import SqlAlchemyDataHandlerFactory
    from omegaconf import DictConfig
from core_lib.core_lib import CoreLib


class {}(CoreLib):

    def __init__(self, conf: DictConfig):
        self.config = conf      

""".format(_to_camel_case(core_lib_name))


def _to_core_lib_class_db():
    return """
        engine = create_engine(build_url(**self._config.core_lib.data.sqlalchemy.url),
                               pool_recycle=self._config.core_lib.data.sqlalchemy.handler.pool_recycle,
                               echo=self._config.core_lib.data.sqlalchemy.log_queries)
        engine.connect()
        db_data_session = SqlAlchemyDataHandlerFactory(engine)    
"""



def _to_entity_impl(table_name):
    return """from sqlalchemy import Column, Integer, VARCHAR

from core_lib.data_layers.data.db.sqlalchemy.base import Base


class {}(Base):

    __tablename__ = '{}'

    id = Column(Integer, primary_key=True, nullable=False)


""".format(table_name, _to_camel_case(table_name))


def _to_core_lib_search_path(core_lib_name):
    canel_case_name = _to_camel_case(core_lib_name)
    return """from hydra.plugins import SearchPathPlugin
from hydra._internal.config_search_path import ConfigSearchPath


class {}SearchPathPlugin(SearchPathPlugin):
    def manipulate_search_path(self, search_path):
        assert isinstance(search_path, ConfigSearchPath)
        search_path.append("{}", "pkg://{}/config")
""".format(canel_case_name, core_lib_name, core_lib_name)


def _to_core_lib_override_config(core_lib_name):
    return """core_lib:
""".format(core_lib_name)

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


current_dir = os.getcwd()


def _create_core_lib(core_lib_name):
    core_lib_dir = os.path.join(current_dir, core_lib_name)

    _new_dir(core_lib_dir)
    core_lib_file_content = '{}{}'.format(_to_core_lib_class(core_lib_name), _to_core_lib_class_db())
    _new_file(os.path.join(core_lib_dir, '{}.py'.format(core_lib_name)), core_lib_file_content)


    # config
    config_dir = os.path.join(core_lib_dir, 'config')
    _new_dir(config_dir)
    _new_file(os.path.join(config_dir, '{}.yaml'.format(core_lib_name)), _to_core_lib_override_config(core_lib_name))

    # hydra_plugins search path
    hydra_plugin_dir = os.path.join(current_dir, 'hydra_plugins')
    _new_dir(hydra_plugin_dir, '__path__ = __import__("pkgutil").extend_path(__path__, __name__)')
    _new_file(os.path.join(hydra_plugin_dir, '{}_searchpath.py'.format(core_lib_name)), _to_core_lib_search_path(core_lib_name))

    # tests
    tests_dir = os.path.join(current_dir, 'tests')
    _new_dir(tests_dir)

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
        safe_file_name = '{}core_lib'.format(safe_file_name)
    return safe_file_name


def new(core_lib_name):
    _create_core_lib(_validate_new_core_lib(core_lib_name))


parser = argh.ArghParser()
parser.add_commands([new])

if __name__ == '__main__':
    parser.dispatch()
