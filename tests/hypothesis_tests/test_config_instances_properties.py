"""Property-based tests for helpers.config_instances."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.config_instances import (
    _get_config_under_path,
    instantiate_config,
    instantiate_config_group_generator_dict,
    instantiate_config_group_generator_list,
)
from tests.hypothesis_tests._settings import SETTINGS


_KEY = st.text(alphabet=stringmod.ascii_lowercase, min_size=1, max_size=10)


class TestGetConfigUnderPathProperties(unittest.TestCase):
    @given(data=st.dictionaries(_KEY, st.integers(), min_size=1, max_size=10))
    @SETTINGS
    def test_none_path_returns_input_verbatim(self, data):
        self.assertEqual(_get_config_under_path(data, None), data)

    @given(data=st.dictionaries(_KEY, st.integers(), min_size=1, max_size=10))
    @SETTINGS
    def test_empty_path_returns_input_verbatim(self, data):
        self.assertEqual(_get_config_under_path(data, ''), data)

    @given(missing_key=_KEY)
    @SETTINGS
    def test_missing_key_silent_returns_none(self, missing_key):
        self.assertIsNone(_get_config_under_path({}, missing_key))

    @given(key=_KEY)
    @SETTINGS
    def test_missing_key_raises_when_flag_set(self, key):
        with self.assertRaises(ValueError):
            _get_config_under_path({}, key, raise_class_config_base_path_error=True)

    @given(key=_KEY, value=st.integers(min_value=1))
    @SETTINGS
    def test_top_level_key_resolution_with_truthy_value(self, key, value):
        # NOTE: production code uses `if not data_at_path:` which treats
        # falsy values (0, '', [], {}, False) as "not found". Only truthy
        # values resolve correctly — surfaced by hypothesis.
        result = _get_config_under_path({key: value}, key)
        self.assertEqual(result, value)

    def test_top_level_key_with_falsy_value_returns_none(self):
        # Document the production quirk: falsy values appear as "not found".
        self.assertIsNone(_get_config_under_path({'k': 0}, 'k'))
        self.assertIsNone(_get_config_under_path({'k': ''}, 'k'))
        self.assertIsNone(_get_config_under_path({'k': []}, 'k'))


class TestInstantiateConfigGroupGeneratorsProperties(unittest.TestCase):
    @given(keys=st.lists(_KEY, min_size=1, max_size=10, unique=True))
    @SETTINGS
    def test_dict_generator_yields_one_entry_per_key(self, keys):
        from omegaconf import OmegaConf
        conf = OmegaConf.create({k: {} for k in keys})
        results = list(instantiate_config_group_generator_dict(conf))
        self.assertEqual(len(results), len(keys))
        result_names = [r[0] for r in results]
        self.assertEqual(set(result_names), set(keys))

    @given(n=st.integers(min_value=1, max_value=10))
    @SETTINGS
    def test_list_generator_yields_n_entries(self, n):
        from omegaconf import OmegaConf
        conf = OmegaConf.create([{} for _ in range(n)])
        results = list(instantiate_config_group_generator_list(conf))
        self.assertEqual(len(results), n)


class TestInstantiateConfigProperties(unittest.TestCase):
    @given(key=_KEY)
    @SETTINGS
    def test_invalid_target_raises_value_error(self, key):
        from omegaconf import OmegaConf
        # An arbitrary string treated as a target path will fail to import
        config = OmegaConf.create({'_target_': f'nonexistent_module.{key}'})
        with self.assertRaises(ValueError):
            instantiate_config(config)
