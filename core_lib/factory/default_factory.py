from core_lib.factory.factory import Factory


class DefaultFactory(Factory):

    def __init__(self, object_type):
        if not object_type:
            raise ValueError()
        self.object_type = object_type
        self.name_to_object = {}

    def register(self, name: str, object):
        if name in self.name_to_object:
            raise ValueError("cache by name \"{}\" already registerd for type \"{}\"".format(name, object.__class__))

        if not isinstance(object, self.object_type):
            raise ValueError("register object is not of type \"{}\"".format(self.object_type))

        self.name_to_object[name] = object

    def get(self, name: str, *args, **kwargs):
        if name:
            return self.name_to_object.get(name)
        if len(self.name_to_object) > 0:
            return list(self.name_to_object.values())[0]

