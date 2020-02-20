from abc import abstractmethod, ABC

from core_lib.cache.cache_client_factory import CacheClientFactory


class A(object):

    def foo(self):
        pass


class B(object):

    def foo(self):
        pass


print(A().foo.__qualname__)
print(B().foo.__qualname__)


