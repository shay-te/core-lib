# Deprecated since 0.3.0, to be removed in 1.0.0: the old name of
# `core_lib.data_layers.data_access.db.crud.crud_soft_delete_data_access`, renamed to match its class.
# Kept until then so existing imports keep working; tests/test_deprecated_aliases.py fails at 1.0.0 if it is still here.
import warnings

from core_lib.data_layers.data_access.db.crud.crud_soft_delete_data_access import CRUDSoftDeleteDataAccess  # noqa: F401

warnings.warn(
    '`core_lib.data_layers.data_access.db.crud.crud_soft_data_access` is deprecated since 0.3.0 and will be removed '
    'in 1.0.0, import `core_lib.data_layers.data_access.db.crud.crud_soft_delete_data_access` instead',
    DeprecationWarning,
    stacklevel=2,
)
