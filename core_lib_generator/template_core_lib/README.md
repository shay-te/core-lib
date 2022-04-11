[![PyPI](https://img.shields.io/pypi/v/core-lib)](https://pypi.org/project/core-lib/)
![PyPI - License](https://img.shields.io/pypi/l/core-lib)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/core-lib)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/core-lib.svg)](https://pypistats.org/packages/core-lib)

# TemplateCoreLib
TemplateCoreLib is built using [Core-Lib](https://github.com/shay-te/core-lib).

## Example

```python
import hydra
from template_core_lib import TemplateCoreLib

hydra.core.global_hydra.GlobalHydra.instance().clear()
hydra.initialize(config_path='../../template_core_lib/config')

# Create a new TemplateCoreLib using hydra (https://hydra.cc/docs/next/advanced/compose_api/) config
template_core_lib = TemplateCoreLib(hydra.compose('template_core_lib.yaml'))
# function_call
```

## License
Core-Lib in licenced under [MIT](https://github.com/shacoshe/core-lib/blob/master/LICENSE)
