"""Cover abstract method `pass` bodies and very-thin classes via concrete subclasses."""
import unittest
from datetime import timedelta

from core_lib.cache.cache_handler import CacheHandler
from core_lib.connection.connection import Connection
from core_lib.factory.factory import Factory
from core_lib.jobs.job import Job
from core_lib.middleware.middleware import Middleware
from core_lib.observer.observer_listener import ObserverListener
from core_lib.registry.registry import Registry
from core_lib.session.token_handler import TokenHandler


class TestCacheHandlerAbstract(unittest.TestCase):
    def test_concrete_can_call_abstract_pass_bodies(self):
        class C(CacheHandler):
            def get(self, key):
                return super().get(key)
            def set(self, key: str, value, expire: timedelta):
                return super().set(key, value, expire)
            def delete(self, key: str):
                return super().delete(key)
            def flush_all(self):
                return super().flush_all()
        c = C()
        self.assertIsNone(c.get('k'))
        self.assertIsNone(c.set('k', 1, timedelta(seconds=1)))
        self.assertIsNone(c.delete('k'))
        self.assertIsNone(c.flush_all())


class TestConnectionAbstract(unittest.TestCase):
    def test_concrete_subclass_pass(self):
        class C(Connection):
            def __enter__(self):
                return super().__enter__()
            def __exit__(self, type, value, traceback):
                return super().__exit__(type, value, traceback)
        with C() as c:
            self.assertIsNone(c)


class TestFactoryAbstract(unittest.TestCase):
    def test_factory_pass(self):
        class F(Factory):
            def get(self, *a, **k):
                return super().get(*a, **k)
        self.assertIsNone(F().get())


class TestJobAbstract(unittest.TestCase):
    def test_job_set_data_handler_calls_initialized(self):
        captured = {}
        class J(Job):
            def initialized(self, data_handler):
                captured['dh'] = data_handler
                return super().initialized(data_handler)
            def run(self):
                return super().run()
        j = J()
        j.set_data_handler('handler')
        self.assertEqual(captured['dh'], 'handler')
        self.assertIsNone(j.run())


class TestMiddlewareAbstract(unittest.TestCase):
    def test_middleware_pass(self):
        class M(Middleware):
            def handle(self, context):
                return super().handle(context)
        self.assertIsNone(M().handle({}))


class TestObserverListenerAbstract(unittest.TestCase):
    def test_pass(self):
        class L(ObserverListener):
            def update(self, key, value):
                return super().update(key, value)
        self.assertIsNone(L().update('k', 'v'))


class TestRegistryAbstract(unittest.TestCase):
    def test_registry_pass(self):
        class R(Registry):
            def get(self, *a, **k):
                return super().get(*a, **k)
        self.assertIsNone(R().get())


class TestTokenHandlerAbstract(unittest.TestCase):
    def test_token_handler_pass(self):
        class T(TokenHandler):
            def encode(self, message):
                return super().encode(message)
            def decode(self, encoded):
                return super().decode(encoded)
        t = T()
        self.assertIsNone(t.encode({}))
        self.assertIsNone(t.decode(''))


class TestCoreLibListenerAbstract(unittest.TestCase):
    def test_listener_dispatch(self):
        from core_lib.core_lib_listener import CoreLibListener

        events = []

        class L(CoreLibListener):
            def on_core_lib_ready(self):
                events.append('ready')
                return super().on_core_lib_ready()

            def on_core_lib_destroy(self):
                events.append('destroy')
                return super().on_core_lib_destroy()

        listener = L()
        listener.update(CoreLibListener.CoreLibEventType.CORE_LIB_READY, None)
        listener.update(CoreLibListener.CoreLibEventType.CORE_LIB_DESTROY, None)
        listener.update('ignored', None)
        self.assertEqual(events, ['ready', 'destroy'])
