"""Deprecated: `RequireLogin` moved to `core_lib.web_helpers.require_login`, one decorator for every framework."""
import warnings

from core_lib.web_helpers.require_login import RequireLogin

__all__ = ['RequireLogin']

warnings.warn(
    '`core_lib.web_helpers.flask.require_login` is deprecated: '
    'import RequireLogin from `core_lib.web_helpers.require_login`',
    DeprecationWarning,
    stacklevel=2,
)
