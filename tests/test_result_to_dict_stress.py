"""Stress tests for result_to_dict.

These are example-based (not hypothesis) tests that exercise every parameter
combination and every supported value type at every dict/list/tuple position.
"""
import datetime
import enum
import unittest
from collections import namedtuple
from decimal import Decimal

from geoalchemy2 import WKTElement

from core_lib.data_transform.result_to_dict import ResultToDict, result_to_dict


class _Color(enum.Enum):
    RED = 1
    GREEN = 'green'
    BLUE = 3.14


# ── Type coverage at top-level dict value position ─────────────────────────


class TestTopLevelDictValueTypes(unittest.TestCase):
    """Every type that __convert_value handles, plus primitives, as a
    top-level dict value (not buried in nested SQLAlchemy entity)."""

    def test_datetime_top_level(self):
        dt = datetime.datetime(2024, 6, 15, 12, 30, 45)
        result = result_to_dict({'k': dt})
        self.assertEqual(result['k'], dt.timestamp())
        self.assertIsInstance(result['k'], float)

    def test_date_top_level(self):
        d = datetime.date(2024, 6, 15)
        result = result_to_dict({'k': d})
        expected = datetime.datetime(2024, 6, 15).timestamp()
        self.assertEqual(result['k'], expected)

    def test_enum_int_value_top_level(self):
        result = result_to_dict({'k': _Color.RED})
        self.assertEqual(result['k'], 1)

    def test_enum_str_value_top_level(self):
        result = result_to_dict({'k': _Color.GREEN})
        self.assertEqual(result['k'], 'green')

    def test_enum_float_value_top_level(self):
        result = result_to_dict({'k': _Color.BLUE})
        self.assertEqual(result['k'], 3.14)

    def test_decimal_top_level(self):
        result = result_to_dict({'k': Decimal('42.5')})
        self.assertIsInstance(result['k'], float)
        self.assertEqual(result['k'], 42.5)

    def test_decimal_zero(self):
        result = result_to_dict({'k': Decimal('0')})
        self.assertEqual(result['k'], 0.0)

    def test_decimal_negative(self):
        result = result_to_dict({'k': Decimal('-1.5')})
        self.assertEqual(result['k'], -1.5)

    def test_bool_true_top_level(self):
        result = result_to_dict({'k': True})
        self.assertIs(result['k'], True)

    def test_bool_false_top_level(self):
        result = result_to_dict({'k': False})
        self.assertIs(result['k'], False)

    def test_none_top_level(self):
        result = result_to_dict({'k': None})
        self.assertIsNone(result['k'])

    def test_bytes_top_level(self):
        result = result_to_dict({'k': b'binary'})
        # bytes isn't a primitive in (int,float,bool,str) so it'd recurse;
        # but with no special branch in __convert_value, returns as-is.
        self.assertEqual(result['k'], b'binary')

    def test_bytearray_top_level(self):
        ba = bytearray(b'mutable')
        result = result_to_dict({'k': ba})
        self.assertEqual(result['k'], ba)

    def test_set_top_level(self):
        s = {1, 2, 3}
        result = result_to_dict({'k': s})
        # set is not a primitive → recursion fires → result_to_dict on set
        # → no isinstance matches → returns the set as-is
        self.assertEqual(result['k'], s)

    def test_frozenset_top_level(self):
        fs = frozenset([1, 2, 3])
        result = result_to_dict({'k': fs})
        self.assertEqual(result['k'], fs)

    def test_wkbelement_top_level(self):
        # WKTElement isn't a WKBElement, so it's not converted via Point.from_point_wkb
        # — it's not a primitive either, so recursion fires and it returns as-is.
        point = WKTElement('POINT(5 45)')
        result = result_to_dict({'k': point})
        self.assertEqual(result['k'], point)

    def test_complex_number_top_level(self):
        # Not in any conversion branch → passes through
        result = result_to_dict({'k': 1 + 2j})
        self.assertEqual(result['k'], 1 + 2j)


# ── properties_as_dict=False ──────────────────────────────────────────────


class TestPropertiesAsDictFlagFalse(unittest.TestCase):
    def test_nested_dict_kept_as_object(self):
        inner = {'b': 1}
        result = result_to_dict({'a': inner}, properties_as_dict=False)
        # No recursion → the inner dict is the SAME object
        self.assertIs(result['a'], inner)

    def test_nested_list_kept_as_object(self):
        inner = [1, 2, 3]
        result = result_to_dict({'a': inner}, properties_as_dict=False)
        self.assertIs(result['a'], inner)

    def test_primitives_still_processed(self):
        # Top-level dict still goes through __dict_to_dict
        result = result_to_dict({1: 'a', 'b': 2}, properties_as_dict=False)
        self.assertEqual(result, {'1': 'a', 'b': 2})

    def test_datetime_in_nested_dict_not_converted_when_false(self):
        dt = datetime.datetime(2024, 1, 1)
        inner = {'when': dt}
        result = result_to_dict({'k': inner}, properties_as_dict=False)
        # Inner dict was not recursed → datetime kept as datetime, not timestamp
        self.assertIs(result['k'], inner)
        self.assertIsInstance(result['k']['when'], datetime.datetime)

    def test_decimal_top_level_still_converted_when_false(self):
        # __convert_value runs during __dict_to_dict on the OUTER dict
        # regardless of properties_as_dict; the flag only controls recursion
        # into non-primitive values discovered in `results`.
        result = result_to_dict({'k': Decimal('5')}, properties_as_dict=False)
        self.assertEqual(result['k'], 5.0)


# ── Lists of every supported type ─────────────────────────────────────────


class TestListWithMixedTypes(unittest.TestCase):
    def test_list_of_dicts(self):
        result = result_to_dict([{'a': 1}, {'b': 2}, {'c': 3}])
        self.assertEqual(result, [{'a': 1}, {'b': 2}, {'c': 3}])

    def test_list_of_primitives_mixed(self):
        items = [1, 'str', 3.14, True, None]
        self.assertEqual(result_to_dict(items), items)

    def test_list_of_datetimes(self):
        items = [datetime.datetime(2024, 1, 1), datetime.datetime(2024, 6, 1)]
        result = result_to_dict(items)
        # The list branch recurses per element. Each datetime is not a dict/
        # list/tuple/Base/Row, so falls into else → returned verbatim.
        self.assertEqual(result, items)

    def test_list_of_decimals(self):
        items = [Decimal('1'), Decimal('2.5'), Decimal('-3')]
        result = result_to_dict(items)
        # Same — Decimal not in any branch of result_to_dict's main switch;
        # only converted inside dicts via __convert_value.
        self.assertEqual(result, items)

    def test_list_of_namedtuples(self):
        Point = namedtuple('Point', ['x', 'y'])
        items = [Point(1, 2), Point(3, 4)]
        result = result_to_dict(items)
        self.assertEqual(result, [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}])

    def test_list_of_lists(self):
        items = [[1, 2], [3, 4]]
        self.assertEqual(result_to_dict(items), items)

    def test_list_containing_none(self):
        result = result_to_dict([1, None, 2])
        self.assertEqual(result, [1, None, 2])

    def test_empty_list_returns_empty(self):
        self.assertEqual(result_to_dict([]), [])


# ── Tuples / NamedTuples with all types ───────────────────────────────────


class TestTupleWithMixedTypes(unittest.TestCase):
    def test_tuple_of_primitives(self):
        result = result_to_dict((1, 'a', 3.14, True))
        self.assertEqual(result, (1, 'a', 3.14, True))

    def test_tuple_with_datetime_converted(self):
        dt = datetime.datetime(2024, 1, 1)
        result = result_to_dict((1, dt))
        # __tuple_to_dict calls __convert_value on each item → datetime → timestamp
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], dt.timestamp())

    def test_tuple_with_decimal_converted(self):
        result = result_to_dict((Decimal('1.5'),))
        self.assertEqual(result, (1.5,))

    def test_tuple_with_enum_converted(self):
        result = result_to_dict((_Color.RED, _Color.GREEN))
        self.assertEqual(result, (1, 'green'))

    def test_tuple_with_none(self):
        result = result_to_dict((None, None))
        self.assertEqual(result, (None, None))

    def test_namedtuple_with_mixed_types(self):
        Row = namedtuple('Row', ['id', 'name', 'when', 'amount'])
        dt = datetime.datetime(2024, 1, 1)
        result = result_to_dict(Row(1, 'foo', dt, Decimal('5.5')))
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['name'], 'foo')
        self.assertEqual(result['when'], dt.timestamp())
        self.assertEqual(result['amount'], 5.5)

    def test_namedtuple_with_none_field(self):
        Row = namedtuple('Row', ['a', 'b'])
        result = result_to_dict(Row(1, None))
        self.assertEqual(result, {'a': 1, 'b': None})


# ── Deep nesting ─────────────────────────────────────────────────────────


class TestDeepNesting(unittest.TestCase):
    def test_dict_5_levels_deep(self):
        deep = {'a': {'b': {'c': {'d': {'e': 'deep'}}}}}
        result = result_to_dict(deep)
        self.assertEqual(result['a']['b']['c']['d']['e'], 'deep')

    def test_list_of_dicts_with_lists_of_dicts(self):
        data = [
            {'items': [{'x': 1}, {'x': 2}]},
            {'items': [{'x': 3}]},
        ]
        result = result_to_dict(data)
        self.assertEqual(result[0]['items'][0]['x'], 1)
        self.assertEqual(result[0]['items'][1]['x'], 2)
        self.assertEqual(result[1]['items'][0]['x'], 3)

    def test_mixed_dict_list_tuple_chain(self):
        Point = namedtuple('Point', ['x', 'y'])
        data = {
            'top': [
                {'pt': Point(1, 2)},
                {'tup': (Decimal('5'), datetime.date(2024, 1, 1))},
            ]
        }
        result = result_to_dict(data)
        self.assertEqual(result['top'][0]['pt'], {'x': 1, 'y': 2})
        self.assertEqual(result['top'][1]['tup'][0], 5.0)
        self.assertEqual(
            result['top'][1]['tup'][1],
            datetime.datetime(2024, 1, 1).timestamp(),
        )


# ── Callback edge cases ─────────────────────────────────────────────────


class TestCallbackEdges(unittest.TestCase):
    def test_callback_mutates_in_place(self):
        def cb(results):
            """
            Add an 'injected' key-value pair to dictionary results.
            
            Returns:
                The results object, with 'injected': 'yes' added if it is a dict.
            """
            if isinstance(results, dict):
                results['injected'] = 'yes'
            return results
        result = result_to_dict({'a': 1}, callback=cb)
        self.assertEqual(result['injected'], 'yes')

    def test_callback_receives_list_when_input_is_list(self):
        # For a list input, the recursive call applies the callback to each
        # element (which is whatever's in the list). The top-level list itself
        # is built up and returned WITHOUT a callback invocation on the list.
        captured = []
        def cb(r):
            captured.append(r)
            return r
        result_to_dict([1, 2, 3], callback=cb)
        # Callback was invoked 3 times (once per primitive element)
        self.assertEqual(captured, [1, 2, 3])

    def test_callback_returning_zero_falls_back(self):
        # `0 or results` → results
        def cb(results):
            return 0
        result = result_to_dict({'a': 1}, callback=cb)
        self.assertEqual(result, {'a': 1})

    def test_callback_returning_false_falls_back(self):
        def cb(results):
            return False
        result = result_to_dict({'a': 1}, callback=cb)
        self.assertEqual(result, {'a': 1})

    def test_callback_returning_other_truthy_replaces(self):
        def cb(results):
            return 'totally different'
        self.assertEqual(result_to_dict({'a': 1}, callback=cb), 'totally different')

    def test_callback_called_for_nested_dicts_too(self):
        # properties_as_dict=True recurses into non-primitive dict values,
        # and that recursive call also receives the callback.
        captured = []
        def cb(r):
            if isinstance(r, dict):
                captured.append(dict(r))
            return r
        result_to_dict({'outer': {'inner': {'k': 'v'}}}, callback=cb)
        # Should have been called on the innermost dict AND the outer
        self.assertGreaterEqual(len(captured), 2)


# ── ResultToDict decorator combinations ────────────────────────────────


class TestResultToDictDecoratorEdges(unittest.TestCase):
    def test_decorator_with_callback(self):
        def cb(results):
            return {'wrapped': results} if isinstance(results, dict) else results

        @ResultToDict(callback=cb)
        def producer():
            return {'a': Decimal('1'), 'b': datetime.datetime(2024, 1, 1)}

        result = producer()
        self.assertIn('wrapped', result)
        self.assertEqual(result['wrapped']['a'], 1.0)

    def test_decorator_on_list_return(self):
        @ResultToDict()
        def producer():
            """
            Return a list of dictionaries containing Decimal values.
            """
            return [{'a': Decimal('5')}, {'b': Decimal('6')}]

        self.assertEqual(producer(), [{'a': 5.0}, {'b': 6.0}])

    def test_decorator_on_namedtuple_return(self):
        Result = namedtuple('Result', ['id', 'value'])

        @ResultToDict()
        def producer():
            return Result(1, Decimal('99.5'))

        self.assertEqual(producer(), {'id': 1, 'value': 99.5})

    def test_decorator_with_args_kwargs(self):
        @ResultToDict()
        def producer(a, b=10):
            return {'a': a, 'b': b}

        self.assertEqual(producer(1, b=20), {'a': 1, 'b': 20})

    def test_decorator_preserves_metadata(self):
        @ResultToDict()
        def my_named_function():
            """My docstring."""
            return {}

        self.assertEqual(my_named_function.__name__, 'my_named_function')
        # Note: @wraps preserves __doc__ too
        self.assertEqual(my_named_function.__doc__, 'My docstring.')


# ── Dict key coercion edges ───────────────────────────────────────────


class TestDictKeyCoercion(unittest.TestCase):
    def test_int_key_becomes_str(self):
        self.assertEqual(result_to_dict({42: 'v'}), {'42': 'v'})

    def test_float_key_becomes_str(self):
        result = result_to_dict({3.14: 'v'})
        self.assertEqual(result['3.14'], 'v')

    def test_bool_key_becomes_str(self):
        # True/False → 'True'/'False' via str()
        result = result_to_dict({True: 'yes', False: 'no'})
        self.assertEqual(result['True'], 'yes')
        self.assertEqual(result['False'], 'no')

    def test_tuple_key_becomes_str(self):
        result = result_to_dict({(1, 2): 'v'})
        self.assertEqual(result['(1, 2)'], 'v')

    def test_none_key_becomes_str(self):
        result = result_to_dict({None: 'v'})
        self.assertEqual(result['None'], 'v')

    def test_unicode_key_preserved(self):
        result = result_to_dict({'kéy': 'v'})
        self.assertEqual(result['kéy'], 'v')


# ── Empty / boundary inputs ───────────────────────────────────────────


class TestBoundaryInputs(unittest.TestCase):
    def test_dict_with_only_falsy_values(self):
        data = {'a': 0, 'b': '', 'c': False, 'd': None, 'e': []}
        result = result_to_dict(data)
        # All falsy values preserved (None included)
        self.assertEqual(result['a'], 0)
        self.assertEqual(result['b'], '')
        self.assertFalse(result['c'])
        self.assertIsNone(result['d'])
        self.assertEqual(result['e'], [])

    def test_large_dict(self):
        big = {f'k{i}': i for i in range(1000)}
        result = result_to_dict(big)
        self.assertEqual(len(result), 1000)
        self.assertEqual(result['k500'], 500)

    def test_large_list(self):
        big = list(range(5000))
        result = result_to_dict(big)
        self.assertEqual(result, big)

    def test_deeply_nested_list_of_lists(self):
        # 20-deep nested list
        x = 'leaf'
        for _ in range(20):
            x = [x]
        result = result_to_dict(x)
        # Walk back down — list branch recurses on each level
        for _ in range(20):
            self.assertIsInstance(result, list)
            result = result[0]
        self.assertEqual(result, 'leaf')
