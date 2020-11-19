from core_lib.factory.default_factory import DefaultRegistry
from core_lib.observer.observer import Observer


class ObserverRegistry(DefaultRegistry):

    def __init__(self):
        DefaultRegistry.__init__(self, Observer)
