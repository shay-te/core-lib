---
id: instance_under_stack
title: instance_under_stack
sidebar_label: instance_under_stack
---

`InstanceUnderStack` will keep the same stored instance as long it was requested under the same parent stack frame.

# Available APIs 

```python

class InstanceUnderStack(object):

    def __init__(self, stack_start_index: int = 4):
        ...

    def get_stack_path(self) -> str:
        ...    

    def store(self, obj):
        ...

    def stored(self, obj) -> bool:
        ...

    def get(self) -> object:
        ...

    def remove(self, obj) -> bool:
        ...

```

`get_stack_path` will return the stack frames as a string (`stack path`) with the id of each frame staring from the `stack_start_index` index
for example a `stack path` may be: 
`main:23469104<-#->self.runTests:64489072<-#->self.result=testRunner.run:95433880<-#->returnsuper:64923568<-#->test:89404320<-#->returnself.run:95166512<-#->test:95434632<-#->returnself.run:95166864<-#->test:95435008<-#->returnself.run:95167216<-#->test:95435384<-#->returnself.run:95168272<-#->testMethod:89394544<-#->core_lib.some_object.create:95182896` 

`store` will store an `object` under the current `stack path` 

`stored` return `True` if the current `object` registered  

`get` will return an `object` if the `current stack path` is under registered `stack path`. if no object stored will return `None` 

`remove` will remove stored object. return `True` when object was stored and remove. otherwise return `False`
