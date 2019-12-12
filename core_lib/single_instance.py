class SingleInstance(object):

    _instances = {}

    def __new__(cls, *args, **kwargs):
        cls_str = str(cls)
        if cls_str in SingleInstance._instances:
            raise RuntimeError('only single instance of class [{}] is allowed'.format(cls_str))
        SingleInstance._instances[cls_str] = True
        return super(SingleInstance, cls).__new__(cls)
