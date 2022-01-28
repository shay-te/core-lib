import hydra


@hydra.main(config_path="./hydra_docker-compose.yaml")
def main(cfg):
    target_config_file = None
    if cfg.target_config_file or None:
        target_config_file = cfg.target_config_file
        del cfg['target_config_file']
    if not target_config_file:
        raise ValueError('target config path not specified')

    with open(target_config_file, "w") as file:
        file.write(cfg.pretty())


if __name__ == '__main__':
    main()
