# Deprecated since 0.3.0, to be removed in 1.0.0: the misspelled old name of
# `core_lib.web_helpers.web_helpers_utils`, kept until then so existing imports keep working.
# tests/test_web_helpers_utils_alias.py fails once the version reaches 1.0.0 and this file still exists.
import warnings

from core_lib.web_helpers.web_helpers_utils import WebHelpersUtils  # noqa: F401 - the same class, so init() is shared

warnings.warn(
    '`core_lib.web_helpers.web_helprs_utils` is deprecated since 0.3.0 and will be removed in 1.0.0, '
    'import `core_lib.web_helpers.web_helpers_utils` instead',
    DeprecationWarning,
    stacklevel=2,
)
