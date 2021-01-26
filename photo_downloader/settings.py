import os

from config import ConfigurationSet, config_from_env, config_from_yaml


default_path = "../.config/config.yaml"
local_path = "../.config-local/config.yaml"


def fix_path(file_path):
    script_path = os.path.dirname(__file__)
    return os.path.normpath(os.path.join(script_path, file_path))


def get_config():
    cfg = ConfigurationSet(
        config_from_env("FPD", "__", lowercase_keys=True),
        config_from_yaml(fix_path(local_path), read_from_file=True),
        config_from_yaml(fix_path(default_path), read_from_file=True)
    )

    print(cfg)
    return cfg
