from core_lib.factory.registry import Registry


class DefaultRegistry(Registry):

    def __init__(self, object_type: object, error_on_no_result: bool = False):
        if not object_type:
            raise ValueError()
        self._object_type = object_type
        self._error_on_no_result = error_on_no_result
        self.name_to_object = {}

    def register(self, name: str, object):
        if not isinstance(object, self._object_type):
            raise ValueError("register object is not of type \"{}\"".format(self._object_type))

        if name in self.name_to_object:
            raise ValueError("cache by name \"{}\" already registerd for type \"{}\"".format(name, object.__class__))

        self.name_to_object[name] = object

    def get(self, name: str = None, *args, **kwargs):
        result = None
        if name:
            result = self.name_to_object.get(name)
        elif len(self.name_to_object) > 0:
            result = list(self.name_to_object.values())[0]
        if not result and self._error_on_no_result:
            raise ValueError("'{}' by name `{}` was not found in factory".format(self._object_type.__name__, name))
        return result
