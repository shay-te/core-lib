# TemplateCoreLib
TemplateCoreLib is built using [Core-Lib](https://github.com/shay-te/core-lib).

## Example

Run from this folder:

```python
import hydra

from template_core_lib.template_core_lib import TemplateCoreLib

# Build TemplateCoreLib from its YAML with Hydra's compose API (https://hydra.cc/docs/advanced/compose_api/)
with hydra.initialize(config_path='template_core_lib/config', version_base=None):
    template_core_lib = TemplateCoreLib(hydra.compose('template_core_lib.yaml'))

# function_call
```
