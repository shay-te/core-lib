"""Blocks inside blocks in a transaction: every clean block flushes, only the last open block releases, the count of
open blocks stays right through errors, bare `get()` calls and threads, and outside a transaction nothing changes."""
import threading
import unittest

from sqlalchemy.exc import IntegrityError

from core_lib.connection.transaction_decorator import Transaction
from core_lib.core_lib import CoreLib
from tests.test_data.recording_connection import EVENT_ENTER, EVENT_EXIT, EVENT_FLUSH, EVENT_RELEASE, NO_ERROR
from tests.test_data.recording_connection_factory import RecordingConnectionFactory
from tests.test_data.test_utils import connect_to_file_db
from tests.test_data.transaction_widget import TransactionWidget
from tests.test_data.transaction_widget_data_access import TransactionWidgetDataAccess

GROUP_ID = 61
WAIT_SECONDS = 60
THREADS = 16
TRANSACTIONS_PER_THREAD = 50


def _widget(name: str, group_id: int = GROUP_ID) -> dict:
    return {TransactionWidget.group_id.key: group_id, TransactionWidget.name.key: name}


class TestTransactionBlocks(unittest.TestCase):

    def setUp(self):
        self.factory = connect_to_file_db(self)
        self.transaction_widget_data_access = TransactionWidgetDataAccess(self.factory)

    def _names(self) -> list:
        return self.transaction_widget_data_access.names_in_group(GROUP_ID)

    def test_k1_three_nested_blocks_each_change_a_row_and_the_inner_creates_have_ids_at_once(self):
        ids = [self.transaction_widget_data_access.create(_widget(name)).id for name in ('one', 'two', 'three')]
        inner_ids = []

        @Transaction()
        def three_levels():
            with self.factory.get() as outer:
                first = outer.get(TransactionWidget, ids[0])
                with self.factory.get() as middle:
                    second = middle.get(TransactionWidget, ids[1])
                    with self.factory.get() as inner:
                        third = inner.get(TransactionWidget, ids[2])
                        third.name = 'three-renamed'
                    inner_ids.append(self.transaction_widget_data_access.create(_widget('made-in-middle')).id)
                    second.name = 'two-renamed'
                first.name = 'one-renamed'
                inner_ids.append(self.transaction_widget_data_access.create(_widget('made-in-outer')).id)

        three_levels()

        self.assertTrue(all(isinstance(row_id, int) for row_id in inner_ids))   # flushed at each inner block's end
        self.assertEqual(['made-in-middle', 'made-in-outer', 'one-renamed', 'three-renamed', 'two-renamed'],
                         self._names())

    def test_k2_only_the_last_open_block_releases(self):
        factory = RecordingConnectionFactory()

        @Transaction()
        def nested_then_flat():
            with factory.get():
                with factory.get():
                    with factory.get():
                        pass
            with factory.get():
                pass

        nested_then_flat()

        [connection] = factory.created
        self.assertEqual([EVENT_ENTER, EVENT_ENTER, EVENT_ENTER, EVENT_FLUSH, EVENT_FLUSH, EVENT_FLUSH, EVENT_RELEASE,
                          EVENT_ENTER, EVENT_FLUSH, EVENT_RELEASE, EVENT_EXIT], connection.events())

    def test_k3_an_inner_block_error_caught_inside_the_outer_block_keeps_the_inner_blocks_unsent_write(self):
        # Documents the limit: only the last open block releases, so a write left by an inner block that failed is
        # still in the session when the outer block flushes. Rolling back one inner block would need a savepoint.
        @Transaction()
        def catch_inside_the_outer_block():
            with self.factory.get():
                try:
                    with self.factory.get() as inner:
                        inner.add(TransactionWidget(group_id=GROUP_ID, name='from-the-failed-inner-block'))
                        raise ValueError('the inner block fails')
                except ValueError:
                    pass

        catch_inside_the_outer_block()

        self.assertEqual(['from-the-failed-inner-block'], self._names())

    def test_k4_a_get_not_used_in_a_with_block_does_not_change_the_count(self):
        factory = RecordingConnectionFactory()
        counts = []

        @Transaction()
        def bare_get_then_block():
            connection = factory.get()   # never entered: the count stays 0
            counts.append(connection.open_blocks)
            with factory.get():
                counts.append(connection.open_blocks)
            counts.append(connection.open_blocks)

        bare_get_then_block()

        self.assertEqual([0, 1, 0], counts)
        self.assertEqual([EVENT_ENTER, EVENT_FLUSH, EVENT_RELEASE, EVENT_EXIT], factory.created[0].events())

    def test_k5_the_count_is_back_to_zero_after_failed_blocks_nested_failures_and_the_end(self):
        factory = RecordingConnectionFactory()
        counts = []

        @Transaction()
        def fail_in_many_ways():
            for i in range(2):
                try:
                    with factory.get():
                        raise ValueError('a flat block fails')
                except ValueError:
                    pass
            connection = factory.created[0]
            counts.append(connection.open_blocks)
            try:
                with factory.get():
                    with factory.get():
                        raise ValueError('a nested block fails')
            except ValueError:
                pass
            counts.append(connection.open_blocks)

        fail_in_many_ways()

        self.assertEqual([0, 0], counts)
        self.assertEqual(0, factory.created[0].open_blocks)
        self.assertEqual([NO_ERROR], factory.created[0].exit_arguments())

    def test_k6_outside_a_transaction_nested_blocks_are_separate_connections_each_ended_by_its_block(self):
        factory = RecordingConnectionFactory()

        with factory.get():
            with factory.get():
                pass

        outer, inner = factory.created
        self.assertEqual([EVENT_ENTER, EVENT_EXIT], outer.events())
        self.assertEqual([EVENT_ENTER, EVENT_EXIT], inner.events())
        self.assertEqual([(inner, EVENT_EXIT, NO_ERROR), (outer, EVENT_EXIT, NO_ERROR)],
                         [entry for entry in factory.journal if entry[1] == EVENT_EXIT])

    def test_k7_a_nested_blocks_failed_flush_goes_up_through_the_outer_block_and_rolls_everything_back(self):
        self.transaction_widget_data_access.create(_widget('taken'))

        @Transaction()
        def duplicate_inside_a_block():
            with self.factory.get() as outer:
                outer.add(TransactionWidget(group_id=GROUP_ID, name='from-the-outer-block'))
                self.transaction_widget_data_access.create(_widget('taken'))   # its flush raises

        with self.assertRaises(IntegrityError):
            duplicate_inside_a_block()

        self.assertEqual(['taken'], self._names())
        self.assertIsNone(CoreLib.transaction_scope_registry.get())

    def test_k8_many_threads_with_nested_blocks_keep_their_counts_apart(self):
        factory = RecordingConnectionFactory()
        errors = []

        @Transaction()
        def nested():
            with factory.get():
                with factory.get():
                    pass

        def run():
            try:
                for i in range(TRANSACTIONS_PER_THREAD):
                    nested()
            except BaseException as error:
                errors.append(error)

        workers = [threading.Thread(target=run) for i in range(THREADS)]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(WAIT_SECONDS)

        self.assertEqual([], errors)
        self.assertEqual(THREADS * TRANSACTIONS_PER_THREAD, len(factory.created))
        for connection in factory.created:
            self.assertEqual([EVENT_ENTER, EVENT_ENTER, EVENT_FLUSH, EVENT_FLUSH, EVENT_RELEASE, EVENT_EXIT],
                             connection.events())
            self.assertEqual(0, connection.open_blocks)
