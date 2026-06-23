from core_lib.registry.registry import Registry


class DefaultRegistry(Registry):
    def __init__(self, object_type: object):
        """
        Initialize a registry for managing objects of a specific type.
        
        Parameters:
            object_type: The required type for all objects registered in this registry.
                Must be a truthy value (e.g., a class or type object).
        
        Raises:
            ValueError: If object_type is falsy.
        """
        if not object_type:
            raise ValueError()
        self._object_type = object_type
        self.key_to_object = {}
        self.default_key = None

    def register(self, key: str, object, is_default: bool = False):
        # Explicit raises (not `assert`) so `python -O` doesn't strip them.
        """
        Register an object in the registry under the specified key.
        
        If `is_default` is True, sets this as the default object for retrieval.
        
        Raises:
            AssertionError: If `key` or `object` is falsy.
            ValueError: If `object` is not an instance of the required type, or if `key` is already registered.
        """
        if not key:
            raise AssertionError('DefaultRegistry.register requires a truthy `key`')
        if not object:
            raise AssertionError('DefaultRegistry.register requires a truthy `object`')
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
        """
        Retrieve a registered object by key.
        
        If no key is provided, uses the default key. If the default key yields no result and the registry contains entries, returns the first registered object.
        
        Parameters:
            key (str, optional): The registry key to look up.
        
        Returns:
            The registered object, or None if no entry is found.
        """
        result = self.key_to_object.get(key or self.default_key)
        if not key and not result and len(self.key_to_object) > 0:
            # Avoid materializing all values just to read the first one.
            result = next(iter(self.key_to_object.values()))
        return result

    def registered(self):
        """
        Retrieve all currently registered keys.
        
        Returns:
            list: A list of all registered keys.
        """
        return list(self.key_to_object.keys())
