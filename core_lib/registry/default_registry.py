from core_lib.registry.registry import Registry


class DefaultRegistry(Registry):

    def __init__(self, object_type: object):
        if not object_type:
            raise ValueError()
        self._object_type = object_type
        self.name_to_object = {}
        self.default_name = None

    def register(self, name: str, object, is_default: bool = False):
        assert name and object
        if not isinstance(object, self._object_type):
            raise ValueError("register object is not of type \"{}\"".format(self._object_type))

        if name in self.name_to_object:
            raise ValueError("cache by name \"{}\" already registerd for type \"{}\"".format(name, object.__class__))

        if is_default:
            self.default_name = name
        self.name_to_object[name] = object

    def unregister(self, name: str):
        if name in self.name_to_object:
            del self.name_to_object[name]
            if self.default_name == name:
                self.default_name = None

    def get(self, name: str = None, *args, **kwargs):
        result = self.name_to_object.get(name or self.default_name)
        if not result and len(self.name_to_object) > 0:
            result = list(self.name_to_object.values())[0]
        return result
