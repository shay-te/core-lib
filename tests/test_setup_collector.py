"""`core_lib generate` asks for the details of setup.py; the answers become the `setup` section of the YAML."""
import unittest

from core_lib_generator.config_collectors.setup_collector import generate_setup_template
from tests.test_data.test_utils import typed


class TestSetupCollector(unittest.TestCase):

    def test_defaults_give_an_mit_licensed_first_version_without_a_url(self):
        # author, email, version [0.0.0.1], description, url [Enter = none], license [1-MIT], classifier 1, another [no]
        with typed('acme', 'dev@acme.example', '', 'Widgets for acme', '', '', '1', 'no'):
            setup = generate_setup_template()

        self.assertEqual({
            'author': 'acme',
            'author_email': 'dev@acme.example',
            'description': 'Widgets for acme',
            'url': '',
            'license': 'MIT',
            'classifiers': ['Development Status :: 3 - Alpha'],
            'version': '0.0.0.1',
        }, setup)

    def test_typed_values_and_answers_that_are_asked_again(self):
        with typed(
            'acme', 'not-an-email', 'dev@acme.example',   # an invalid email is asked again
            '1.2.0', 'Widgets for acme', 'https://acme.example/widgets',
            '3',                                          # 3-MOZILLA_PUBLIC_LICENSE_2
            '9', '', '9', '1', 'no',                      # a classifier picked twice is asked again
        ):
            setup = generate_setup_template()

        self.assertEqual({
            'author': 'acme',
            'author_email': 'dev@acme.example',
            'description': 'Widgets for acme',
            'url': 'https://acme.example/widgets',
            'license': 'MOZILLA_PUBLIC_LICENSE_2',
            'classifiers': ['Natural Language :: English', 'Development Status :: 3 - Alpha'],
            'version': '1.2.0',
        }, setup)

    def test_apache_license_is_stored_by_its_name(self):
        with typed('acme', 'dev@acme.example', '', 'Widgets for acme', '', '2', '4', 'no'):
            setup = generate_setup_template()

        self.assertEqual('APACHE_LICENSE_2', setup['license'])
        self.assertEqual(['Environment :: MacOS X'], setup['classifiers'])
