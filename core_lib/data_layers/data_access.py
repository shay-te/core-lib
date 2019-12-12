from core_lib.single_instance import SingleInstance


class DataAccess(SingleInstance):

    __instances = []

    def __new__(cls, *args, **kwargs):
        instance = super(SingleInstance, cls).__new__(cls)
        DataAccess.__instances.append(instance)
        return instance

