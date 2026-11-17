"""@Transaction() at the connection level, for every connection type: one connection per factory,
ended once, in join order, with after-commit callbacks (no SQL needed)."""
import types
import unittest
from unittest import mock

from core_lib.connection import mongodb_connection_factory
from core_lib.connection.mongodb_connection import MongoDBConnection
from core_lib.connection.object_connection_factory import ObjectConnectionFactory
from core_lib.connection.transaction_decorator import Transaction
from core_lib.connection.transaction_scope import TransactionScope
from tests.test_data.recording_connection import EVENT_ENTER, EVENT_EXIT, EVENT_FLUSH, NO_ERROR
from tests.test_data.recording_connection_factory import RecordingConnectionFactory
from tests.test_data.test_utils import connect_to_mongo

SCOPE_LOGGER = 'core_lib.connection.transaction_scope'


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
        self.assertEqual([EVENT_ENTER, EVENT_FLUSH, EVENT_FLUSH, EVENT_FLUSH], events_before_end)
        self.assertEqual([EVENT_ENTER, EVENT_FLUSH, EVENT_FLUSH, EVENT_FLUSH, EVENT_EXIT], connection.events())
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
        self.assertEqual([EVENT_ENTER, EVENT_FLUSH, EVENT_EXIT], connection_a.events())
        self.assertEqual([EVENT_ENTER, EVENT_EXIT], connection_b.events())
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
            TransactionScope.current().on_commit(lambda: callbacks_run.append('after commit'))

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
        self.assertIn('after a failed commit failed', logs.records[0].getMessage())
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
        self.assertIn('rollback of RecordingConnection failed', logs.records[0].getMessage())
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

        self.assertEqual(2, len(factory.create_calls))
        self.assertEqual(1, len(factory.created))
        self.assertEqual([factory.created[0].resource], retried)
        self.assertEqual([NO_ERROR], factory.created[0].exit_arguments())

    def test_g8_object_connection_factory_opens_and_closes_once_per_transaction(self):
        counts = {'new': 0, 'close': 0}
        closes_before_end = []

        def new_session(obj):
            counts['new'] += 1
            return {'session_of': obj, 'number': counts['new']}

        def close_session(session):
            counts['close'] += 1

        factory = ObjectConnectionFactory('acme', new_session, close_session)

        @Transaction()
        def two_blocks():
            sessions = []
            for i in range(2):
                with factory.get() as session:
                    sessions.append(session)
            closes_before_end.append(counts['close'])
            return sessions

        sessions = two_blocks()
        self.assertEqual({'new': 1, 'close': 1}, counts)
        self.assertEqual([0], closes_before_end)
        self.assertIs(sessions[0], sessions[1])

        with factory.get():
            pass
        with factory.get():
            pass
        self.assertEqual({'new': 3, 'close': 3}, counts)

    def test_g9_mongo_joins_through_the_base_no_op_flush(self):
        factory = connect_to_mongo()
        clients = []

        @Transaction()
        def two_blocks():
            for i in range(2):
                with factory.get() as client:
                    clients.append(client)

        with mock.patch.object(mongodb_connection_factory, MongoDBConnection.__name__,
                               wraps=MongoDBConnection) as connection_class:
            two_blocks()

        self.assertEqual(1, connection_class.call_count)
        self.assertIs(factory.client, clients[0])
        self.assertIs(clients[0], clients[1])

    def test_g10_the_current_scope_exists_only_while_the_outermost_function_runs(self):
        seen = {}

        @Transaction()
        def inner():
            seen['nested'] = TransactionScope.current()

        @Transaction()
        def outer(should_fail: bool):
            seen['inside'] = TransactionScope.current()
            inner()
            if should_fail:
                raise RuntimeError('fail on purpose')

        self.assertIsNone(TransactionScope.current())
        outer(False)
        self.assertIsInstance(seen['inside'], TransactionScope)
        self.assertIs(seen['inside'], seen['nested'])
        self.assertIsNone(TransactionScope.current())

        with self.assertRaises(RuntimeError):
            outer(True)
        self.assertIsNone(TransactionScope.current())

    def test_g11_refuses_functions_that_return_before_their_body_runs(self):
        async def coroutine():
            pass

        def generator():
            yield 1

        async def async_generator():
            yield 1

        for function in (coroutine, generator, async_generator):
            with self.assertRaises(ValueError) as raised:
                Transaction()(function)
            self.assertIn(function.__qualname__, str(raised.exception))

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
        callback_failure = RuntimeError('second callback failed')
        runs = []

        def callback(number, should_fail=False):
            def run():
                exits = [event for event in journal if event[1] == EVENT_EXIT]
                runs.append((number, len(exits), TransactionScope.current()))
                if should_fail:
                    raise callback_failure
            return run

        @Transaction()
        def register_three():
            with factory_a.get():
                pass
            with factory_b.get():
                pass
            scope = TransactionScope.current()
            scope.on_commit(callback(1))
            scope.on_commit(callback(2, should_fail=True))
            scope.on_commit(callback(3))

        with self.assertRaises(RuntimeError) as raised:
            register_three()

        self.assertIs(callback_failure, raised.exception)
        self.assertEqual([(1, 2, None), (2, 2, None), (3, 2, None)], runs)

    def test_g13_a_second_failing_callback_is_logged_and_the_first_error_wins(self):
        first_failure = RuntimeError('first')
        second_failure = RuntimeError('second')

        def fail_with(error):
            def run():
                raise error
            return run

        @Transaction()
        def register_two_failing():
            TransactionScope.current().on_commit(fail_with(first_failure))
            TransactionScope.current().on_commit(fail_with(second_failure))

        with self.assertLogs(SCOPE_LOGGER, 'ERROR') as logs:
            with self.assertRaises(RuntimeError) as raised:
                register_two_failing()

        self.assertIs(first_failure, raised.exception)
        self.assertEqual(1, len(logs.records))
        self.assertIs(second_failure, logs.records[0].exc_info[1])

    def test_g13_after_commit_callbacks_never_run_on_rollback(self):
        factory = RecordingConnectionFactory()
        runs = []

        @Transaction()
        def register_then_fail():
            with factory.get():
                pass
            TransactionScope.current().on_commit(lambda: runs.append('ran'))
            raise RuntimeError('rolled back')

        with self.assertRaises(RuntimeError):
            register_then_fail()

        self.assertEqual([], runs)
        self.assertIs(RuntimeError, factory.created[0].exit_arguments()[0][0])

    def test_g14_later_arguments_reuse_the_first_connection(self):
        factory = RecordingConnectionFactory()
        resources = []

        @Transaction()
        def two_gets():
            with factory.get('x') as resource:
                resources.append(resource)
            with factory.get('y') as resource:
                resources.append(resource)

        two_gets()

        self.assertEqual([(('x',), {})], factory.create_calls)
        self.assertEqual([factory.created[0].resource] * 2, resources)

    def test_g15_a_subclass_joins_once_whether_it_inherits_get_or_calls_super_get(self):
        class InheritingConnectionFactory(RecordingConnectionFactory):
            pass

        class SuperCallingConnectionFactory(RecordingConnectionFactory):
            def get(self, *args, **kwargs):
                self.journal.append((None, 'own get', None))
                return super().get(*args, **kwargs)

        inheriting = InheritingConnectionFactory()
        factory = SuperCallingConnectionFactory()

        @Transaction()
        def two_blocks():
            for i in range(2):
                with factory.get():
                    pass
                with inheriting.get():
                    pass

        two_blocks()
        with factory.get():
            pass

        self.assertEqual(1, len(inheriting.created))
        self.assertEqual([NO_ERROR], inheriting.created[0].exit_arguments())
        self.assertEqual(2, [entry[1] for entry in factory.journal].count('own get'))
        inside, outside = factory.created
        self.assertEqual([EVENT_ENTER, EVENT_FLUSH, EVENT_FLUSH, EVENT_EXIT], inside.events())
        self.assertEqual([NO_ERROR], inside.exit_arguments())
        self.assertEqual([EVENT_ENTER, EVENT_EXIT], outside.events())
