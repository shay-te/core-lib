import keyword

from core_lib.core_lib import CoreLib
from core_lib.helpers.string import camel_to_snake

SERVICE_SUFFIX = 'Service'


def _is_usable_name(name: str) -> bool:
    return name.isidentifier() and not keyword.iskeyword(name)


def _is_usable_attribute(name: str) -> bool:
    return _is_usable_name(name) and name != 'config' and not hasattr(CoreLib, name)


def service_attribute_name(service_class_name: str) -> str:
    # The generated CoreLib's public name for a service: the class name minus `Service`, in snake_case
    # (WidgetService -> widget). `self.<name> = ...` must compile and must not hide what the CoreLib already has, so
    # a keyword (`import`), an empty name (a class called `Service`) or a name in use (`config`, `load_jobs`) falls
    # back to the full snake_case class name, and if that fails the same way, to `service_<full name>`.
    full_name = camel_to_snake(service_class_name)
    short_name = camel_to_snake(service_class_name.removesuffix(SERVICE_SUFFIX))
    for name in (short_name, full_name):
        if _is_usable_attribute(name):
            return name
    return f'service_{full_name}'


def service_module_name(service_class_name: str) -> str:
    # `import.py` can be written to disk, but no `import` statement can name it.
    module_name = camel_to_snake(service_class_name)
    return module_name if _is_usable_name(module_name) else f'service_{module_name}'


def data_access_attribute_name(data_access_class_name: str) -> str:
    # Private: a host or a test reaches a DataAccess only through its service.
    return f'_{camel_to_snake(data_access_class_name)}'
