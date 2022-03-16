import hydra

from core_lib.data_transform.result_to_dict import result_to_dict
from my_core_lib.my_core_lib.my_core_lib import MyCoreLib

config_file = 'config.yaml'
hydra.core.global_hydra.GlobalHydra.instance().clear()
hydra.initialize(config_path='my_core_lib/config')
config = hydra.compose(config_file)
print(config)
core_lib = MyCoreLib(config)

print(result_to_dict(core_lib.user.create({'username': 'afsfaf', 'password': 'afafadfdafa'})))
print(result_to_dict(core_lib.user.get(1)))
print(result_to_dict(core_lib.user.delete(1)))
print(result_to_dict(core_lib.user.get(1)))
