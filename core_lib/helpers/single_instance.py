#
# Extend this class to make sure only single instance of your class is allowed
#


class SingleInstance(object):

    _instances = {}

    def __new__(cls, *args, **kwargs):
        cls_str = str(cls)
        if cls_str in SingleInstance._instances:
            raise RuntimeError('only single instance of class [{}] is allowed'.format(cls_str))

        instance = super(SingleInstance, cls).__new__(cls)
        SingleInstance._instances[cls_str] = instance
        return instance
