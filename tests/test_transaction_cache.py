"""@Cache follows @Transaction(): inside a transaction a read neither reads nor fills the cache, and an
invalidation waits for the commit and is dropped on rollback; outside one nothing changes."""
import unittest
from http import HTTPStatus

from core_lib.cache.cache_decorator import Cache
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.connection.transaction_decorator import Transaction
from core_lib.core_lib import CoreLib
from core_lib.error_handling.status_code_exception import StatusCodeException
from tests.test_data.test_utils import connect_to_mem_db
from tests.test_data.transaction_widget import TransactionWidget
from tests.test_data.transaction_widget_data_access import TransactionWidgetDataAccess
from tests.test_data.transaction_widget_service import (
    CACHE_KEY_GROUP,
    TRANSACTION_TEST_CACHE,
    TransactionWidgetService,
)

GROUP_ID = 5
OTHER_GROUP_ID = 6
FLOW_GROUP_ID = 9


def _group_key(group_id: int) -> str:
    return CACHE_KEY_GROUP.format(group_id=group_id)


def _widget(name: str, group_id: int = GROUP_ID) -> dict:
    return {TransactionWidget.group_id.key: group_id, TransactionWidget.name.key: name}


@Cache(CACHE_KEY_GROUP, handler_name=TRANSACTION_TEST_CACHE, invalidate=True)
def _invalidate_group(group_id: int):
    pass


@Cache(CACHE_KEY_GROUP, handler_name=TRANSACTION_TEST_CACHE, invalidate=True)
def _fail_to_change_group(group_id: int):
    raise RuntimeError('the change failed')


class _FailingDeleteCacheHandler(CacheHandlerRam):
    """Refuses to delete one key, so a test can see an invalidation fail after the commit."""

    def __init__(self, failing_key: str, error: BaseException):
        super().__init__()
        self.failing_key = failing_key
        self.error = error

    def delete(self, key: str):
        if key == self.failing_key:
            raise self.error
        super().delete(key)


class TestTransactionCache(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        CoreLib.cache_registry.register(TRANSACTION_TEST_CACHE, CacheHandlerRam())

    @classmethod
    def tearDownClass(cls):
        CoreLib.cache_registry.unregister(TRANSACTION_TEST_CACHE)

    def setUp(self):
        self.factory = connect_to_mem_db()
        self.addCleanup(self.factory.engine.dispose)
        self.transaction_widget_data_access = TransactionWidgetDataAccess(self.factory)
        self.transaction_widget_service = TransactionWidgetService(self.transaction_widget_data_access)
        CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).flush_all()

    def _warm_group(self, group_id: int, name: str) -> list:
        self.transaction_widget_data_access.create(_widget(name, group_id))
        names = self.transaction_widget_service.list_group(group_id)
        self.assertEqual(names, CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).get(_group_key(group_id)))
        return names

    def _restore_ram_handler(self):
        CoreLib.cache_registry.unregister(TRANSACTION_TEST_CACHE)
        CoreLib.cache_registry.register(TRANSACTION_TEST_CACHE, CacheHandlerRam())

    def test_c1_a_read_inside_a_transaction_bypasses_a_warm_cache(self):
        self.assertEqual(['acme'], self._warm_group(GROUP_ID, 'acme'))

        @Transaction()
        def create_then_read():
            self.transaction_widget_data_access.create(_widget('beta'))
            return self.transaction_widget_service.list_group(GROUP_ID)

        self.assertEqual(['acme', 'beta'], create_then_read())
        self.assertEqual(['acme'], CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).get(_group_key(GROUP_ID)))

    def test_c2_a_read_inside_a_transaction_does_not_fill_a_cold_key(self):
        @Transaction()
        def read_cold():
            return self.transaction_widget_service.list_group(OTHER_GROUP_ID)

        self.assertEqual([], read_cold())
        self.assertIsNone(CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).get(_group_key(OTHER_GROUP_ID)))

    def test_c3_rows_of_a_rolled_back_transaction_are_never_cached(self):
        names_read_inside = []

        @Transaction()
        def create_read_fail():
            self.transaction_widget_data_access.create(_widget('acme'))
            names_read_inside.append(self.transaction_widget_service.list_group(GROUP_ID))
            raise RuntimeError('roll back')

        with self.assertRaises(RuntimeError):
            create_read_fail()

        self.assertEqual([['acme']], names_read_inside)
        self.assertIsNone(CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).get(_group_key(GROUP_ID)))
        self.assertEqual([], self.transaction_widget_service.list_group(GROUP_ID))

    def test_c4_an_invalidation_inside_a_transaction_waits_for_the_commit(self):
        self._warm_group(GROUP_ID, 'acme')
        cached_inside = []

        @Transaction()
        def invalidate_inside():
            _invalidate_group(GROUP_ID)
            cached_inside.append(CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).get(_group_key(GROUP_ID)))

        invalidate_inside()

        self.assertEqual([['acme']], cached_inside)
        self.assertIsNone(CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).get(_group_key(GROUP_ID)))

    def test_c5_an_invalidation_is_dropped_when_the_transaction_rolls_back(self):
        self._warm_group(GROUP_ID, 'acme')

        @Transaction()
        def invalidate_then_fail():
            _invalidate_group(GROUP_ID)
            raise RuntimeError('roll back')

        with self.assertRaises(RuntimeError):
            invalidate_then_fail()

        self.assertEqual(['acme'], CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).get(_group_key(GROUP_ID)))

    def test_c6_an_invalidating_method_that_raises_schedules_nothing(self):
        self._warm_group(GROUP_ID, 'acme')

        @Transaction()
        def swallow_failed_change():
            try:
                _fail_to_change_group(GROUP_ID)
            except RuntimeError:
                pass
            return 'committed'

        self.assertEqual('committed', swallow_failed_change())
        self.assertEqual(['acme'], CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).get(_group_key(GROUP_ID)))

    def test_c7_an_invalidation_above_the_transaction_runs_after_it_returns(self):
        @Cache(CACHE_KEY_GROUP, handler_name=TRANSACTION_TEST_CACHE, invalidate=True)
        @Transaction()
        def add_to_group(group_id: int, name: str, should_fail: bool):
            self.transaction_widget_data_access.create(_widget(name, group_id))
            if should_fail:
                raise RuntimeError('add failed')

        self._warm_group(GROUP_ID, 'acme')
        add_to_group(GROUP_ID, 'beta', False)
        self.assertIsNone(CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).get(_group_key(GROUP_ID)))

        self.assertEqual(['acme', 'beta'], self.transaction_widget_service.list_group(GROUP_ID))
        with self.assertRaises(RuntimeError):
            add_to_group(GROUP_ID, 'gamma', True)
        self.assertEqual(['acme', 'beta'],
                         CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).get(_group_key(GROUP_ID)))
        self.assertEqual(['acme', 'beta'], self.transaction_widget_data_access.names_in_group(GROUP_ID))

    def test_c8_a_failing_invalidation_raises_after_the_commit_and_the_next_one_still_runs(self):
        delete_failure = ConnectionError('cache delete failed')
        CoreLib.cache_registry.unregister(TRANSACTION_TEST_CACHE)
        CoreLib.cache_registry.register(TRANSACTION_TEST_CACHE,
                                        _FailingDeleteCacheHandler(_group_key(GROUP_ID), delete_failure))
        self.addCleanup(self._restore_ram_handler)
        self._warm_group(GROUP_ID, 'acme')
        self._warm_group(OTHER_GROUP_ID, 'acme')

        @Transaction()
        def write_and_invalidate_both():
            self.transaction_widget_data_access.create(_widget('beta'))
            _invalidate_group(GROUP_ID)
            _invalidate_group(OTHER_GROUP_ID)

        with self.assertRaises(ConnectionError) as raised:
            write_and_invalidate_both()

        self.assertIs(delete_failure, raised.exception)
        self.assertEqual(['acme', 'beta'], self.transaction_widget_data_access.names_in_group(GROUP_ID))
        self.assertEqual(['acme'], CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).get(_group_key(GROUP_ID)))
        self.assertIsNone(CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).get(_group_key(OTHER_GROUP_ID)))

    def test_c9_outside_a_transaction_the_cache_behaves_as_before(self):
        self.transaction_widget_data_access.create(_widget('acme'))
        self.assertIsNone(CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).get(_group_key(GROUP_ID)))

        self.assertEqual(['acme'], self.transaction_widget_service.list_group(GROUP_ID))
        self.assertEqual(['acme'], CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).get(_group_key(GROUP_ID)))
        self.transaction_widget_data_access.create(_widget('beta'))
        self.assertEqual(['acme'], self.transaction_widget_service.list_group(GROUP_ID))

        _invalidate_group(GROUP_ID)
        self.assertIsNone(CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).get(_group_key(GROUP_ID)))
        self.assertEqual(['acme', 'beta'], self.transaction_widget_service.list_group(GROUP_ID))

    def test_c10_flow_replace_group_keeps_the_cache_true_to_the_database(self):
        self.assertEqual([], self.transaction_widget_service.list_group(FLOW_GROUP_ID))

        self.assertEqual(['gamma'], self.transaction_widget_service.replace_group(FLOW_GROUP_ID, ['gamma']))
        self.assertIsNone(CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).get(_group_key(FLOW_GROUP_ID)))
        self.assertEqual(['gamma'], self.transaction_widget_service.list_group(FLOW_GROUP_ID))

        with self.assertRaises(StatusCodeException) as raised:
            self.transaction_widget_service.replace_group(FLOW_GROUP_ID, ['dup', 'dup'])
        self.assertEqual(HTTPStatus.CONFLICT, raised.exception.status_code)
        self.assertEqual(['gamma'],
                         CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).get(_group_key(FLOW_GROUP_ID)))
        self.assertEqual(['gamma'], self.transaction_widget_service.list_group(FLOW_GROUP_ID))
        self.assertEqual(['gamma'], self.transaction_widget_data_access.names_in_group(FLOW_GROUP_ID))
