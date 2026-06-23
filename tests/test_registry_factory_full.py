"""Exhaustive permutation tests for Registry and Factory base classes.

Covers:
- DefaultRegistry: ctor validation, register/unregister cycles, key collisions,
  default key lifecycle, get() fallbacks (no default, single entry, multiple),
  is_default toggle, registered() ordering, type-narrowing
- Registry abstract: instantiation rules
- Factory abstract: instantiation rules
"""
import unittest

from core_lib.factory.factory import Factory
from core_lib.registry.default_registry import DefaultRegistry
from core_lib.registry.registry import Registry


class _Item:
    def __init__(self, name):
        """
        Initialize an Item with a name.
        """
        self.name = name


# ── DefaultRegistry constructor ────────────────────────────────────────────


class TestDefaultRegistryConstruction(unittest.TestCase):
    def test_requires_object_type(self):
        with self.assertRaises(ValueError):
            DefaultRegistry(None)
        with self.assertRaises(ValueError):
            DefaultRegistry(False)
        with self.assertRaises(ValueError):
            DefaultRegistry(0)
        with self.assertRaises(ValueError):
            DefaultRegistry('')

    def test_accepts_any_truthy_object_type(self):
        # Even non-class types are accepted as the constraint is just truthy
        for t in [str, int, list, dict, tuple, set, object]:
            with self.subTest(t=t):
                r = DefaultRegistry(t)
                self.assertIs(r._object_type, t)
                self.assertEqual(r.key_to_object, {})
                self.assertIsNone(r.default_key)


# ── DefaultRegistry.register ───────────────────────────────────────────────


class TestDefaultRegistryRegister(unittest.TestCase):
    def setUp(self):
        self.r = DefaultRegistry(_Item)

    def test_register_basic(self):
        a = _Item('a')
        self.r.register('a', a)
        self.assertIs(self.r.get('a'), a)

    def test_register_requires_truthy_key(self):
        with self.assertRaises(AssertionError):
            self.r.register('', _Item('x'))
        with self.assertRaises(AssertionError):
            self.r.register(None, _Item('x'))

    def test_register_requires_truthy_object(self):
        with self.assertRaises(AssertionError):
            self.r.register('a', None)
        with self.assertRaises(AssertionError):
            self.r.register('a', False)
        with self.assertRaises(AssertionError):
            self.r.register('a', '')

    def test_register_wrong_type_raises(self):
        with self.assertRaises(ValueError):
            self.r.register('a', 'not-an-item')
        with self.assertRaises(ValueError):
            self.r.register('a', 123)

    def test_register_duplicate_key_raises(self):
        """
        Assert that registering a duplicate key raises ValueError.
        """
        self.r.register('a', _Item('a'))
        with self.assertRaises(ValueError):
            self.r.register('a', _Item('b'))

    def test_register_with_is_default_sets_default(self):
        a = _Item('a')
        self.r.register('a', a, is_default=True)
        self.assertEqual(self.r.default_key, 'a')
        self.assertIs(self.r.get(), a)

    def test_register_without_is_default_leaves_default_none(self):
        self.r.register('a', _Item('a'))
        self.assertIsNone(self.r.default_key)


# ── DefaultRegistry.unregister ─────────────────────────────────────────────


class TestDefaultRegistryUnregister(unittest.TestCase):
    def setUp(self):
        self.r = DefaultRegistry(_Item)

    def test_unregister_existing_removes_key(self):
        self.r.register('a', _Item('a'))
        self.r.unregister('a')
        self.assertIsNone(self.r.get('a'))
        self.assertNotIn('a', self.r.key_to_object)

    def test_unregister_default_key_clears_default(self):
        self.r.register('a', _Item('a'), is_default=True)
        self.r.unregister('a')
        self.assertIsNone(self.r.default_key)

    def test_unregister_non_default_keeps_default(self):
        self.r.register('a', _Item('a'), is_default=True)
        self.r.register('b', _Item('b'))
        self.r.unregister('b')
        self.assertEqual(self.r.default_key, 'a')

    def test_unregister_missing_no_op(self):
        self.r.register('a', _Item('a'))
        self.r.unregister('not-there')
        # Original is untouched
        self.assertIsNotNone(self.r.get('a'))


# ── DefaultRegistry.get fallback rules ─────────────────────────────────────


class TestDefaultRegistryGet(unittest.TestCase):
    def setUp(self):
        self.r = DefaultRegistry(_Item)

    def test_get_explicit_key(self):
        a = _Item('a')
        self.r.register('a', a)
        self.assertIs(self.r.get('a'), a)

    def test_get_missing_key_returns_none(self):
        self.r.register('a', _Item('a'))
        self.assertIsNone(self.r.get('nope'))

    def test_get_with_no_arg_uses_default_when_set(self):
        a = _Item('a')
        b = _Item('b')
        self.r.register('a', a)
        self.r.register('b', b, is_default=True)
        self.assertIs(self.r.get(), b)

    def test_get_with_no_arg_no_default_returns_first_when_one_entry(self):
        a = _Item('a')
        self.r.register('a', a)
        # No default → fallback: first value in dict
        self.assertIs(self.r.get(), a)

    def test_get_with_no_arg_no_default_returns_first_of_many(self):
        # Insertion order in Py3.7+
        self.r.register('a', _Item('a'))
        self.r.register('b', _Item('b'))
        self.r.register('c', _Item('c'))
        # No default → returns first registered (which is 'a')
        self.assertEqual(self.r.get().name, 'a')

    def test_get_with_no_arg_on_empty_returns_none(self):
        # No registered entries → result is None and the `len > 0` branch is False
        """
        Verify that get() returns None when the registry is empty.
        """
        self.assertIsNone(self.r.get())

    def test_get_passes_extra_args_kwargs_silently(self):
        a = _Item('a')
        self.r.register('a', a)
        # Extra args/kwargs are accepted but ignored
        self.assertIs(self.r.get('a', 1, 2, foo='bar'), a)


# ── DefaultRegistry.registered ─────────────────────────────────────────────


class TestDefaultRegistryRegistered(unittest.TestCase):
    def test_returns_insertion_order(self):
        r = DefaultRegistry(_Item)
        for k in ['z', 'a', 'm']:
            r.register(k, _Item(k))
        self.assertEqual(r.registered(), ['z', 'a', 'm'])

    def test_empty_returns_empty_list(self):
        r = DefaultRegistry(_Item)
        self.assertEqual(r.registered(), [])

    def test_reflects_unregister(self):
        r = DefaultRegistry(_Item)
        r.register('a', _Item('a'))
        r.register('b', _Item('b'))
        r.unregister('a')
        self.assertEqual(r.registered(), ['b'])


# ── Multiple defaults: only the latest is_default wins ────────────────────


class TestDefaultRegistryDefaultLifecycle(unittest.TestCase):
    def test_later_is_default_overrides_earlier(self):
        r = DefaultRegistry(_Item)
        a = _Item('a')
        b = _Item('b')
        r.register('a', a, is_default=True)
        r.register('b', b, is_default=True)
        # Default switches to b
        self.assertEqual(r.default_key, 'b')
        self.assertIs(r.get(), b)

    def test_re_register_after_unregister(self):
        r = DefaultRegistry(_Item)
        a1 = _Item('a1')
        r.register('a', a1, is_default=True)
        r.unregister('a')
        # default cleared
        self.assertIsNone(r.default_key)
        a2 = _Item('a2')
        r.register('a', a2)
        self.assertIs(r.get('a'), a2)


# ── Registry abstract ─────────────────────────────────────────────────────


class TestRegistryAbstract(unittest.TestCase):
    def test_cannot_instantiate_directly(self):
        with self.assertRaises(TypeError):
            Registry()  # type: ignore[abstract]

    def test_concrete_subclass_must_implement_get(self):
        class Incomplete(Registry):
            pass
        with self.assertRaises(TypeError):
            Incomplete()  # type: ignore[abstract]

    def test_concrete_subclass_works(self):
        class Concrete(Registry):
            def get(self, *args, **kwargs):
                return 'value'
        self.assertEqual(Concrete().get(), 'value')


# ── Factory abstract ──────────────────────────────────────────────────────


class TestFactoryAbstract(unittest.TestCase):
    def test_cannot_instantiate_directly(self):
        with self.assertRaises(TypeError):
            Factory()  # type: ignore[abstract]

    def test_concrete_subclass_must_implement_get(self):
        class Incomplete(Factory):
            pass
        with self.assertRaises(TypeError):
            Incomplete()  # type: ignore[abstract]

    def test_concrete_subclass_works(self):
        class Concrete(Factory):
            def get(self, *args, **kwargs):
                return ('a', args, kwargs)
        self.assertEqual(Concrete().get(1, x='y'), ('a', (1,), {'x': 'y'}))
