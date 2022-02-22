from core_lib.registry.registry import Registry


class DefaultRegistry(Registry):
    def __init__(self, object_type: object):
        if not object_type:
            raise ValueError()
        self._object_type = object_type
        self.key_to_object = {}
        self.default_key = None

    def register(self, key: str, object, is_default: bool = False):
        assert key and object
        if not isinstance(object, self._object_type):
            raise ValueError("register object is not of type \"{}\"".format(self._object_type))

        if key in self.key_to_object:
            raise ValueError("cache by key \"{}\" already registerd for type \"{}\"".format(key, object.__class__))

        if is_default:
            self.default_key = key
        self.key_to_object[key] = object

    def unregister(self, key: str):
        if key in self.key_to_object:
            del self.key_to_object[key]
            if self.default_key == key:
                self.default_key = None

    def get(self, key: str = None, *args, **kwargs):
        result = self.key_to_object.get(key or self.default_key)
        if not key and not result and len(self.key_to_object) > 0:
            result = list(self.key_to_object.values())[0]
        return result

    def registered(self):
        return list(self.key_to_object.keys())
