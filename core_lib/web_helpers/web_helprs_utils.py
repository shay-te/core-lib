# Deprecated: the misspelled old name of `core_lib.web_helpers.web_helpers_utils`, kept so existing
# imports keep working. Remove it in the next major version.
#
# It replaces itself with the real module, so both names are one module object: WebHelpersUtils keeps
# its server type on the class, and `init()` through either name must set the one the helpers read.
import sys
import warnings

from core_lib.web_helpers import web_helpers_utils

warnings.warn(
    '`core_lib.web_helpers.web_helprs_utils` is deprecated, '
    'import `core_lib.web_helpers.web_helpers_utils` instead',
    DeprecationWarning,
    stacklevel=2,
)
sys.modules[__name__] = web_helpers_utils
