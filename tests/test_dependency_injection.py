import unittest
import threading
from http import HTTPStatus

from core_lib.dependency_injection.di_container import DIContainer
from core_lib.error_handling.status_code_exception import StatusCodeException
import time
import abc


class TestDependencyInjection(unittest.TestCase):

    def test_bind_and_resolve_instance_and_factory(self):
        container = DIContainer()

        # Bind plain instance
        instance_obj = object()
        container.bind('plain_instance', instance_obj)
        self.assertIs(container.resolve('plain_instance'), instance_obj)

        # Bind factory
        class Foo:
            def __init__(self):
                self.value = 42

        container.bind(Foo, Foo)
        foo_instance = container.resolve(Foo)
        self.assertIsInstance(foo_instance, Foo)
        self.assertEqual(foo_instance.value, 42)

    def test_singleton(self):
        container = DIContainer()

        class Bar:
            def __init__(self):
                self.value = time.time()

        container.bind(Bar, Bar, singleton=True)
        first = container.resolve(Bar)
        second = container.resolve(Bar)
        self.assertIs(first, second)

    def test_singleton_thread_safety(self):
        """Verify that only one singleton instance is created even with concurrent access."""
        container = DIContainer()

        class SlowSingleton:
            def __init__(self):
                time.sleep(0.1)
                self.value = threading.get_ident()

        container.bind(SlowSingleton, SlowSingleton, singleton=True)

        results = []

        def resolve_instance():
            results.append(container.resolve(SlowSingleton))

        threads = [threading.Thread(target=resolve_instance) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        first_instance = results[0]
        for inst in results[1:]:
            self.assertIs(inst, first_instance)

    def test_missing_key_raises(self):
        container = DIContainer()
        with self.assertRaises(StatusCodeException) as cm:
            container.resolve('unknown')
        self.assertEqual(cm.exception.status_code, HTTPStatus.NOT_FOUND)

    def test_circular_dependency_detection(self):
        container = DIContainer()

        class A:
            def __init__(self, b: 'B'):
                self.b = b

        class B:
            def __init__(self, a: A):
                self.a = a

        container.bind(A, A)
        container.bind(B, B)

        with self.assertRaises(StatusCodeException) as cm:
            container.resolve(A)
        self.assertEqual(cm.exception.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertIn('Circular dependency detected', str(cm.exception))

    def test_circular_dependency_chain_reporting(self):
        """Verify circular dependency error message shows the full chain."""
        container = DIContainer()

        class A:
            def __init__(self, b: 'B'):
                pass

        class B:
            def __init__(self, c: 'C'):
                pass

        class C:
            def __init__(self, a: A):
                pass

        container.bind(A, A)
        container.bind(B, B)
        container.bind(C, C)

        with self.assertRaises(StatusCodeException) as cm:
            container.resolve(A)
        error_msg = str(cm.exception)
        self.assertIn('Circular dependency detected', error_msg)
        # Chain should be visible in error
        self.assertIn('A', error_msg)
        self.assertIn('B', error_msg)
        self.assertIn('C', error_msg)

    def test_factory_with_primitive_default(self):
        container = DIContainer()

        class C:
            def __init__(self, x: int = 10):
                self.x = x

        container.bind(C, C)
        instance = container.resolve(C)
        self.assertEqual(instance.x, 10)

    def test_factory_with_unresolvable_parameter_raises(self):
        container = DIContainer()

        class D:
            def __init__(self, y):
                self.y = y

        container.bind(D, D)
        with self.assertRaises(StatusCodeException) as cm:
            container.resolve(D)
        self.assertIn('Cannot resolve dependency', str(cm.exception))

    def test_interface_binding(self):
        container = DIContainer()

        class IService(abc.ABC):
            @abc.abstractmethod
            def do_something(self):
                pass

        class ServiceImpl(IService):
            def do_something(self):
                return "ok"

        container.bind(IService, ServiceImpl)
        instance = container.resolve(IService)
        self.assertIsInstance(instance, ServiceImpl)
        self.assertEqual(instance.do_something(), "ok")

    def test_unhinted_required_parameter(self):
        container = DIContainer()

        class F:
            def __init__(self, a, b: int = 5):
                self.a = a
                self.b = b

        container.bind(F, F)
        with self.assertRaises(StatusCodeException) as cm:
            container.resolve(F)
        self.assertIn("Cannot resolve dependency for parameter", str(cm.exception))

    def test_binding_primitive_directly(self):
        container = DIContainer()
        container.bind(int, 123)
        container.bind(str, "hello")
        container.bind(dict, {"key": "value"})

        self.assertEqual(container.resolve(int), 123)
        self.assertEqual(container.resolve(str), "hello")
        self.assertEqual(container.resolve(dict), {"key": "value"})

    def test_thread_local_resolving_isolated(self):
        """Verify that resolution stacks are isolated per thread."""
        container = DIContainer()

        class A:
            def __init__(self, b: 'B'):
                self.b = b

        class B:
            def __init__(self):
                pass

        container.bind(A, A)
        container.bind(B, B)

        results = []

        def resolve_A():
            try:
                results.append(container.resolve(A))
            except StatusCodeException as e:
                results.append(str(e))

        threads = [threading.Thread(target=resolve_A) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        for r in results:
            self.assertIsInstance(r, A)

    # ============================================================================
    # EDGE CASE TESTS
    # ============================================================================

    def test_non_singleton_factory_side_effects_interleaved(self):
        """Test that factory side effects can interleave for non-singletons (expected behavior)."""
        container = DIContainer()

        execution_order = []
        lock = threading.Lock()

        class SlowFactory:
            def __init__(self):
                with lock:
                    execution_order.append('start')
                time.sleep(0.05)
                with lock:
                    execution_order.append('end')

        container.bind(SlowFactory, SlowFactory, singleton=False)

        def resolve_factory():
            container.resolve(SlowFactory)

        threads = [threading.Thread(target=resolve_factory) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should see interleaved starts and ends (not all starts then all ends)
        # This verifies that factory execution is NOT locked
        self.assertEqual(len(execution_order), 6)  # 3 starts + 3 ends
        # Count starts before the last end
        starts_before_last_end = execution_order[:execution_order.rfind('end')]
        self.assertGreater(len(starts_before_last_end), 1, "Factory side effects should be interleaved")

    def test_non_singleton_creates_new_instances_concurrently(self):
        """Verify that non-singleton factories create separate instances even with concurrent access."""
        container = DIContainer()

        class NonSingleton:
            instance_count = 0

            def __init__(self):
                NonSingleton.instance_count += 1
                self.id = NonSingleton.instance_count
                time.sleep(0.05)

        container.bind(NonSingleton, NonSingleton, singleton=False)

        results = []

        def resolve_non_singleton():
            results.append(container.resolve(NonSingleton))

        threads = [threading.Thread(target=resolve_non_singleton) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Each should be a different instance
        self.assertEqual(len(results), 3)
        ids = [r.id for r in results]
        self.assertEqual(len(set(ids)), 3, "Non-singleton should create separate instances")

    def test_circular_dependency_with_thread_local_isolation(self):
        """Verify that circular dependency detection works correctly with thread-local stacks."""
        container = DIContainer()

        class X:
            def __init__(self, y: 'Y'):
                self.y = y

        class Y:
            def __init__(self, x: X):
                self.x = x

        container.bind(X, X)
        container.bind(Y, Y)

        results = []

        def try_resolve():
            try:
                container.resolve(X)
                results.append(None)
            except StatusCodeException as e:
                results.append('circular_detected')

        threads = [threading.Thread(target=try_resolve) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Both threads should independently detect circular dependency
        self.assertEqual(results, ['circular_detected', 'circular_detected'])

    def test_unhinted_required_parameter_error_on_resolution(self):
        """Verify error is raised during resolution, not at bind time."""
        container = DIContainer()

        class G:
            def __init__(self, unnamed_param):
                pass

        # Binding should succeed
        container.bind(G, G)

        # Resolution should fail
        with self.assertRaises(StatusCodeException) as cm:
            container.resolve(G)
        self.assertEqual(cm.exception.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertIn('Cannot resolve dependency', str(cm.exception))
        self.assertIn('unnamed_param', str(cm.exception))

    def test_multiple_unhinted_parameters_error_reports_first(self):
        """Verify error message identifies the problematic parameter."""
        container = DIContainer()

        class H:
            def __init__(self, first_untyped, second_untyped):
                pass

        container.bind(H, H)

        with self.assertRaises(StatusCodeException) as cm:
            container.resolve(H)
        error_msg = str(cm.exception)
        self.assertIn('first_untyped', error_msg)

    def test_mixed_typed_and_untyped_parameters(self):
        """Verify typed params are resolved but untyped without defaults fail."""
        container = DIContainer()

        class Service:
            def __init__(self):
                pass

        class Consumer:
            def __init__(self, service: Service, untyped_param):
                self.service = service
                self.untyped = untyped_param

        container.bind(Service, Service)
        container.bind(Consumer, Consumer)

        with self.assertRaises(StatusCodeException) as cm:
            container.resolve(Consumer)
        self.assertIn('Cannot resolve dependency', str(cm.exception))
        self.assertIn('untyped_param', str(cm.exception))

    def test_nested_dependency_resolution(self):
        """Verify deep dependency chains resolve correctly."""
        container = DIContainer()

        class Level1:
            pass

        class Level2:
            def __init__(self, l1: Level1):
                self.l1 = l1

        class Level3:
            def __init__(self, l2: Level2):
                self.l2 = l2

        class Level4:
            def __init__(self, l3: Level3):
                self.l3 = l3

        container.bind(Level1, Level1)
        container.bind(Level2, Level2)
        container.bind(Level3, Level3)
        container.bind(Level4, Level4)

        result = container.resolve(Level4)
        self.assertIsInstance(result, Level4)
        self.assertIsInstance(result.l3, Level3)
        self.assertIsInstance(result.l3.l2, Level2)
        self.assertIsInstance(result.l3.l2.l1, Level1)

    def test_default_value_with_none(self):
        """Verify None as a default value is properly handled."""
        container = DIContainer()

        class WithNoneDefault:
            def __init__(self, value=None):
                self.value = value

        container.bind(WithNoneDefault, WithNoneDefault)
        instance = container.resolve(WithNoneDefault)
        self.assertIsNone(instance.value)

    def test_default_value_with_mutable_object(self):
        """Verify mutable default values work (though not best practice)."""
        container = DIContainer()

        default_list = [1, 2, 3]

        class WithListDefault:
            def __init__(self, items=default_list):
                self.items = items

        container.bind(WithListDefault, WithListDefault)
        instance = container.resolve(WithListDefault)
        self.assertIs(instance.items, default_list)

    def test_singleton_with_failed_resolution_doesnt_cache(self):
        """Verify failed singleton resolution doesn't cache a broken state."""
        container = DIContainer()

        class Dependency:
            pass

        class FailingSingleton:
            def __init__(self, dep: Dependency):
                self.dep = dep

        container.bind(FailingSingleton, FailingSingleton, singleton=True)

        # First attempt fails (Dependency not bound)
        with self.assertRaises(StatusCodeException):
            container.resolve(FailingSingleton)

        # Now bind the dependency
        container.bind(Dependency, Dependency)

        # Should succeed on retry (not cached as failed)
        instance = container.resolve(FailingSingleton)
        self.assertIsInstance(instance, FailingSingleton)

    def test_string_forward_reference_type_hint(self):
        """Verify string type hints work for forward references."""
        container = DIContainer()

        class Forward:
            def __init__(self, ref: 'Forward'):
                self.ref = ref

        container.bind(Forward, Forward)

        # This should detect circular dependency
        with self.assertRaises(StatusCodeException) as cm:
            container.resolve(Forward)
        self.assertIn('Circular dependency detected', str(cm.exception))

    def test_callable_check_with_lambda(self):
        """Verify lambdas are treated as callables."""
        container = DIContainer()

        container.bind('lambda_key', lambda: 42)
        result = container.resolve('lambda_key')
        self.assertEqual(result, 42)

    def test_callable_check_with_builtin_type(self):
        """Verify builtin types (which are callable) work as factories."""
        container = DIContainer()

        container.bind('list_factory', list)
        result = container.resolve('list_factory')
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_concurrent_different_singleton_resolutions(self):
        """Verify different singletons can be resolved concurrently without interference."""
        container = DIContainer()

        class Singleton1:
            def __init__(self):
                time.sleep(0.05)
                self.name = 's1'

        class Singleton2:
            def __init__(self):
                time.sleep(0.05)
                self.name = 's2'

        container.bind(Singleton1, Singleton1, singleton=True)
        container.bind(Singleton2, Singleton2, singleton=True)

        results = {'s1': [], 's2': []}

        def resolve_s1():
            results['s1'].append(container.resolve(Singleton1))

        def resolve_s2():
            results['s2'].append(container.resolve(Singleton2))

        threads = (
            [threading.Thread(target=resolve_s1) for _ in range(2)] +
            [threading.Thread(target=resolve_s2) for _ in range(2)]
        )
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Each singleton should have single instance
        s1_ids = [id(x) for x in results['s1']]
        s2_ids = [id(x) for x in results['s2']]
        self.assertEqual(len(set(s1_ids)), 1)
        self.assertEqual(len(set(s2_ids)), 1)
        # But they should be different
        self.assertNotEqual(s1_ids[0], s2_ids[0])

    # ============================================================================
    # ADDITIONAL EDGE CASES
    # ============================================================================

    def test_long_circular_dependency_chain(self):
        """Test circular dependency detection with longer chain: A → B → C → D → A."""
        container = DIContainer()

        class A:
            def __init__(self, b: 'B'):
                self.b = b

        class B:
            def __init__(self, c: 'C'):
                self.c = c

        class C:
            def __init__(self, d: 'D'):
                self.d = d

        class D:
            def __init__(self, a: A):
                self.a = a

        container.bind(A, A)
        container.bind(B, B)
        container.bind(C, C)
        container.bind(D, D)

        with self.assertRaises(StatusCodeException) as cm:
            container.resolve(A)
        self.assertEqual(cm.exception.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertIn('Circular dependency detected', str(cm.exception))

    def test_factory_with_multiple_dependencies(self):
        """Test class with multiple constructor parameters requiring resolution."""
        container = DIContainer()

        class ServiceA:
            def __init__(self):
                self.name = 'A'

        class ServiceB:
            def __init__(self):
                self.name = 'B'

        class ServiceC:
            def __init__(self):
                self.name = 'C'

        class Consumer:
            def __init__(self, a: ServiceA, b: ServiceB, c: ServiceC):
                self.a = a
                self.b = b
                self.c = c

        container.bind(ServiceA, ServiceA)
        container.bind(ServiceB, ServiceB)
        container.bind(ServiceC, ServiceC)
        container.bind(Consumer, Consumer)

        instance = container.resolve(Consumer)
        self.assertIsInstance(instance.a, ServiceA)
        self.assertIsInstance(instance.b, ServiceB)
        self.assertIsInstance(instance.c, ServiceC)
        self.assertEqual(instance.a.name, 'A')
        self.assertEqual(instance.b.name, 'B')
        self.assertEqual(instance.c.name, 'C')

    def test_singleton_with_multiple_dependencies(self):
        """Verify singleton with dependencies is only instantiated once."""
        container = DIContainer()

        creation_count = {'count': 0}

        class Dependency:
            def __init__(self):
                creation_count['count'] += 1

        class SingletonWithDeps:
            def __init__(self, dep: Dependency):
                self.dep = dep

        container.bind(Dependency, Dependency, singleton=False)
        container.bind(SingletonWithDeps, SingletonWithDeps, singleton=True)

        first = container.resolve(SingletonWithDeps)
        second = container.resolve(SingletonWithDeps)
        third = container.resolve(SingletonWithDeps)

        self.assertIs(first, second)
        self.assertIs(second, third)
        # Dependency should be created 3 times (not a singleton)
        self.assertEqual(creation_count['count'], 3)

    def test_singleton_dependency_chain(self):
        """Verify a chain of singletons all resolve to the same instances."""
        container = DIContainer()

        class L1:
            pass

        class L2:
            def __init__(self, l1: L1):
                self.l1 = l1

        class L3:
            def __init__(self, l2: L2):
                self.l2 = l2

        container.bind(L1, L1, singleton=True)
        container.bind(L2, L2, singleton=True)
        container.bind(L3, L3, singleton=True)

        res1 = container.resolve(L3)
        res2 = container.resolve(L3)

        self.assertIs(res1, res2)
        self.assertIs(res1.l2, res2.l2)
        self.assertIs(res1.l2.l1, res2.l2.l1)

    def test_stress_test_concurrent_non_singletons(self):
        """Heavy concurrency stress test: resolve many non-singleton instances."""
        container = DIContainer()

        class Service:
            instances = []
            lock = threading.Lock()

            def __init__(self):
                with Service.lock:
                    Service.instances.append(self)

        container.bind(Service, Service, singleton=False)

        def resolve_many():
            for _ in range(10):
                container.resolve(Service)

        threads = [threading.Thread(target=resolve_many) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have created 100 distinct instances
        self.assertEqual(len(Service.instances), 100)

    def test_primitive_injectable_dependency(self):
        """Test that bound primitives can be injected as dependencies."""
        container = DIContainer()

        container.bind(int, 42)
        container.bind(str, "hello")
        container.bind(bool, True)

        class Config:
            def __init__(self, port: int, host: str, debug: bool):
                self.port = port
                self.host = host
                self.debug = debug

        container.bind(Config, Config)
        instance = container.resolve(Config)

        self.assertEqual(instance.port, 42)
        self.assertEqual(instance.host, "hello")
        self.assertTrue(instance.debug)

    def test_primitive_and_typed_dependency_mix(self):
        """Test mixing primitives with class dependencies."""
        container = DIContainer()

        class Logger:
            def log(self, msg):
                return f"LOG: {msg}"

        container.bind(str, "app_name")
        container.bind(int, 8080)
        container.bind(Logger, Logger)

        class AppConfig:
            def __init__(self, name: str, port: int, logger: Logger):
                self.name = name
                self.port = port
                self.logger = logger

        container.bind(AppConfig, AppConfig)
        instance = container.resolve(AppConfig)

        self.assertEqual(instance.name, "app_name")
        self.assertEqual(instance.port, 8080)
        self.assertIsInstance(instance.logger, Logger)

    def test_overwrite_binding(self):
        """Test that rebinding the same key overwrites the previous binding."""
        container = DIContainer()

        class Service:
            version = 1

        class ServiceV2:
            version = 2

        container.bind('service', Service)
        first = container.resolve('service')
        self.assertEqual(first.version, 1)

        # Overwrite binding
        container.bind('service', ServiceV2)
        second = container.resolve('service')
        self.assertEqual(second.version, 2)

    def test_overwrite_singleton_binding(self):
        """Test that rebinding clears cached singletons."""
        container = DIContainer()

        class V1:
            pass

        class V2:
            pass

        container.bind('singleton_key', V1, singleton=True)
        first = container.resolve('singleton_key')
        self.assertIsInstance(first, V1)

        # Rebind to different class
        container.bind('singleton_key', V2, singleton=True)
        second = container.resolve('singleton_key')
        self.assertIsInstance(second, V2)
        self.assertNotEqual(type(first), type(second))

    def test_provider_raises_exception(self):
        """Test that exceptions from providers propagate correctly."""
        container = DIContainer()

        def failing_factory():
            raise ValueError("Factory error")

        container.bind('failing', failing_factory)

        with self.assertRaises(ValueError) as cm:
            container.resolve('failing')
        self.assertEqual(str(cm.exception), "Factory error")

    def test_provider_raises_during_dependency_resolution(self):
        """Test exception in provider during dependency chain."""
        container = DIContainer()

        def failing_factory():
            raise RuntimeError("Dependency creation failed")

        class Dependent:
            def __init__(self, dep: 'FailingDep'):
                self.dep = dep

        class FailingDep:
            pass

        container.bind('FailingDep', failing_factory)
        container.bind(Dependent, Dependent)

        with self.assertRaises(RuntimeError) as cm:
            container.resolve(Dependent)
        self.assertEqual(str(cm.exception), "Dependency creation failed")

    def test_container_state_after_failed_resolution(self):
        """Verify container remains usable after a failed resolution."""
        container = DIContainer()

        class GoodService:
            pass

        class FailingDep:
            def __init__(self):
                raise RuntimeError("Init failed")

        class NeedsFailingDep:
            def __init__(self, dep: FailingDep):
                self.dep = dep

        container.bind(GoodService, GoodService)
        container.bind(FailingDep, FailingDep)
        container.bind(NeedsFailingDep, NeedsFailingDep)

        # First, try to resolve something that will fail
        with self.assertRaises(RuntimeError):
            container.resolve(NeedsFailingDep)

        # Container should still work for unaffected bindings
        good = container.resolve(GoodService)
        self.assertIsInstance(good, GoodService)

    def test_factory_with_optional_typed_parameter(self):
        """Test optional typed parameter with default value."""
        container = DIContainer()

        class Logger:
            pass

        class Service:
            def __init__(self, logger: Logger = None):
                self.logger = logger

        container.bind(Service, Service)
        # Logger is not bound, but has default None
        instance = container.resolve(Service)
        self.assertIsNone(instance.logger)

    def test_factory_with_optional_parameter_and_bound_dependency(self):
        """Test that bound dependencies override defaults."""
        container = DIContainer()

        class Logger:
            pass

        class Service:
            def __init__(self, logger: Logger = None):
                self.logger = logger

        container.bind(Logger, Logger)
        container.bind(Service, Service)

        instance = container.resolve(Service)
        self.assertIsInstance(instance.logger, Logger)

    def test_deeply_nested_primitives(self):
        """Test injection of primitives through multiple levels."""
        container = DIContainer()

        container.bind(int, 10)

        class L1:
            def __init__(self, num: int):
                self.num = num

        class L2:
            def __init__(self, l1: L1):
                self.l1 = l1

        class L3:
            def __init__(self, l2: L2):
                self.l2 = l2

        container.bind(L1, L1)
        container.bind(L2, L2)
        container.bind(L3, L3)

        instance = container.resolve(L3)
        self.assertEqual(instance.l2.l1.num, 10)

    def test_multiple_bindings_to_same_instance(self):
        """Test binding multiple keys to the same instance."""
        container = DIContainer()

        shared_obj = object()

        container.bind('key1', shared_obj)
        container.bind('key2', shared_obj)

        res1 = container.resolve('key1')
        res2 = container.resolve('key2')

        self.assertIs(res1, res2)
        self.assertIs(res1, shared_obj)

    def test_self_referencing_non_singleton(self):
        """Test that non-singleton doesn't have self-reference issue (each is separate)."""
        container = DIContainer()

        class SelfRef:
            def __init__(self, other: 'SelfRef' = None):
                self.other = other

        container.bind(SelfRef, SelfRef)

        # With default None, should not recurse
        instance = container.resolve(SelfRef)
        self.assertIsNone(instance.other)

    def test_exception_in_constructor_propagates(self):
        """Test that exceptions raised in __init__ propagate correctly."""
        container = DIContainer()

        class BadInit:
            def __init__(self):
                raise TypeError("Bad constructor logic")

        container.bind(BadInit, BadInit)

        with self.assertRaises(TypeError) as cm:
            container.resolve(BadInit)
        self.assertEqual(str(cm.exception), "Bad constructor logic")

    # ============================================================================
    # PERFORMANCE & STRESS TESTS
    # ============================================================================

    def test_heavy_concurrency_stress_test(self):
        """Stress test with high concurrency: 200 threads resolving singletons."""
        container = DIContainer()

        class HeavyService:
            instances_created = 0
            lock = threading.Lock()

            def __init__(self):
                with HeavyService.lock:
                    HeavyService.instances_created += 1

        container.bind(HeavyService, HeavyService, singleton=True)

        results = []

        def resolve_many():
            for _ in range(5):
                results.append(container.resolve(HeavyService))

        threads = [threading.Thread(target=resolve_many) for _ in range(200)]
        start_time = time.time()

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        elapsed = time.time() - start_time

        # Should have created only 1 instance despite 1000 resolve calls
        self.assertEqual(HeavyService.instances_created, 1)
        self.assertEqual(len(results), 1000)
        # All should be the same instance
        self.assertTrue(all(r is results[0] for r in results))
        # Should complete in reasonable time (< 30 seconds even with lock contention)
        self.assertLess(elapsed, 30)

    def test_heavy_concurrency_non_singleton(self):
        """Stress test non-singletons with high concurrency."""
        container = DIContainer()

        class Counter:
            instances = 0
            lock = threading.Lock()

            def __init__(self):
                with Counter.lock:
                    Counter.instances += 1

        container.bind(Counter, Counter, singleton=False)

        results = []

        def resolve_many():
            for _ in range(10):
                results.append(container.resolve(Counter))

        threads = [threading.Thread(target=resolve_many) for _ in range(100)]
        start_time = time.time()

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        elapsed = time.time() - start_time

        # Should have created 1000 instances
        self.assertEqual(Counter.instances, 1000)
        self.assertEqual(len(results), 1000)
        # All should be distinct
        result_ids = [id(r) for r in results]
        self.assertEqual(len(set(result_ids)), 1000)
        # Should complete in reasonable time
        self.assertLess(elapsed, 30)

    def test_heavy_concurrency_mixed_singletons_and_non_singletons(self):
        """Stress test with mix of singletons and non-singletons."""
        container = DIContainer()

        class SingletonA:
            pass

        class SingletonB:
            pass

        class NonSingletonC:
            count = 0
            lock = threading.Lock()

            def __init__(self):
                with NonSingletonC.lock:
                    NonSingletonC.count += 1

        container.bind(SingletonA, SingletonA, singleton=True)
        container.bind(SingletonB, SingletonB, singleton=True)
        container.bind(NonSingletonC, NonSingletonC, singleton=False)

        results = {'a': [], 'b': [], 'c': []}

        def resolve_all():
            for _ in range(5):
                results['a'].append(container.resolve(SingletonA))
                results['b'].append(container.resolve(SingletonB))
                results['c'].append(container.resolve(NonSingletonC))

        threads = [threading.Thread(target=resolve_all) for _ in range(50)]
        start_time = time.time()

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        elapsed = time.time() - start_time

        # Singletons should have 1 instance each
        a_ids = set(id(x) for x in results['a'])
        b_ids = set(id(x) for x in results['b'])
        self.assertEqual(len(a_ids), 1)
        self.assertEqual(len(b_ids), 1)

        # Non-singleton should have 250 instances
        self.assertEqual(NonSingletonC.count, 250)
        self.assertEqual(len(results['c']), 250)

        self.assertLess(elapsed, 30)

    def test_deep_dependency_chain_stress(self):
        """Stress test with very deep dependency chains."""
        container = DIContainer()

        # Create a chain of 50 classes
        classes = []
        for i in range(50):
            class_dict = {'__annotations__': {}}
            if i > 0:
                class_dict['__init__'] = lambda self, prev: setattr(self, 'prev', prev)
                class_dict['__annotations__']['prev'] = classes[i - 1]

            cls = type(f'Level{i}', (), class_dict)
            classes.append(cls)
            container.bind(cls, cls)

        start_time = time.time()
        result = container.resolve(classes[-1])
        elapsed = time.time() - start_time

        # Verify chain is built correctly
        current = result
        for i in range(49, 0, -1):
            self.assertIsInstance(current, classes[i])
            current = current.prev

        # Should complete reasonably fast
        self.assertLess(elapsed, 5)

    def test_large_number_of_bindings(self):
        """Test container with many (1000+) bindings."""
        container = DIContainer()

        # Create 1000 different classes and bind them
        classes = []
        for i in range(1000):
            cls = type(f'Service{i}', (), {'__init__': lambda self: None})
            classes.append(cls)
            container.bind(cls, cls)

        # Resolve a sample to verify they work
        for i in [0, 250, 500, 999]:
            instance = container.resolve(classes[i])
            self.assertIsInstance(instance, classes[i])

    def test_repeated_resolution_performance(self):
        """Verify singleton resolution is fast on repeated calls (no overhead)."""
        container = DIContainer()

        class QuickService:
            pass

        container.bind(QuickService, QuickService, singleton=True)

        # Warm up
        container.resolve(QuickService)

        # Time 10000 resolutions
        start_time = time.time()
        for _ in range(10000):
            container.resolve(QuickService)
        elapsed = time.time() - start_time

        # Should be very fast (< 1 second for 10k lookups)
        self.assertLess(elapsed, 1)

    # ============================================================================
    # CUSTOM KEY TYPES
    # ============================================================================

    def test_custom_key_type_tuple(self):
        """Test binding with tuple as key."""
        container = DIContainer()

        class Service:
            pass

        key = ('api', 'v1', 'service')
        container.bind(key, Service)

        instance = container.resolve(key)
        self.assertIsInstance(instance, Service)

    def test_custom_key_type_frozenset(self):
        """Test binding with frozenset as key."""
        container = DIContainer()

        service_obj = object()
        key = frozenset(['config', 'db'])

        container.bind(key, service_obj)
        result = container.resolve(key)
        self.assertIs(result, service_obj)

    def test_custom_key_type_enum(self):
        """Test binding with Enum as key."""
        from enum import Enum

        container = DIContainer()

        class ServiceType(Enum):
            DATABASE = 1
            CACHE = 2
            LOGGER = 3

        class DbService:
            pass

        class CacheService:
            pass

        container.bind(ServiceType.DATABASE, DbService)
        container.bind(ServiceType.CACHE, CacheService)

        db = container.resolve(ServiceType.DATABASE)
        cache = container.resolve(ServiceType.CACHE)

        self.assertIsInstance(db, DbService)
        self.assertIsInstance(cache, CacheService)

    def test_custom_key_type_mixed(self):
        """Test mixing different key types in same container."""
        container = DIContainer()

        class ServiceA:
            pass

        class ServiceB:
            pass

        class ServiceC:
            pass

        container.bind('string_key', ServiceA)
        container.bind(42, ServiceB)
        container.bind(('tuple', 'key'), ServiceC)

        self.assertIsInstance(container.resolve('string_key'), ServiceA)
        self.assertIsInstance(container.resolve(42), ServiceB)
        self.assertIsInstance(container.resolve(('tuple', 'key')), ServiceC)

    def test_custom_key_type_hash_collisions(self):
        """Test that different hashable types don't collide."""
        container = DIContainer()

        obj1 = object()
        obj2 = object()

        container.bind(1, obj1)
        container.bind('1', obj2)

        self.assertIs(container.resolve(1), obj1)
        self.assertIs(container.resolve('1'), obj2)

    # ============================================================================
    # MEMORY & REFERENCE TRACKING
    # ============================================================================

    def test_singleton_memory_persistence(self):
        """Verify singleton instances persist in memory (reference tracking)."""
        import gc

        container = DIContainer()

        class MemoryService:
            pass

        container.bind(MemoryService, MemoryService, singleton=True)

        instance = container.resolve(MemoryService)
        instance_id = id(instance)

        # Force garbage collection
        gc.collect()

        # Resolve again and verify same instance
        resolved = container.resolve(MemoryService)
        self.assertEqual(id(resolved), instance_id)

    def test_non_singleton_garbage_collection(self):
        """Verify non-singleton instances can be garbage collected."""
        import gc

        container = DIContainer()

        class ShortLivedService:
            pass

        container.bind(ShortLivedService, ShortLivedService, singleton=False)

        instance = container.resolve(ShortLivedService)
        weak_ref = __import__('weakref').ref(instance)

        # Instance exists
        self.assertIsNotNone(weak_ref())

        # Delete reference
        del instance

        # Force garbage collection
        gc.collect()

        # Instance should be collected
        self.assertIsNone(weak_ref())

    def test_large_dependency_chain_no_memory_leak(self):
        """Test that large chains don't retain unnecessary references."""
        import gc
        import sys

        container = DIContainer()

        # Create chain of 100 classes
        prev_cls = None
        for i in range(100):
            if i == 0:
                cls = type(f'Node{i}', (), {'__init__': lambda self: None})
            else:
                cls = type(
                    f'Node{i}',
                    (),
                    {
                        '__init__': lambda self, p=prev_cls: setattr(self, 'prev', p()),
                        '__annotations__': {'p': prev_cls}
                    }
                )
            container.bind(cls, cls)
            prev_cls = cls

        gc.collect()
        initial_count = len(gc.get_objects())

        # Resolve multiple times
        for _ in range(100):
            container.resolve(prev_cls)

        gc.collect()
        final_count = len(gc.get_objects())

        # Object count shouldn't grow unbounded
        # Allow some growth for internal structures, but not 10x
        growth = final_count - initial_count
        self.assertLess(growth, initial_count / 2)

    def test_circular_dependency_error_doesnt_leak(self):
        """Verify circular dependency exceptions clean up properly."""
        import gc

        container = DIContainer()

        class A:
            def __init__(self, b: 'B'):
                pass

        class B:
            def __init__(self, a: A):
                pass

        container.bind(A, A)
        container.bind(B, B)

        gc.collect()
        initial_objects = len(gc.get_objects())

        # Trigger circular error multiple times
        for _ in range(50):
            try:
                container.resolve(A)
            except StatusCodeException:
                pass

        gc.collect()
        final_objects = len(gc.get_objects())

        # Shouldn't accumulate exception objects excessively
        leak = final_objects - initial_objects
        self.assertLess(leak, initial_objects / 4)

    def test_failed_resolution_cleanup(self):
        """Verify resolution stack is cleaned up even on exception."""
        container = DIContainer()

        class Dep1:
            pass

        class Dep2:
            def __init__(self):
                raise RuntimeError("Intentional failure")

        class Consumer:
            def __init__(self, d1: Dep1, d2: Dep2):
                pass

        container.bind(Dep1, Dep1)
        container.bind(Dep2, Dep2)
        container.bind(Consumer, Consumer)

        # Trigger failure
        try:
            container.resolve(Consumer)
        except RuntimeError:
            pass

        # Resolution stack should be empty, allowing new resolutions
        class NewService:
            pass

        container.bind(NewService, NewService)
        result = container.resolve(NewService)
        self.assertIsInstance(result, NewService)

    # ============================================================================
    # ADVANCED EDGE CASES
    # ============================================================================

    def test_zero_parameter_factory(self):
        """Test factory with no parameters."""
        container = DIContainer()

        def create_value():
            return 42

        container.bind('value', create_value)
        result = container.resolve('value')
        self.assertEqual(result, 42)

    def test_class_with_class_method_constructor(self):
        """Test that classmethod constructors work (if used as provider)."""
        container = DIContainer()

        class Service:
            @classmethod
            def create(cls):
                return cls()

            def __init__(self):
                self.created = True

        # Bind the classmethod as provider
        container.bind('service', Service.create)
        result = container.resolve('service')
        self.assertIsInstance(result, Service)
        self.assertTrue(result.created)

    def test_static_method_as_provider(self):
        """Test static method as provider."""
        container = DIContainer()

        class Factory:
            @staticmethod
            def create_service():
                return "service_instance"

        container.bind('service', Factory.create_service)
        result = container.resolve('service')
        self.assertEqual(result, "service_instance")

    def test_lambda_with_default_args(self):
        """Test lambda with default arguments."""
        container = DIContainer()

        container.bind('lambda', lambda x=10, y=20: x + y)
        result = container.resolve('lambda')
        self.assertEqual(result, 30)

    def test_resolution_with_kwargs_only(self):
        """Test class with **kwargs in constructor."""
        container = DIContainer()

        class FlexibleService:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        container.bind(FlexibleService, FlexibleService)
        result = container.resolve(FlexibleService)
        self.assertIsInstance(result, FlexibleService)
        self.assertEqual(result.kwargs, {})

    def test_resolution_with_args_and_kwargs(self):
        """Test class with *args and **kwargs."""
        container = DIContainer()

        class VarArgsService:
            def __init__(self, x: int = 5, *args, **kwargs):
                self.x = x
                self.args = args
                self.kwargs = kwargs

        container.bind(VarArgsService, VarArgsService)
        result = container.resolve(VarArgsService)
        self.assertEqual(result.x, 5)
        self.assertEqual(result.args, ())
        self.assertEqual(result.kwargs, {})


if __name__ == '__main__':
    unittest.main()