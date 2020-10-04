import inspect
import threading


class InstanceUnderStack(object):

    def __init__(self, stack_start_index: int = 4):
        self.object_to_instance_path = {}
        self.stack_start_index = stack_start_index

    def get_stack_path(self) -> str:
        stack = inspect.stack(0)
        lst = []
        for stack_frame in stack[self.stack_start_index:]:
            lst.insert(0, str(id(stack_frame.frame)))
        stack_path = '<-#->'.join(lst)

        return 'thread:{},path:{}'.format(threading.get_native_id(), stack_path)

    def store(self, obj):
        stack_path = self.get_stack_path()
        self.object_to_instance_path[obj] = stack_path
        return stack_path

    def stored(self, obj) -> bool:
        return True if obj in self.object_to_instance_path else False

    def get(self) -> object:
        current_session_path = self.get_stack_path()
        for object, path in self.object_to_instance_path.items():
            if len(current_session_path) > len(path) and current_session_path.startswith(path):
                return object

    def remove(self, obj) -> bool:
        if obj in self.object_to_instance_path:
            del self.object_to_instance_path[obj]
            return True
        return False
