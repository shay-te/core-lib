import inspect
import threading
from http import HTTPStatus

from core_lib.error_handling.status_code_exception import StatusCodeException

PRIMITIVE_TYPES = (int, float, str, bool, complex, list, dict, set, tuple, bytes, bytearray, frozenset)

class DIContainer:
    """
    A simple Dependency Injection (DI) container.

    Supports:
        - Binding keys (classes or identifiers) to factories or instances.
        - Singleton management.
        - Automatic constructor injection based on type hints.
        - Circular dependency detection.
        - Thread-local resolution stack for safe concurrent use.
    """

    def __init__(self):
        """
        Initialize the DI container.

        Attributes:
            _bindings (dict): Maps keys to (provider_or_instance, singleton_flag).
            _singletons (dict): Stores instantiated singletons.
            _lock (RLock): Ensures thread-safe access to container data.
            _thread_local (threading.local): Holds per-thread resolving stack for circular dependency detection.
        """
        self._bindings = {}
        self._singletons = {}
        self._resolving = []
        self._lock = threading.RLock()
        self._thread_local = threading.local()

    def bind(self, key, provider, singleton=False):
        """
        Bind a key to a provider or instance.

        Args:
            key: The key to bind (usually a class or identifier).
            provider: A callable (provider) that returns an instance, or an already-created instance.
            singleton (bool): Whether this binding should be treated as a singleton.

        Example:
            container.bind(IService, ServiceImplementation, singleton=True)
        """
        self._bindings[key] = (provider, singleton)

    def resolve(self, key):
        """
        Resolve a key to an instance.

        Automatically instantiates factories, injecting dependencies
        recursively based on constructor type hints. Detects circular dependencies.

        Args:
            key: The key to resolve.

        Returns:
            The resolved instance.

        Raises:
            StatusCodeException: If key not found, circular dependency detected,
                                 or constructor parameter cannot be resolved.
        """
        with self._lock:
            if not hasattr(self._thread_local, "resolving"):
                self._thread_local.resolving = []
            self._resolving = self._thread_local.resolving  # use thread-local resolving stack

            # LOGIC
            if key not in self._bindings:
                raise StatusCodeException(HTTPStatus.NOT_FOUND, f'No binding found for "{key}"')

            if key in self._singletons:
                return self._singletons[key]

            if key in self._resolving:
                path = " -> ".join(
                    [f'"{getattr(k, "__name__", str(k))}"' for k in self._resolving] +
                    [f'"{getattr(key, "__name__", str(key))}"']
                )
                raise StatusCodeException(HTTPStatus.INTERNAL_SERVER_ERROR, f'Circular dependency detected along the chain: {path}')

            self._resolving.append(key)
            provider, singleton = self._bindings.get(key)

            if isinstance(provider, type):
                if provider in PRIMITIVE_TYPES:
                    instance = provider()
                else:
                    instance = self._create_provider_instance(provider)
            elif callable(provider):
                instance = self._create_provider_instance(provider)
            else:
                instance = provider

            self._resolving.pop()

            if singleton:
                self._singletons[key] = instance
            return instance

    # WRITE TESTS FOR THIS FUNCTION
    def __getattr__(self, name):
        """Allow attribute-style access to bindings by key."""
        if name in self._bindings:
            return self.resolve(name)
        raise AttributeError(f"'DIContainer' object has no attribute '{name}'")

    def _create_provider_instance(self, provider):
        # Inspect constructor parameters
        sig = inspect.signature(provider)
        kwargs = {}
        for name, param in sig.parameters.items():
            if param.annotation is inspect.Parameter.empty:
                # No type hint; use default value if exists, else raise
                if param.default is not inspect.Parameter.empty:
                    kwargs[name] = param.default
                else:
                    raise StatusCodeException(
                        HTTPStatus.INTERNAL_SERVER_ERROR,
                        f'Cannot resolve dependency for parameter "{name}" in {provider}. '
                        'No type hint or default value provided.'
                    )
            else:
                kwargs[name] = self.resolve(param.annotation)
        instance = provider(**kwargs)
        return instance