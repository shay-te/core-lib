"""TransactionManager.end with several connections, when ending one of them fails: the others still end, every pooled
connection goes back, a failed rollback never commits, an interrupt still rolls the rest back, and the caller gets the
first error."""
import unittest
from unittest import mock

from core_lib.connection.transaction_decorator import Transaction
from core_lib.core_lib import CoreLib
from tests.test_data.engine_event_counter import EngineEventCounter
from tests.test_data.recording_connection import NO_ERROR
from tests.test_data.recording_connection_factory import RecordingConnectionFactory
from tests.test_data.test_utils import connect_to_file_db
from tests.test_data.transaction_widget import TransactionWidget
from tests.test_data.transaction_widget_data_access import TransactionWidgetDataAccess

GROUP_ID = 95
MANAGER_LOGGER = 'core_lib.connection.transaction_manager'
CONNECTION_LOGGER = 'core_lib.connection.sql_alchemy_connection'


def _widget(name: str) -> dict:
    return {TransactionWidget.group_id.key: GROUP_ID, TransactionWidget.name.key: name}


class TestTransactionManager(unittest.TestCase):

    def setUp(self):
        self.first_factory, self.second_factory = connect_to_file_db(self), connect_to_file_db(self)
        self.first = TransactionWidgetDataAccess(self.first_factory)
        self.second = TransactionWidgetDataAccess(self.second_factory)

    def test_m1_a_failed_rollback_on_one_database_still_rolls_back_and_releases_the_other_and_commits_nothing(self):
        failure = LookupError('the work fails')
        rollback_failure = OSError('the first rollback fails')

        @Transaction()
        def write_both_then_fail():
            self.first.create(_widget('first'))
            self.second.create(_widget('second'))
            self.first.current_session().rollback = mock.Mock(side_effect=rollback_failure)
            raise failure

        with EngineEventCounter(self.first_factory.engine) as first_counter, \
                EngineEventCounter(self.second_factory.engine) as second_counter:
            with self.assertLogs(MANAGER_LOGGER, 'ERROR') as logs:
                with self.assertRaises(LookupError) as raised:
                    write_both_then_fail()

        self.assertIs(failure, raised.exception)                       # the caller's own error, not the rollback's
        self.assertIs(rollback_failure, logs.records[0].exc_info[1])   # the failed rollback is logged
        self.assertEqual(([], []), (self.first.names_in_group(GROUP_ID), self.second.names_in_group(GROUP_ID)))
        self.assertEqual(0, first_counter.commits)                     # a failed rollback never commits
        self.assertEqual(first_counter.checkouts, first_counter.checkins)    # every pooled connection went back
        self.assertEqual(second_counter.checkouts, second_counter.checkins)

    def test_m2_outside_a_transaction_a_failed_rollback_still_releases_the_connection(self):
        block_failure = ValueError('the block fails')
        rollback_failure = OSError('the rollback fails')

        def write_then_fail():
            with self.first_factory.get() as session:
                session.add(TransactionWidget(group_id=GROUP_ID, name='never-saved'))
                session.flush()
                session.rollback = mock.Mock(side_effect=rollback_failure)
                raise block_failure

        with EngineEventCounter(self.first_factory.engine) as counter:
            with self.assertLogs(CONNECTION_LOGGER, 'ERROR'):
                with self.assertRaises(OSError) as raised:
                    write_then_fail()

        self.assertIs(rollback_failure, raised.exception)
        self.assertIs(block_failure, raised.exception.__context__)   # the block's own error is still attached
        self.assertEqual(0, counter.commits)
        self.assertEqual(counter.checkouts, counter.checkins)
        self.assertEqual([], self.first.names_in_group(GROUP_ID))

    def test_m3_an_interrupt_during_the_first_commit_rolls_the_rest_back_and_goes_up_unchanged(self):
        interrupt = KeyboardInterrupt()
        first, second = RecordingConnectionFactory(commit_error=interrupt), RecordingConnectionFactory()

        @Transaction()
        def use_both():
            with first.get():
                pass
            with second.get():
                pass

        with self.assertRaises(KeyboardInterrupt) as raised:
            use_both()

        self.assertIs(interrupt, raised.exception)
        self.assertEqual([NO_ERROR], first.created[0].exit_arguments())   # its commit was tried, and was interrupted
        [(exec_type, exec_value, _)] = second.created[0].exit_arguments()
        self.assertIs(KeyboardInterrupt, exec_type)                       # the rest rolled back with the interrupt
        self.assertIs(interrupt, exec_value)

    def test_m4_when_every_commit_fails_the_first_error_wins_and_the_rest_roll_back(self):
        first_failure, second_failure = ConnectionError('first commit fails'), ConnectionError('second commit fails')
        first = RecordingConnectionFactory(commit_error=first_failure)
        second = RecordingConnectionFactory(commit_error=second_failure)

        @Transaction()
        def use_both():
            with first.get():
                pass
            with second.get():
                pass

        with self.assertRaises(ConnectionError) as raised:
            use_both()

        self.assertIs(first_failure, raised.exception)
        [(exec_type, exec_value, _)] = second.created[0].exit_arguments()
        self.assertIs(first_failure, exec_value)   # never committed: rolled back with the first failure

    def test_m5_every_after_commit_callback_runs_the_first_error_is_raised_and_the_later_ones_logged(self):
        first_failure, later_failure = ConnectionError('the first callback fails'), OSError('the third callback fails')
        ran = []

        def callback(number: int, failure: BaseException = None):
            def run():
                ran.append(number)
                if failure is not None:
                    raise failure
            return run

        @Transaction()
        def write_and_register_three():
            self.first.create(_widget('committed'))
            for registered in (callback(1, first_failure), callback(2), callback(3, later_failure)):
                CoreLib.transaction_scope_registry.get().on_commit.append(registered)

        with self.assertLogs(MANAGER_LOGGER, 'ERROR') as logs:
            with self.assertRaises(ConnectionError) as raised:
                write_and_register_three()

        self.assertEqual([1, 2, 3], ran)                              # none skipped
        self.assertIs(first_failure, raised.exception)                # the first error wins
        self.assertIs(later_failure, logs.records[0].exc_info[1])     # the later one is not lost
        self.assertEqual(['committed'], self.first.names_in_group(GROUP_ID))
        self.assertIsNone(CoreLib.transaction_scope_registry.get())
