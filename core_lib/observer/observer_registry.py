from core_lib.observer.observer import Observer
from core_lib.registry.default_registry import DefaultRegistry


class ObserverRegistry(DefaultRegistry):

    def __init__(self):
        DefaultRegistry.__init__(self, Observer)
