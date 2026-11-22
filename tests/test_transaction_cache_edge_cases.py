"""@Cache inside @Transaction(), the hard cases: which key a deferred invalidation deletes, how many, in what order,
under nesting, swallowed errors, failed commits, unknown or replaced handlers, long keys, threads, and the one race
a deferred invalidation cannot close."""
import threading
import unittest
from unittest import mock

from core_lib.cache.cache_decorator import Cache
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.connection.transaction_decorator import Transaction
from core_lib.core_lib import CoreLib
from tests.test_data.test_utils import connect_to_file_db
from tests.test_data.transaction_widget import TransactionWidget
from tests.test_data.transaction_widget_data_access import TransactionWidgetDataAccess

GROUP_ID = 91
OTHER_GROUP_ID = 92
WAIT_SECONDS = 30
EDGE_CACHE = 'core_lib_test_transaction_cache_edge_cases'
MISSING_CACHE = 'core_lib_test_transaction_cache_that_does_not_exist'
KEY_NAMES = 'core_lib_test_cache_edge_names'
KEY_GROUP = 'core_lib_test_cache_edge_group_{data[group_id]}'
KEY_LONG = 'core_lib_test_cache_edge_long_{suffix}'
KEY_WITH_SPACES = 'core_lib test cache edge {label}'
LONG_SUFFIX = 'x' * 400
REPEATED_INVALIDATIONS = 100
MAX_KEY_LENGTH = 250


class _RecordingCacheHandler(CacheHandlerRam):
    """A RAM cache that records every key it stores and every key it deletes, in order."""

    def __init__(self):
        super().__init__()
        self.stored = []
        self.deleted = []

    def set(self, key: str, value, expire):
        self.stored.append(key)
        super().set(key, value, expire)

    def delete(self, key: str):
        self.deleted.append(key)
        super().delete(key)


def _widget(name: str, group_id: int = GROUP_ID) -> dict:
    return {TransactionWidget.group_id.key: group_id, TransactionWidget.name.key: name}


@Cache(KEY_NAMES, handler_name=EDGE_CACHE, invalidate=True)
def _invalidate_names():
    return 'the invalidating function returned'


@Cache(KEY_GROUP, handler_name=EDGE_CACHE, invalidate=True)
def _invalidate_group(data: dict):
    pass


@Cache(KEY_LONG, handler_name=EDGE_CACHE, invalidate=True)
def _invalidate_long(suffix: str):
    pass


@Cache(KEY_WITH_SPACES, handler_name=EDGE_CACHE, invalidate=True)
def _invalidate_with_spaces(label: str):
    pass


@Cache(KEY_NAMES, handler_name=MISSING_CACHE, invalidate=True)
def _invalidate_through_a_missing_handler():
    pass


@Cache(KEY_NAMES, handler_name=EDGE_CACHE, invalidate=True)
def _fail_to_invalidate():
    raise RuntimeError('the invalidating function fails')


class TestTransactionCacheEdgeCases(unittest.TestCase):

    def setUp(self):
        self.cache = _RecordingCacheHandler()
        CoreLib.cache_registry.register(EDGE_CACHE, self.cache)
        self.addCleanup(CoreLib.cache_registry.unregister, EDGE_CACHE)
        self.factory = connect_to_file_db(self)
        self.transaction_widget_data_access = TransactionWidgetDataAccess(self.factory)

    def _names(self, group_id: int = GROUP_ID) -> list:
        return self.transaction_widget_data_access.names_in_group(group_id)

    def _run_in_thread(self, target) -> threading.Thread:
        worker = threading.Thread(target=target)
        worker.start()
        return worker

    def test_ce1_the_deleted_key_is_the_one_built_at_the_call_even_if_its_argument_changes_before_the_commit(self):
        data = {'group_id': GROUP_ID}
        original_key, changed_key = KEY_GROUP.format(data={'group_id': GROUP_ID}), KEY_GROUP.format(data={'group_id': OTHER_GROUP_ID})
        self.cache.set(original_key, 'original', None)
        self.cache.set(changed_key, 'changed', None)

        @Transaction()
        def invalidate_then_change_the_argument():
            _invalidate_group(data)
            data['group_id'] = OTHER_GROUP_ID

        invalidate_then_change_the_argument()

        self.assertEqual([original_key], self.cache.deleted)
        self.assertIsNone(self.cache.get(original_key))
        self.assertEqual('changed', self.cache.get(changed_key))

    def test_ce2_one_key_invalidated_many_times_is_deleted_only_after_the_commit_once_per_call(self):
        self.cache.set(KEY_NAMES, ['cached'], None)
        seen_before_the_commit = []

        @Transaction()
        def invalidate_many_times():
            results = [_invalidate_names() for i in range(REPEATED_INVALIDATIONS)]
            seen_before_the_commit.append((self.cache.get(KEY_NAMES), list(self.cache.deleted)))
            return results

        results = invalidate_many_times()

        self.assertEqual(['the invalidating function returned'] * REPEATED_INVALIDATIONS, results)
        self.assertEqual([(['cached'], [])], seen_before_the_commit)
        self.assertEqual([KEY_NAMES] * REPEATED_INVALIDATIONS, self.cache.deleted)   # one delete per call, no dedup
        self.assertIsNone(self.cache.get(KEY_NAMES))

    def test_ce3_several_keys_are_deleted_after_the_commit_in_the_order_they_were_invalidated(self):
        @Transaction()
        def invalidate_three():
            _invalidate_with_spaces('third')
            _invalidate_group({'group_id': GROUP_ID})
            _invalidate_names()

        invalidate_three()

        self.assertEqual([KEY_WITH_SPACES.format(label='third').replace(' ', '_'),
                          KEY_GROUP.format(data={'group_id': GROUP_ID}), KEY_NAMES], self.cache.deleted)

    def test_ce4_an_invalidation_in_a_nested_transaction_waits_for_the_outermost_commit(self):
        self.cache.set(KEY_NAMES, ['cached'], None)
        seen = []

        @Transaction()
        def inner():
            _invalidate_names()

        @Transaction()
        def outer():
            inner()
            seen.append(self.cache.get(KEY_NAMES))   # the inner transaction returned: nothing committed yet

        outer()

        self.assertEqual([['cached']], seen)
        self.assertIsNone(self.cache.get(KEY_NAMES))

    def test_ce5_an_inner_failure_swallowed_by_the_outer_transaction(self):
        @Transaction()
        def inner_invalidates_then_fails():
            _invalidate_names()   # succeeded: scheduled on the one transaction
            raise RuntimeError('the inner transaction fails after the invalidation')

        @Transaction()
        def outer_swallows(inner):
            try:
                inner()
            except RuntimeError:
                pass

        self.cache.set(KEY_NAMES, ['cached'], None)
        outer_swallows(inner_invalidates_then_fails)
        after_a_successful_invalidation = self.cache.get(KEY_NAMES)
        self.cache.set(KEY_NAMES, ['cached'], None)
        outer_swallows(_fail_to_invalidate)

        self.assertIsNone(after_a_successful_invalidation)    # nested transactions join: it ran at the outer commit
        self.assertEqual(['cached'], self.cache.get(KEY_NAMES))   # the invalidating function raised: nothing scheduled

    def test_ce6_an_unknown_cache_handler_fails_before_the_function_and_rolls_the_transaction_back(self):
        @Transaction()
        def write_then_invalidate():
            self.transaction_widget_data_access.create(_widget('rolled-back'))
            _invalidate_through_a_missing_handler()

        with self.assertRaises(ValueError) as raised:
            write_then_invalidate()

        self.assertIn(MISSING_CACHE, str(raised.exception))
        self.assertEqual([], self._names())

    def test_ce7_a_cached_read_that_raises_inside_a_transaction_caches_nothing_and_rolls_back(self):
        @Cache(KEY_NAMES, handler_name=EDGE_CACHE)
        def read_that_fails():
            raise LookupError('the read fails')

        @Transaction()
        def write_then_read():
            self.transaction_widget_data_access.create(_widget('rolled-back'))
            return read_that_fails()

        with self.assertRaises(LookupError):
            write_then_read()

        self.assertIsNone(self.cache.get(KEY_NAMES))
        self.assertEqual([], self._names())

    def test_ce8_long_keys_and_keys_with_spaces_are_cut_and_cleaned_alike_for_the_read_and_its_deferred_delete(self):
        @Cache(KEY_LONG, handler_name=EDGE_CACHE)
        def read_long(suffix: str):
            return ['long']

        @Cache(KEY_WITH_SPACES, handler_name=EDGE_CACHE)
        def read_with_spaces(label: str):
            return ['spaces']

        read_long(LONG_SUFFIX)
        read_with_spaces('a label')
        stored = sorted(self.cache.stored)   # the keys the reads really stored

        @Transaction()
        def invalidate_both():
            _invalidate_long(LONG_SUFFIX)
            _invalidate_with_spaces('a label')

        invalidate_both()

        self.assertEqual(MAX_KEY_LENGTH, max(len(key) for key in stored))
        self.assertTrue(all(' ' not in key for key in stored))
        self.assertEqual(stored, sorted(self.cache.deleted))
        self.assertEqual([None, None], [self.cache.get(key) for key in stored])

    def test_ce9_a_failed_commit_drops_the_invalidation(self):
        self.cache.set(KEY_NAMES, ['cached'], None)

        @Transaction()
        def write_invalidate_and_fail_the_commit():
            self.transaction_widget_data_access.create(_widget('never-saved'))
            _invalidate_names()
            self.transaction_widget_data_access.current_session().commit = mock.Mock(
                side_effect=ConnectionError('the commit fails'))

        with self.assertRaises(ConnectionError):
            write_invalidate_and_fail_the_commit()

        self.assertEqual([], self.cache.deleted)
        self.assertEqual(['cached'], self.cache.get(KEY_NAMES))

    def test_ce10_the_deferred_delete_goes_to_the_handler_registered_at_the_call(self):
        # Documents the behaviour: the delete is bound to the handler the registry held when the invalidation ran;
        # a handler registered under the same name before the commit keeps its entry.
        replacement = _RecordingCacheHandler()
        replacement.set(KEY_NAMES, ['in-the-replacement'], None)

        @Transaction()
        def invalidate_then_replace_the_handler():
            _invalidate_names()
            CoreLib.cache_registry.unregister(EDGE_CACHE)
            CoreLib.cache_registry.register(EDGE_CACHE, replacement)

        invalidate_then_replace_the_handler()

        self.assertEqual([KEY_NAMES], self.cache.deleted)
        self.assertEqual([], replacement.deleted)
        self.assertEqual(['in-the-replacement'], replacement.get(KEY_NAMES))

    def test_ce11_two_threads_invalidating_one_key_each_delete_after_their_own_commit(self):
        self.cache.set(KEY_NAMES, ['cached'], None)
        scheduled = threading.Event()
        release = threading.Event()

        @Transaction()
        def slow_invalidation():
            _invalidate_names()
            scheduled.set()
            release.wait(WAIT_SECONDS)

        @Transaction()
        def quick_invalidation():
            _invalidate_names()

        slow = self._run_in_thread(slow_invalidation)
        scheduled.wait(WAIT_SECONDS)
        still_cached = self.cache.get(KEY_NAMES)   # the slow thread has not committed
        quick_invalidation()                        # this thread commits: its own delete runs
        after_the_quick_commit = list(self.cache.deleted)
        release.set()
        slow.join(WAIT_SECONDS)

        self.assertEqual(['cached'], still_cached)
        self.assertEqual([KEY_NAMES], after_the_quick_commit)
        self.assertEqual([KEY_NAMES, KEY_NAMES], self.cache.deleted)   # the slow thread's delete ran at its commit

    def test_ce12_a_reader_that_loaded_the_old_value_before_the_commit_stores_it_after_the_invalidation(self):
        # Documents the limit (not new with transactions): a read on another thread that loaded before the commit and
        # stores after the invalidation leaves the old value cached, until it expires or the next invalidation.
        self.transaction_widget_data_access.create(_widget('old'))
        loaded = threading.Event()
        committed = threading.Event()

        @Cache(KEY_NAMES, handler_name=EDGE_CACHE)
        def slow_cached_read():
            names = self._names()
            loaded.set()
            committed.wait(WAIT_SECONDS)
            return names

        @Transaction()
        def write_and_invalidate():
            self.transaction_widget_data_access.create(_widget('new'))
            _invalidate_names()

        reader = self._run_in_thread(slow_cached_read)
        loaded.wait(WAIT_SECONDS)
        write_and_invalidate()
        committed.set()
        reader.join(WAIT_SECONDS)

        self.assertEqual(['new', 'old'], self._names())
        self.assertEqual(['old'], self.cache.get(KEY_NAMES))   # stale
