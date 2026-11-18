"""@Transaction() at the connection level, with a recording factory that joins it: one connection per
factory, ended once, in join order, with after-commit callbacks; factories that do not join are untouched
(no SQL needed)."""
import types
import unittest

from core_lib.connection.object_connection_factory import ObjectConnectionFactory
from core_lib.connection.transaction_decorator import Transaction
from core_lib.connection.transaction_scope import TransactionScope
from core_lib.connection.transactional_connection import TransactionalConnection
from core_lib.connection.transactional_connection_factory import TransactionalConnectionFactory
from core_lib.core_lib import CoreLib
from tests.test_data.recording_connection import EVENT_ENTER, EVENT_EXIT, EVENT_FLUSH, EVENT_RELEASE, NO_ERROR, RecordingConnection
from tests.test_data.recording_connection_factory import RecordingConnectionFactory
from tests.test_data.test_utils import connect_to_mongo

SCOPE_LOGGER = 'core_lib.connection.transaction_manager'


class TestTransactionScope(unittest.TestCase):

    def test_g1_outside_a_transaction_every_block_gets_and_ends_its_own_connection(self):
        factory = RecordingConnectionFactory()
        resources = []
        with factory.get() as resource:
            resources.append(resource)
            self.assertEqual([EVENT_ENTER], factory.created[0].events())
        with factory.get() as resource:
            resources.append(resource)

        self.assertEqual(2, len(factory.created))
        first, second = factory.created
        self.assertEqual([
            (first, EVENT_ENTER, None), (first, EVENT_EXIT, NO_ERROR),
            (second, EVENT_ENTER, None), (second, EVENT_EXIT, NO_ERROR),
        ], factory.journal)
        self.assertIsNot(resources[0], resources[1])

    def test_g2_inside_a_transaction_three_blocks_share_one_connection_ended_once(self):
        factory = RecordingConnectionFactory()
        resources = []
        events_before_end = []

        @Transaction()
        def three_blocks():
            for i in range(3):
                with factory.get() as resource:
                    resources.append(resource)
            events_before_end.extend(factory.created[0].events())

        three_blocks()

        self.assertEqual(1, len(factory.created))
        connection = factory.created[0]
        self.assertEqual([connection.resource] * 3, resources)
        self.assertEqual([EVENT_ENTER, EVENT_FLUSH, EVENT_RELEASE] * 3, events_before_end)
        self.assertEqual([EVENT_ENTER, EVENT_FLUSH, EVENT_RELEASE] * 3 + [EVENT_EXIT], connection.events())
        self.assertEqual([NO_ERROR], connection.exit_arguments())

    def test_g3_two_factories_each_get_one_connection_ended_in_join_order(self):
        journal = []
        factory_a = RecordingConnectionFactory(journal)
        factory_b = RecordingConnectionFactory(journal)

        @Transaction()
        def a_then_b_then_a():
            with factory_a.get():
                pass
            with factory_b.get():
                pass
            with factory_a.get():
                pass

        a_then_b_then_a()

        self.assertEqual(1, len(factory_a.created))
        self.assertEqual(1, len(factory_b.created))
        connection_a, connection_b = factory_a.created[0], factory_b.created[0]
        exits = [(connection, arguments) for connection, event, arguments in journal if event == EVENT_EXIT]
        self.assertEqual([(connection_a, NO_ERROR), (connection_b, NO_ERROR)], exits)
        self.assertEqual((connection_b, EVENT_EXIT, NO_ERROR), journal[-1])

    def test_g4_an_error_inside_a_block_skips_its_flush_and_rolls_every_connection_back(self):
        journal = []
        factory_a = RecordingConnectionFactory(journal)
        factory_b = RecordingConnectionFactory(journal)
        failure = RuntimeError('second block failed')

        @Transaction()
        def fail_in_second_block():
            with factory_a.get():
                pass
            with factory_b.get():
                raise failure

        with self.assertRaises(RuntimeError) as raised:
            fail_in_second_block()

        self.assertIs(failure, raised.exception)
        connection_a, connection_b = factory_a.created[0], factory_b.created[0]
        self.assertEqual([EVENT_ENTER, EVENT_FLUSH, EVENT_RELEASE, EVENT_EXIT], connection_a.events())
        self.assertEqual([EVENT_ENTER, EVENT_RELEASE, EVENT_EXIT], connection_b.events())   # the failed block sent nothing
        for connection in (connection_a, connection_b):
            [(exec_type, exec_value, traceback)] = connection.exit_arguments()
            self.assertIs(RuntimeError, exec_type)
            self.assertIs(failure, exec_value)
            self.assertIsInstance(traceback, types.TracebackType)

    def test_g5_a_failed_commit_rolls_back_the_rest_and_skips_after_commit_callbacks(self):
        journal = []
        commit_failure = ConnectionError('commit of A failed')
        factory_a = RecordingConnectionFactory(journal, commit_error=commit_failure)
        factory_b = RecordingConnectionFactory(journal)
        callbacks_run = []

        @Transaction()
        def use_a_then_b():
            with factory_a.get():
                pass
            with factory_b.get():
                pass
            CoreLib.transaction_scope_registry.get().on_commit.append(lambda: callbacks_run.append('after commit'))

        with self.assertRaises(ConnectionError) as raised:
            use_a_then_b()

        self.assertIs(commit_failure, raised.exception)
        self.assertEqual([NO_ERROR], factory_a.created[0].exit_arguments())
        [(exec_type, exec_value, traceback)] = factory_b.created[0].exit_arguments()
        self.assertIs(ConnectionError, exec_type)
        self.assertIs(commit_failure, exec_value)
        self.assertIsInstance(traceback, types.TracebackType)
        self.assertEqual([], callbacks_run)

    def test_g5_a_rollback_failing_after_a_failed_commit_is_logged_and_the_commit_error_wins(self):
        journal = []
        commit_failure = ConnectionError('commit of A failed')
        rollback_failure = OSError('rollback of B failed')
        factory_a = RecordingConnectionFactory(journal, commit_error=commit_failure)
        factory_b = RecordingConnectionFactory(journal, rollback_error=rollback_failure)
        factory_c = RecordingConnectionFactory(journal)

        @Transaction()
        def use_three():
            for factory in (factory_a, factory_b, factory_c):
                with factory.get():
                    pass

        with self.assertLogs(SCOPE_LOGGER, 'ERROR') as logs:
            with self.assertRaises(ConnectionError) as raised:
                use_three()

        self.assertIs(commit_failure, raised.exception)
        self.assertEqual(1, len(logs.records))
        self.assertIn('rolling back RecordingConnection failed', logs.records[0].getMessage())
        self.assertIs(rollback_failure, logs.records[0].exc_info[1])
        self.assertIs(commit_failure, factory_c.created[0].exit_arguments()[0][1])

    def test_g6_a_failed_rollback_is_logged_the_rest_still_roll_back_and_the_original_error_wins(self):
        journal = []
        rollback_failure = OSError('rollback of A failed')
        factory_a = RecordingConnectionFactory(journal, rollback_error=rollback_failure)
        factory_b = RecordingConnectionFactory(journal)
        failure = KeyError('work failed')

        @Transaction()
        def fail_after_both():
            with factory_a.get():
                pass
            with factory_b.get():
                pass
            raise failure

        with self.assertLogs(SCOPE_LOGGER, 'ERROR') as logs:
            with self.assertRaises(KeyError) as raised:
                fail_after_both()

        self.assertIs(failure, raised.exception)
        self.assertEqual(KeyError, factory_a.created[0].exit_arguments()[0][0])
        [(exec_type, exec_value, _)] = factory_b.created[0].exit_arguments()
        self.assertIs(KeyError, exec_type)
        self.assertIs(failure, exec_value)
        self.assertEqual(1, len(logs.records))
        self.assertIn('rolling back RecordingConnection failed', logs.records[0].getMessage())
        self.assertIs(rollback_failure, logs.records[0].exc_info[1])

    def test_g7_a_factory_failing_to_connect_rolls_back_what_joined_and_stores_nothing(self):
        journal = []
        create_failure = LookupError('cannot connect B')
        factory_a = RecordingConnectionFactory(journal)
        factory_b = RecordingConnectionFactory(journal, create_error=create_failure)

        @Transaction()
        def use_a_then_b():
            with factory_a.get():
                pass
            with factory_b.get():
                pass

        with self.assertRaises(LookupError) as raised:
            use_a_then_b()

        self.assertIs(create_failure, raised.exception)
        [(exec_type, exec_value, _)] = factory_a.created[0].exit_arguments()
        self.assertIs(LookupError, exec_type)
        self.assertIs(create_failure, exec_value)
        self.assertEqual([], factory_b.created)
        self.assertEqual({factory_a.created[0]}, {entry[0] for entry in journal})

    def test_g7_after_a_failed_connect_the_next_get_connects_again(self):
        factory = RecordingConnectionFactory(create_error=LookupError('first attempt fails'))
        retried = []

        @Transaction()
        def retry_after_failure():
            with self.assertRaises(LookupError):
                factory.get()
            factory.create_error = None
            with factory.get() as resource:
                retried.append(resource)

        retry_after_failure()

        self.assertEqual(2, factory.connect_attempts)
        self.assertEqual(1, len(factory.created))
        self.assertEqual([factory.created[0].resource], retried)
        self.assertEqual([NO_ERROR], factory.created[0].exit_arguments())

    def test_g8_factories_that_do_not_join_behave_inside_as_outside(self):
        counts = {'new': 0, 'close': 0}

        def new_session(obj):
            counts['new'] += 1
            return {'session_of': obj, 'number': counts['new']}

        def close_session(session):
            counts['close'] += 1

        object_factory = ObjectConnectionFactory('acme', new_session, close_session)
        mongo_factory = connect_to_mongo()

        def two_blocks_each():
            sessions = []
            for i in range(2):
                with object_factory.get() as session:
                    sessions.append(session)
                with mongo_factory.get() as client:
                    sessions.append(client)
            return sessions

        outside = two_blocks_each()
        inside = Transaction()(two_blocks_each)()

        self.assertEqual({'new': 4, 'close': 4}, counts)
        self.assertIsNot(outside[0], outside[2])
        self.assertIsNot(inside[0], inside[2])
        self.assertIs(mongo_factory.client, inside[1])
        self.assertIs(mongo_factory.client, inside[3])

    def test_g10_the_current_scope_exists_only_while_the_outermost_function_runs(self):
        seen = {}

        @Transaction()
        def inner():
            seen['nested'] = CoreLib.transaction_scope_registry.get()

        @Transaction()
        def outer(should_fail: bool):
            seen['inside'] = CoreLib.transaction_scope_registry.get()
            inner()
            if should_fail:
                raise RuntimeError('fail on purpose')

        self.assertIsNone(CoreLib.transaction_scope_registry.get())
        outer(False)
        self.assertIsInstance(seen['inside'], TransactionScope)
        self.assertIs(seen['inside'], seen['nested'])
        self.assertIsNone(CoreLib.transaction_scope_registry.get())

        with self.assertRaises(RuntimeError):
            outer(True)
        self.assertIsNone(CoreLib.transaction_scope_registry.get())

    def test_g11_keeps_name_doc_arguments_and_return_value(self):
        def add_widget(group_id, name, suffix='-widget'):
            """Join the parts."""
            return '{}:{}{}'.format(group_id, name, suffix)

        wrapped = Transaction()(add_widget)

        self.assertEqual('add_widget', wrapped.__name__)
        self.assertEqual('Join the parts.', wrapped.__doc__)
        self.assertEqual('7:acme-widget', wrapped(7, 'acme'))
        self.assertEqual('7:acme!', wrapped(7, name='acme', suffix='!'))

    def test_g12_a_swallowed_inner_failure_still_commits(self):
        factory = RecordingConnectionFactory()

        @Transaction()
        def inner():
            with factory.get():
                pass
            raise RuntimeError('inner failed')

        @Transaction()
        def outer():
            try:
                inner()
            except RuntimeError:
                pass
            return 'done'

        self.assertEqual('done', outer())
        self.assertEqual([NO_ERROR], factory.created[0].exit_arguments())

    def test_g13_after_commit_callbacks_run_last_in_order_outside_the_scope(self):
        journal = []
        factory_a = RecordingConnectionFactory(journal)
        factory_b = RecordingConnectionFactory(journal)
        runs = []

        def callback(number):
            def run():
                exits = [event for event in journal if event[1] == EVENT_EXIT]
                runs.append((number, len(exits), CoreLib.transaction_scope_registry.get()))
            return run

        @Transaction()
        def register_three():
            with factory_a.get():
                pass
            with factory_b.get():
                pass
            scope = CoreLib.transaction_scope_registry.get()
            scope.on_commit.append(callback(1))
            scope.on_commit.append(callback(2))
            scope.on_commit.append(callback(3))

        register_three()

        self.assertEqual([(1, 2, None), (2, 2, None), (3, 2, None)], runs)

    def test_g13_after_commit_callbacks_never_run_on_rollback(self):
        factory = RecordingConnectionFactory()
        runs = []

        @Transaction()
        def register_then_fail():
            with factory.get():
                pass
            CoreLib.transaction_scope_registry.get().on_commit.append(lambda: runs.append('ran'))
            raise RuntimeError('rolled back')

        with self.assertRaises(RuntimeError):
            register_then_fail()

        self.assertEqual([], runs)
        self.assertIs(RuntimeError, factory.created[0].exit_arguments()[0][0])

    def test_g14_a_transactional_connection_and_factory_must_implement_their_abstract_methods(self):
        class FactoryWithoutCreateConnection(TransactionalConnectionFactory):
            pass

        class ConnectionWithoutItsMethods(TransactionalConnection):
            pass

        with self.assertRaises(TypeError) as factory_error:
            FactoryWithoutCreateConnection()
        with self.assertRaises(TypeError) as connection_error:
            ConnectionWithoutItsMethods()

        for method in ('create_connection', 'identity'):
            self.assertIn(method, str(factory_error.exception))
        for method in ('open', 'flush', 'release', 'end'):
            self.assertIn(method, str(connection_error.exception))
        self.assertFalse(RecordingConnection([]).in_transaction)
