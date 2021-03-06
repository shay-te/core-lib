import inspect


class InstanceUnderStack(object):

    def __init__(self, stack_start_index: int = 4):
        self.object_to_instance_path = {}
        self.stack_start_index = stack_start_index

    def get_stack_path(self) -> str:
        stack = inspect.stack()
        lst = []
        for stack_frame in stack[self.stack_start_index:]:
            line = stack_frame.code_context[0] if stack_frame.code_context else "!NO_CODE_CONTEXT!"
            line = line.replace(" ", "").split("(")[0]
            lst.insert(0, "{}:{}".format(line, id(stack_frame.frame)))
        return "<-#->".join(lst)

    def store(self, obj):
        self.object_to_instance_path[obj] = self.get_stack_path()

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
