import hydra

hydra.core.global_hydra.GlobalHydra.instance().clear()
hydra.initialize()
config = hydra.compose('TemplateCoreLib.yaml')


entities = list(config.TemplateCoreLib.env.keys())
core_lib_name = next(iter(config))
core_lib_config = config[core_lib_name].config
core_lib_data_access = 
print(core_lib_config)
