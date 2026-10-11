from core_lib.core_lib import CoreLib
from core_lib.helpers.string import camel_to_snake

SERVICE_SUFFIX = 'Service'


def service_attribute_name(service_class_name: str) -> str:
    # The generated CoreLib's public name for a service: the class name minus `Service`, in snake_case
    # (WidgetService -> widget). A name the CoreLib already uses (`config`, `load_jobs`, ...) keeps the full
    # snake_case class name instead, so the service never hides it.
    full_name = camel_to_snake(service_class_name)
    if not service_class_name.endswith(SERVICE_SUFFIX) or service_class_name == SERVICE_SUFFIX:
        return full_name
    short_name = camel_to_snake(service_class_name[:-len(SERVICE_SUFFIX)])
    if short_name == 'config' or hasattr(CoreLib, short_name):
        return full_name
    return short_name


def data_access_attribute_name(data_access_class_name: str) -> str:
    # Private: a host or a test reaches a DataAccess only through its service.
    return f'_{camel_to_snake(data_access_class_name)}'
