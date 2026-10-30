"""A project made by `core_lib generate` builds its CoreLib twice in one process and its own tests pass."""
import contextlib
import datetime
import keyword
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from click.testing import CliRunner
from hydra.core.global_hydra import GlobalHydra
from omegaconf import OmegaConf

from core_lib.core_lib_main import main
from core_lib_generator.core_lib_generator_from_yaml import CoreLibGenerator
from core_lib_generator.file_generators.license_generator import LicenseGenerateTemplate
from core_lib_generator.file_generators.readme_generator import ReadmeGenerateTemplate
from core_lib_generator.generator_utils.naming_utils import service_attribute_name

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(REPO_ROOT, 'tests', 'test_data', 'generator')
SAMPLE_YAML = os.path.join(SAMPLES, 'AcmeCoreLib.yaml')
SOLR_FACTORY = 'core_lib.connection.solr_connection_factory.SolrConnectionFactory'
SQL_FACTORY = 'core_lib.connection.sql_alchemy_connection_factory.SqlAlchemyConnectionFactory'
MONGO_FACTORY = 'core_lib.connection.mongodb_connection_factory.MongoDBConnectionFactory'

# The CRUD DataAccess of each entity, created, deleted and read again against the project's real SQLite database.
INVENTORY_ROUND_TRIP = '''
from core_lib.error_handling.status_code_exception import StatusCodeException
from tests.test_data.helpers.util import load_config
from acme_inventory.acme_inventory import AcmeInventory
from acme_inventory.data_layers.data_access.gadget_report_data_access import GadgetReportDataAccess

acme_inventory = AcmeInventory(load_config())
for service in (acme_inventory.gadget, acme_inventory.widget_catalog):
    data_access = service._data_access
    row = data_access.create({'name': 'sprocket'})
    deleted = data_access.delete(row.id)
    try:
        data_access.get(row.id)
    except StatusCodeException as missing:
        print(type(data_access).__bases__[0].__name__, hasattr(row, 'deleted_at'), deleted, int(missing.status_code))
print(GadgetReportDataAccess.__bases__[0].__name__)
gadget = acme_inventory.gadget._data_access.create({'name': 'cog'})
print(repr(gadget.stock), repr(gadget.active), repr(gadget.label), repr(gadget.colour))
'''

# Built without a server: the Solr, Neo4j, Redis and Memcached clients connect on first use.
SEARCH_BUILD = '''
from core_lib.core_lib import CoreLib
from tests.test_data.helpers.util import load_config
from acme_search.acme_search import AcmeSearch

config = load_config()
AcmeSearch(config)
acme_search = AcmeSearch(config)
redis_server = CoreLib.cache_registry.get('sessions').redis_client.connection_pool.connection_kwargs
memcached_server = CoreLib.cache_registry.get('pages').memcached_client.servers[0]
print(type(CoreLib.cache_registry.get('sessions')).__name__, redis_server['host'], redis_server['port'])
print(type(CoreLib.cache_registry.get('pages')).__name__, memcached_server.ip, memcached_server.port)
print(type(acme_search._report_data_access).__name__, type(acme_search._search_data_access.session).__name__)
'''

SEARCH_CORE_LIB_SOURCE = (
    'from omegaconf import DictConfig\n'
    'from core_lib.core_lib import CoreLib\n'
    'from core_lib.data_layers.data.data_helpers import build_url\n'
    'from core_lib.cache.cache_handler_redis import CacheHandlerRedis\n'
    'from core_lib.cache.cache_handler_memcached import CacheHandlerMemcached\n'
    'from core_lib.helpers.config_instances import instantiate_config\n'
    'from core_lib.connection.neo4j_connection_factory import Neo4jConnectionFactory\n'
    'from acme_search.data_layers.data_access.search_data_access import SearchDataAccess\n'
    'from acme_search.data_layers.data_access.graph_data_access import GraphDataAccess\n'
    'from acme_search.data_layers.data_access.report_data_access import ReportDataAccess\n'
    'from acme_search.data_layers.data_access.audit_data_access import AuditDataAccess\n'
    '\n'
    '\n'
    'class AcmeSearch(CoreLib):\n'
    '    def __init__(self, conf: DictConfig):\n'
    '        super().__init__()\n'
    '        self.config = conf\n'
    '\n'
    "        if not CoreLib.cache_registry.get('sessions'):\n"
    "            CoreLib.cache_registry.register('sessions', "
    'CacheHandlerRedis(build_url(**self.config.core_lib.acme_search.cache.sessions.url)))\n'
    "        if not CoreLib.cache_registry.get('pages'):\n"
    "            CoreLib.cache_registry.register('pages', "
    'CacheHandlerMemcached(build_url(**self.config.core_lib.acme_search.cache.pages.url)))\n'
    '        search = instantiate_config(self.config.core_lib.acme_search.solr.search)\n'
    '        graph = Neo4jConnectionFactory(self.config.core_lib.acme_search.neo4j.graph)\n'
    '        self._search_data_access = SearchDataAccess(search)\n'
    '        self._graph_data_access = GraphDataAccess(graph)\n'
    '        self._report_data_access = ReportDataAccess()\n'
    '        self._audit_data_access = AuditDataAccess()\n'
)

GADGET_ENTITY_SOURCE = (
    'from sqlalchemy import Column, INTEGER, VARCHAR, BOOLEAN\n'
    '\n'
    'from core_lib.data_layers.data.db.sqlalchemy.base import Base\n'
    '\n'
    '\n'
    'class Gadget(Base):\n'
    "    __tablename__ = 'gadget'\n"
    '\n'
    '    id = Column(INTEGER, primary_key=True, nullable=False)\n'
    '    name = Column(VARCHAR, nullable=False, default=None)\n'
    '    stock = Column(INTEGER, nullable=True, default=0)\n'
    '    active = Column(BOOLEAN, nullable=False, default=False)\n'
    "    label = Column(VARCHAR, nullable=False, default='')\n"
    "    colour = Column(VARCHAR, nullable=False, default='grey')\n"
)

WIDGET_CATALOG_SOURCE = (
    'from core_lib.data_layers.service.service import Service\n'
    'from core_lib.cache.cache_decorator import Cache\n'
    'from core_lib.data_transform.result_to_dict import ResultToDict\n'
    'from acme_inventory.data_layers.data_access.widget_data_access import WidgetDataAccess\n'
    '\n'
    '\n'
    'class WidgetCatalog(Service):\n'
    "    CACHE_WIDGET = 'CACHE_WIDGET'\n"
    "    CACHE_WIDGET_LIST = 'CACHE_WIDGET_LIST'\n"
    '\n'
    '    def __init__(self, data_access: WidgetDataAccess):\n'
    '        self._data_access = data_access\n'
    '\n'
    '    @Cache(CACHE_WIDGET)\n'
    '    @ResultToDict()\n'
    '    def get_by_name(self):\n'
    '        pass\n'
    '\n'
    '    @Cache(CACHE_WIDGET, invalidate=True)\n'
    '    def rename_widget(self):\n'
    '        pass\n'
    '\n'
    '    def count_widgets(self):\n'
    '        pass\n'
    '\n'
    '    @Cache(CACHE_WIDGET_LIST)\n'
    '    def list_widgets(self):\n'
    '        pass\n'
)

MIT_LICENSE = (
    'MIT License\n'
    '\n'
    'Copyright {year} acme\n'
    '\n'
    'Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated '
    'documentation files (the "Software"), to deal in the Software without restriction, including without limitation '
    'the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and '
    'to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n'
    '\n'
    'The above copyright notice and this permission notice shall be included in all copies or substantial portions '
    'of the Software.\n'
    '\n'
    'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO '
    'THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE '
    'AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF '
    'CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER '
    'DEALINGS IN THE SOFTWARE.'
)

# Generates both samples in a fresh interpreter, whose str hash seed (PYTHONHASHSEED) the test chooses.
GENERATE_SAMPLES = '''
import sys
from omegaconf import OmegaConf
from core_lib_generator.core_lib_generator_from_yaml import CoreLibGenerator

for sample in sys.argv[1:]:
    CoreLibGenerator(OmegaConf.load(sample)).run_all()
'''

UNSUPPORTED_CONNECTION = (
    f'connection `docs` has an unsupported type `{MONGO_FACTORY}`; the generator supports '
    'SqlAlchemyConnectionFactory, SolrConnectionFactory, Neo4jConnectionFactory'
)

INVENTORY_SURFACE = '''
import inspect
from core_lib.data_layers.service.service import Service
from tests.test_data.helpers.util import load_config
from acme_inventory.acme_inventory import AcmeInventory
from acme_inventory.data_layers.service.widget_catalog import WidgetCatalog

config = load_config()
AcmeInventory(config)
acme_inventory = AcmeInventory(config)
print(type(acme_inventory.gadget).__name__, type(acme_inventory.widget_catalog).__name__,
      type(acme_inventory.status).__name__)
print(isinstance(acme_inventory.status, Service), vars(acme_inventory.status))
print(WidgetCatalog.CACHE_WIDGET)
for name in ('install', 'uninstall'):
    print(name, isinstance(AcmeInventory.__dict__[name], staticmethod),
          list(inspect.signature(getattr(AcmeInventory, name)).parameters))
'''


def generate_project(test_class, sample_yaml: str) -> str:
    output_folder = tempfile.mkdtemp()
    test_class.addClassCleanup(shutil.rmtree, output_folder)
    shutil.copy(sample_yaml, output_folder)
    original_cwd = os.getcwd()
    try:
        os.chdir(output_folder)
        result = CliRunner().invoke(main, ['generate', '--yaml', os.path.basename(sample_yaml)])
    finally:
        os.chdir(original_cwd)
        GlobalHydra.instance().clear()
    if result.exception:
        raise result.exception
    project_names = [name for name in os.listdir(output_folder) if not name.endswith('.yaml')]
    return os.path.join(output_folder, *project_names)


def run_python(project_root: str, *args) -> subprocess.CompletedProcess:
    # The project first: core-lib's own `tests` package must not hide the generated project's.
    environment = dict(os.environ, PYTHONPATH=os.pathsep.join([project_root, REPO_ROOT]))
    return subprocess.run(
        [sys.executable, *args], cwd=project_root, env=environment, capture_output=True, text=True, timeout=120
    )


def read(project_root: str, *path) -> str:
    with open(os.path.join(project_root, *path)) as generated_file:
        return generated_file.read()


def run_readme_example(project_root: str) -> subprocess.CompletedProcess:
    example = re.search(r'```python\n(.*?)```', read(project_root, 'README.md'), flags=re.S).group(1)
    with open(os.path.join(project_root, 'readme_example.py'), 'w') as example_file:
        example_file.write(example)
    return run_python(project_root, 'readme_example.py')


def generated_files(project_root: str):
    for folder, _, file_names in os.walk(project_root):
        for file_name in file_names:
            if file_name.endswith(('.py', '.yaml', '.md', '.txt', '.in')):
                yield os.path.join(folder, file_name)


def license_file_name() -> str:
    today = datetime.datetime.utcnow()
    return f'LICENSE_{today.year}_{today.month}_{today.day}'


@contextlib.contextmanager
def inside(folder: str):
    # The generator writes relative to the working folder.
    original_cwd = os.getcwd()
    os.chdir(folder)
    try:
        yield
    finally:
        os.chdir(original_cwd)


class TestGeneratedProject(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.project_root = generate_project(cls, SAMPLE_YAML)
        cls.bare_root = generate_project(cls, os.path.join(SAMPLES, 'AcmeBare.yaml'))
        cls.inventory_root = generate_project(cls, os.path.join(SAMPLES, 'AcmeInventory.yaml'))
        cls.search_root = generate_project(cls, os.path.join(SAMPLES, 'AcmeSearch.yaml'))

    def _run_in_project(self, *args) -> subprocess.CompletedProcess:
        return run_python(self.project_root, *args)

    def test_generated_tests_pass(self):
        result = self._run_in_project('-m', 'unittest', 'discover', '-s', 'tests', '-t', '.')

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('Ran 1 test', result.stderr)

    def test_core_lib_builds_twice_in_one_process(self):
        script = (
            'from tests.test_data.helpers.util import load_config\n'
            'from acme_core_lib.acme_core_lib import AcmeCoreLib\n'
            'config = load_config()\n'
            'first = AcmeCoreLib(config)\n'
            'second = AcmeCoreLib(config)\n'
            'print(type(second.widget).__name__, type(second.widget._data_access).__name__)\n'
            "print(hasattr(second, 'widget_data_access'), hasattr(second, 'widget_service'))\n"
            'from acme_core_lib_instance import AcmeCoreLibInstance\n'   # the generated instance holder
            'AcmeCoreLibInstance.init(config)\n'
            'print(type(AcmeCoreLibInstance.get()).__name__)\n'
        )
        result = self._run_in_project('-c', script)

        self.assertEqual(0, result.returncode, result.stderr)
        wiring_line, public_names_line, instance_line = result.stdout.strip().splitlines()
        # The service is public under its rulebook name and holds a DataAccess instance; the DataAccess is private.
        self.assertEqual('WidgetService WidgetDataAccess', wiring_line)
        self.assertEqual('False False', public_names_line)
        self.assertEqual('AcmeCoreLib', instance_line)

    def test_service_name_the_core_lib_already_uses_keeps_its_full_name(self):
        # ConfigService as `config` would replace the generated CoreLib's own config.
        self.assertEqual('widget', service_attribute_name('WidgetService'))
        self.assertEqual('config_service', service_attribute_name('ConfigService'))
        self.assertEqual('load_jobs_service', service_attribute_name('LoadJobsService'))

    def test_every_service_name_gives_an_attribute_the_generated_class_can_assign(self):
        attributes = {f'{word.title()}Service': f'{word}_service' for word in keyword.kwlist if word.islower()}
        attributes.update({
            'WidgetService': 'widget',
            'MatchService': 'match',                # a soft keyword is a valid attribute
            'Service': 'service',                   # nothing is left of the name
            'Import': 'service_import',             # no suffix, so the full name is the keyword or the CoreLib's own
            'Class': 'service_class',
            'Config': 'service_config',
            'LoadJobs': 'service_load_jobs',
            '_3dService': 'service_3d_service',     # `camel_to_snake` strips the underscore, leaving a leading digit
        })
        self.assertEqual(attributes, {class_name: service_attribute_name(class_name) for class_name in attributes})

        core_lib = OmegaConf.create({'core_lib': {
            'name': 'AcmeDocs', 'services': [{'key': class_name} for class_name in attributes],
        }})
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        generator = CoreLibGenerator(core_lib)
        with inside(folder):
            generator.generate_service()
            generator.generate_core_lib_class()
        package = os.path.join(folder, 'acme_docs', 'acme_docs')
        source = read(package, 'acme_docs.py')

        compile(source, 'acme_docs.py', 'exec')   # a keyword or an empty name is a SyntaxError here
        for class_name, attribute in attributes.items():
            self.assertIn(f'self.{attribute} = {class_name}()', source)
        imported_modules = re.findall(r'^from acme_docs\.data_layers\.service\.(\w+) import ', source, flags=re.M)
        self.assertEqual(len(attributes), len(imported_modules))
        for module in imported_modules:
            self.assertFalse(keyword.iskeyword(module))
            compile(read(package, 'data_layers', 'service', f'{module}.py'), module, 'exec')

    def test_readme_comments_out_a_service_without_functions(self):
        with open(os.path.join(REPO_ROOT, 'core_lib_generator', 'template_core_lib', 'README.md')) as template:
            readme = ReadmeGenerateTemplate().generate(
                template.read(), [{'key': 'WidgetService', 'data_access': 'WidgetDataAccess'}], 'acme_core_lib', None
            )

        # A live call to a method the empty service lacks would raise AttributeError when the example runs.
        calls = [line for line in readme.splitlines() if 'acme_core_lib.widget.' in line]
        self.assertEqual(['# acme_core_lib.widget.your_function()'], calls)

    def test_readme_example_runs(self):
        example = re.search(r'```python\n(.*?)```', read(self.project_root, 'README.md'), flags=re.S).group(1)

        result = run_readme_example(self.project_root)

        self.assertIn('acme_core_lib.widget.get_by_name()', example)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_generated_setup_builds_isolated_and_does_not_install_tests(self):
        # An isolated build has setuptools only: neither pip nor the library itself is importable.
        script = (
            'import runpy, setuptools, sys\n'
            "sys.modules['pip'] = None\n"
            "sys.modules['acme_core_lib'] = None\n"
            'captured = {}\n'
            'setuptools.setup = lambda **kwargs: captured.update(kwargs)\n'
            "runpy.run_path('setup.py', run_name='__main__')\n"
            "print(sorted(captured['packages']))\n"
            "print(captured['python_requires'], captured['version'], captured['install_requires'])\n"
        )
        result = self._run_in_project('-c', script)

        self.assertEqual(0, result.returncode, result.stderr)
        packages_line, settings_line = result.stdout.strip().splitlines()
        self.assertNotIn("'tests", packages_line)
        self.assertIn("'acme_core_lib'", packages_line)
        self.assertIn("'hydra_plugins.acme_core_lib'", packages_line)
        self.assertEqual(">=3.10 0.0.0.1 ['core-lib']", settings_line)

    def test_soft_delete_data_access_deletes_a_row(self):
        # The sample declares `is_crud_soft_delete_token: false`: its widget has no token column.
        script = (
            'from core_lib.error_handling.status_code_exception import StatusCodeException\n'
            'from tests.test_data.helpers.util import load_config\n'
            'from acme_core_lib.acme_core_lib import AcmeCoreLib\n'
            'widget_data_access = AcmeCoreLib(load_config()).widget._data_access\n'
            "row = widget_data_access.create({'name': 'cog'})\n"
            'print(type(widget_data_access).__bases__[0].__name__, widget_data_access.delete(row.id))\n'
            'try:\n'
            '    widget_data_access.get(row.id)\n'
            'except StatusCodeException as missing:\n'
            '    print(int(missing.status_code))\n'
        )
        result = self._run_in_project('-c', script)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(['CRUDSoftDeleteDataAccess 1', '404'], result.stdout.splitlines())

    def test_mit_license_is_the_standard_text(self):
        expected = MIT_LICENSE.format(year=datetime.datetime.utcnow().year)

        self.assertEqual(expected, read(self.project_root, license_file_name()))

    def test_no_template_placeholder_is_left(self):
        for project_root in (self.project_root, self.bare_root, self.inventory_root, self.search_root):
            for path in generated_files(project_root):
                with open(path) as generated_file:
                    self.assertNotIn('# template_', generated_file.read(), path)

    def test_output_does_not_depend_on_the_hash_seed(self):
        # Python salts str hashes per process, so lines put through a set come out in a different order per run.
        samples = [os.path.join(SAMPLES, name) for name in ('AcmeInventory.yaml', 'AcmeSearch.yaml')]
        for seed in ('1', '2', '3', '4'):
            with self.subTest(PYTHONHASHSEED=seed):
                folder = tempfile.mkdtemp()
                self.addCleanup(shutil.rmtree, folder)
                result = subprocess.run(
                    [sys.executable, '-c', GENERATE_SAMPLES, *samples], cwd=folder, capture_output=True, text=True,
                    env=dict(os.environ, PYTHONPATH=REPO_ROOT, PYTHONHASHSEED=seed), timeout=120,
                )

                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(SEARCH_CORE_LIB_SOURCE, read(folder, 'acme_search', 'acme_search', 'acme_search.py'))
                self.assertEqual(GADGET_ENTITY_SOURCE, read(
                    folder, 'acme_inventory', 'acme_inventory', 'data_layers', 'data', 'inventory_db', 'entities',
                    'gadget.py',
                ))
                self.assertEqual(WIDGET_CATALOG_SOURCE, read(
                    folder, 'acme_inventory', 'acme_inventory', 'data_layers', 'service', 'widget_catalog.py'
                ))

    # ── what the generator refuses ───────────────────────────────────────────

    def test_unsupported_connection_type_stops_each_generator_that_reads_it(self):
        core_lib = OmegaConf.create({'core_lib': {
            'name': 'AcmeDocs',
            'connections': [{'key': 'docs', 'type': MONGO_FACTORY, 'config': {'url': {'host': 'localhost'}}}],
            'data_accesses': [{'key': 'DocsDataAccess', 'functions': [], 'connection': 'docs'}],
        }})
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        generator = CoreLibGenerator(core_lib)
        for part in (generator.generate_data_access, generator.generate_core_lib_class, generator.generate_config):
            with self.subTest(part.__name__), inside(folder):
                with self.assertRaises(ValueError) as error:
                    part()

                self.assertEqual(UNSUPPORTED_CONNECTION, str(error.exception))

    def test_crud_data_access_without_a_connection_is_refused(self):
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        for flag in ('is_crud', 'is_crud_soft_delete', 'is_crud_soft_delete_token'):
            generator = CoreLibGenerator(OmegaConf.create({'core_lib': {
                'name': 'AcmeDocs', 'connections': [],
                'data_accesses': [{'key': 'DocsDataAccess', 'functions': [], 'entity': 'doc', flag: True}],
            }}))
            with self.subTest(flag), inside(folder):
                with self.assertRaises(ValueError) as error:
                    generator.generate_data_access()

                self.assertEqual(
                    'data access `DocsDataAccess` is a CRUD data access, so it needs a `connection`', str(error.exception)
                )

    def test_unsupported_connection_type_stops_the_generate_command(self):
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        OmegaConf.save(OmegaConf.create({'core_lib': {
            'name': 'AcmeDocs', 'env': {}, 'caches': [], 'jobs': [], 'entities': [], 'services': [], 'setup': {},
            'connections': [{'key': 'docs', 'type': MONGO_FACTORY, 'config': {'url': {'host': 'localhost'}}}],
            'data_accesses': [],
        }}), os.path.join(folder, 'AcmeDocs.yaml'))

        with inside(folder):
            result = CliRunner().invoke(main, ['generate', '--yaml', 'AcmeDocs.yaml'])
        GlobalHydra.instance().clear()

        self.assertIsInstance(result.exception, ValueError)
        self.assertEqual(UNSUPPORTED_CONNECTION, str(result.exception))
        self.assertNotEqual(0, result.exit_code)

    def test_unsupported_cache_type_stops_the_core_lib_class(self):
        core_lib = OmegaConf.create({'core_lib': {'name': 'AcmeDocs', 'caches': [{'key': 'sessions', 'type': 'ram'}]}})
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)

        with inside(folder), self.assertRaises(ValueError) as error:
            CoreLibGenerator(core_lib).generate_core_lib_class()

        self.assertEqual(
            'cache `sessions` has an unsupported type `ram`; the generator supports memory, memcached, redis',
            str(error.exception),
        )

    def test_unsupported_license_stops_setup_and_license_generation(self):
        expected = (
            'unsupported license `GPL-3.0`; the generator supports MIT, APACHE_LICENSE_2, MOZILLA_PUBLIC_LICENSE_2'
        )
        setup = {
            'author': 'acme', 'author_email': 'dev@acme.example', 'description': 'Docs for acme', 'url': '',
            'license': 'GPL-3.0', 'classifiers': [], 'version': '0.1.0',
        }
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)

        with inside(folder), self.assertRaises(ValueError) as setup_error:
            CoreLibGenerator(OmegaConf.create({'core_lib': {'name': 'AcmeDocs', 'setup': setup}})).generate_setup()
        with self.assertRaises(ValueError) as license_error:
            LicenseGenerateTemplate().get_template_file(setup)

        self.assertEqual(expected, str(setup_error.exception))
        self.assertEqual(expected, str(license_error.exception))
        self.assertFalse(os.path.exists(os.path.join(folder, 'acme_docs', 'setup.py')))   # no half-filled setup.py

    # ── a library with nothing in it ─────────────────────────────────────────

    def test_bare_library_is_an_empty_core_lib_without_packaging(self):
        # __pycache__ appears once another test imports the package; it is Python's, not the generator's.
        generated = sorted(name for name in os.listdir(os.path.join(self.bare_root, 'acme_bare')) if name != '__pycache__')
        self.assertEqual(['__init__.py', 'acme_bare.py', 'config'], generated)
        self.assertFalse([name for name in os.listdir(self.bare_root) if name.startswith(('setup', 'LICENSE'))])
        self.assertEqual(
            'from omegaconf import DictConfig\n'
            'from core_lib.core_lib import CoreLib\n'
            '\n'
            '\n'
            'class AcmeBare(CoreLib):\n'
            '    def __init__(self, conf: DictConfig):\n'
            '        super().__init__()\n'
            '        self.config = conf\n'
            '\n',
            read(self.bare_root, 'acme_bare', 'acme_bare.py'),
        )
        config = OmegaConf.load(os.path.join(self.bare_root, 'acme_bare', 'config', 'acme_bare.yaml'))
        self.assertEqual({'core_lib': {'acme_bare': {}}}, OmegaConf.to_container(config))

    def test_bare_library_tests_and_readme_say_what_to_add(self):
        self.assertEqual(
            'import unittest\n'
            'from acme_bare.acme_bare import AcmeBare\n'
            'from tests.test_data.helpers.util import sync_create_start_core_lib\n'
            '\n'
            '\n'
            'class TestAcmeBare(unittest.TestCase):\n'
            '    @classmethod\n'
            '    def setUpClass(cls):\n'
            '        cls.acme_bare = sync_create_start_core_lib()\n'
            '\n'
            '\n'
            '    # You can write tests for your Service functions or your DataAccess functions below, '
            'by using the Core-Lib instance created above',
            read(self.bare_root, 'tests', 'test_acme_bare.py'),
        )
        example = re.search(r'```python\n(.*?)```', read(self.bare_root, 'README.md'), flags=re.S).group(1)
        # No service: the example builds the library and calls nothing.
        self.assertEqual(
            'import hydra\n'
            '\n'
            'from acme_bare.acme_bare import AcmeBare\n'
            '\n'
            "# Build AcmeBare from its YAML with Hydra's compose API (https://hydra.cc/docs/advanced/compose_api/)\n"
            "with hydra.initialize(config_path='acme_bare/config', version_base=None):\n"
            "    acme_bare = AcmeBare(hydra.compose('acme_bare.yaml'))\n"
            '\n',
            example,
        )
        result = run_readme_example(self.bare_root)

        self.assertEqual(0, result.returncode, result.stderr)

    def test_bare_library_builds_twice_in_one_process(self):
        script = (
            'from tests.test_data.helpers.util import load_config\n'
            'from acme_bare.acme_bare import AcmeBare\n'
            'config = load_config()\n'
            'AcmeBare(config)\n'
            'print(sorted(name for name in vars(AcmeBare(config)) if not name.startswith("_")))\n'
        )
        result = run_python(self.bare_root, '-c', script)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("['config']", result.stdout.strip())

    # ── SQLite: plain, soft-delete and migrated ──────────────────────────────

    def test_crud_template_follows_the_data_access_flags(self):
        result = run_python(self.inventory_root, '-c', INVENTORY_ROUND_TRIP)

        self.assertEqual(0, result.returncode, result.stderr)
        # The flags are read by value: an explicit `false` picks the plainer base class.
        # gadget: plain CRUD, deleted for real; widget: soft delete. Both are gone for `get`. GadgetReport: no CRUD.
        # A new gadget takes the column defaults written in the YAML, falsy ones included.
        self.assertEqual([
            'CRUDDataAccess False 1 404',
            'CRUDSoftDeleteDataAccess True 1 404',
            'DataAccess',
            "0 False '' 'grey'",
        ], result.stdout.splitlines())

    def test_entity_keeps_every_column_default(self):
        self.assertEqual(GADGET_ENTITY_SOURCE, read(
            self.inventory_root, 'acme_inventory', 'data_layers', 'data', 'inventory_db', 'entities', 'gadget.py'
        ))

    def test_services_are_wired_by_name_with_or_without_a_data_access(self):
        result = run_python(self.inventory_root, '-c', INVENTORY_SURFACE)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([
            'GadgetService WidgetCatalog StatusService',   # WidgetCatalog does not end in Service: full snake name
            'True {}',                                      # StatusService has no DataAccess to hold
            'CACHE_WIDGET',                                 # the constant the decorators name
            "install True ['cfg']",                         # `migrate: true` adds the Alembic entry points
            "uninstall True ['cfg']",
        ], result.stdout.splitlines())

    def test_service_functions_get_the_decorators_asked_for(self):
        self.assertEqual(
            'from core_lib.data_layers.service.service import Service\n'
            'from core_lib.data_transform.result_to_dict import ResultToDict\n'
            'from acme_inventory.data_layers.data_access.gadget_data_access import GadgetDataAccess\n'
            '\n'
            '\n'
            'class GadgetService(Service):\n'
            '\n'
            '    def __init__(self, data_access: GadgetDataAccess):\n'
            '        self._data_access = data_access\n'
            '\n'
            '    @ResultToDict()\n'
            '    def list_gadgets(self):\n'
            '        pass\n',
            read(self.inventory_root, 'acme_inventory', 'data_layers', 'service', 'gadget_service.py'),
        )
        # `cache_widget` and `CACHE_WIDGET` are one key: one constant, upper case.
        self.assertEqual(
            WIDGET_CATALOG_SOURCE,
            read(self.inventory_root, 'acme_inventory', 'data_layers', 'service', 'widget_catalog.py'),
        )
        # No function, no DataAccess: an empty Service.
        self.assertEqual(
            'from core_lib.data_layers.service.service import Service\n'
            '\n'
            '\n'
            'class StatusService(Service):\n'
            '\n'
            '    pass\n',
            read(self.inventory_root, 'acme_inventory', 'data_layers', 'service', 'status_service.py'),
        )

    def test_inventory_tests_and_readme_run(self):
        tests = run_python(self.inventory_root, '-m', 'unittest', 'discover', '-s', 'tests', '-t', '.')
        readme = run_readme_example(self.inventory_root)

        self.assertEqual(0, tests.returncode, tests.stderr)
        self.assertIn('Ran 3 tests', tests.stderr)
        self.assertEqual(0, readme.returncode, readme.stderr)

    def test_apache_license_reaches_setup_and_the_license_file(self):
        setup_py = read(self.inventory_root, 'setup.py')

        self.assertIn("    license='Apache-2.0',\n", setup_py)
        self.assertIn("    url='https://acme.example/inventory',\n", setup_py)
        self.assertEqual(
            "# Version of the core_lib\n__version__ = '1.2.0'\n",
            read(self.inventory_root, 'acme_inventory', '__init__.py'),
        )
        self.assertEqual(
            ['Apache-2.0 License', '', f'Copyright {datetime.datetime.utcnow().year} acme'],
            read(self.inventory_root, license_file_name()).splitlines()[:3],
        )

    # ── Solr, Neo4j and remote caches: generated, never connected ────────────

    def test_connections_without_sql_are_configured_by_their_kind(self):
        config = OmegaConf.load(os.path.join(self.search_root, 'acme_search', 'config', 'acme_search.yaml'))

        self.assertEqual({'core_lib': {'acme_search': {
            'cache': {
                'sessions': {'type': 'redis', 'url': {'host': 'cache.acme.example', 'port': 6380, 'protocol': 'redis'}},
                'pages': {'type': 'memcached', 'url': {'host': 'cache.acme.example', 'port': 11212}},
            },
            'solr': {'search': {   # config_instantiate: the factory is named by `_target_`
                'config': {
                    'always_commit': True,
                    'url': {'protocol': 'http', 'host': '${oc.env:SEARCH_HOST}', 'port': 8983, 'file': 'solr/widgets'},
                },
                '_target_': SOLR_FACTORY,
            }},
            'neo4j': {'graph': {
                'url': {'protocol': 'neo4j', 'host': 'localhost', 'port': 7687},
                'credentials': {'username': 'reviewer', 'password': 's3cret'},
            }},
        }}}, OmegaConf.to_container(config, resolve=False))

    def test_core_lib_builds_each_connection_and_registers_each_cache_once(self):
        # In YAML order. Solr, built through instantiate_config, is not imported by name. A DataAccess without a
        # connection has no __init__ to pass one to. Each cache reads the config block the generator wrote for it.
        self.assertEqual(SEARCH_CORE_LIB_SOURCE, read(self.search_root, 'acme_search', 'acme_search.py'))

    def test_search_core_lib_builds_with_its_remote_caches(self):
        result = run_python(self.search_root, '-c', SEARCH_BUILD)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([
            'CacheHandlerRedis cache.acme.example 6380',
            'CacheHandlerMemcached cache.acme.example 11212',
            'ReportDataAccess SolrConnectionFactory',
        ], result.stdout.splitlines())

    def test_data_access_holds_its_connection_and_its_functions(self):
        data_access_folder = os.path.join(self.search_root, 'acme_search', 'data_layers', 'data_access')
        expected = {
            'search_data_access.py': (
                'from core_lib.data_layers.data_access.data_access import DataAccess\n'
                'from core_lib.connection.solr_connection_factory import SolrConnectionFactory\n'
                '\n'
                '\n'
                'class SearchDataAccess(DataAccess):\n'
                '    def __init__(self, session: SolrConnectionFactory):\n'
                '        self.session = session\n'
                '\n'
                '    def find_widgets(self):\n'
                '        pass\n'
            ),
            'graph_data_access.py': (
                'from core_lib.data_layers.data_access.data_access import DataAccess\n'
                'from core_lib.connection.neo4j_connection_factory import Neo4jConnectionFactory\n'
                '\n'
                '\n'
                'class GraphDataAccess(DataAccess):\n'
                '    def __init__(self, session: Neo4jConnectionFactory):\n'
                '        self.session = session\n'
            ),
            'report_data_access.py': (   # no connection and no function: an empty class body still parses
                'from core_lib.data_layers.data_access.data_access import DataAccess\n'
                '\n'
                '\n'
                'class ReportDataAccess(DataAccess):\n'
                '    pass\n'
            ),
            'audit_data_access.py': (
                'from core_lib.data_layers.data_access.data_access import DataAccess\n'
                '\n'
                '\n'
                'class AuditDataAccess(DataAccess):\n'
                '\n'
                '    def record(self):\n'
                '        pass\n'
            ),
        }
        for file_name, source in expected.items():
            with self.subTest(file_name):
                self.assertEqual(source, read(data_access_folder, file_name))

    def test_without_services_each_data_access_gets_a_test(self):
        test_file = read(self.search_root, 'tests', 'test_acme_search.py')

        self.assertEqual(
            ['test_search_data_access', 'test_graph_data_access', 'test_report_data_access', 'test_audit_data_access'],
            re.findall(r'def (test_\w+)\(self\):', test_file),
        )
        self.assertIn(
            'from acme_search.data_layers.data_access.report_data_access import ReportDataAccess\n', test_file
        )
        self.assertIn(
            '        # ReportDataAccess is private to the CoreLib: test it through the service that uses it\n',
            test_file,
        )

    def test_every_generated_search_module_imports(self):
        script = (
            'import acme_search.acme_search\n'
            'import tests.test_acme_search\n'
            'from acme_search.data_layers.data_access import '
            'search_data_access, graph_data_access, report_data_access, audit_data_access\n'
            'print(search_data_access.SearchDataAccess.__init__.__annotations__["session"].__name__)\n'
        )
        result = run_python(self.search_root, '-c', script)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual('SolrConnectionFactory', result.stdout.strip())

    def test_mozilla_license_reaches_setup_and_the_license_file(self):
        setup_py = read(self.search_root, 'setup.py')

        self.assertIn("    license='MPL-2.0',\n", setup_py)
        self.assertIn('    classifiers=[],\n', setup_py)
        self.assertEqual(
            ['MPL-2.0 License', '', f'Copyright {datetime.datetime.utcnow().year} acme'],
            read(self.search_root, license_file_name()).splitlines()[:3],
        )
