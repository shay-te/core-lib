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
