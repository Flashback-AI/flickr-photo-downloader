"""settings.py"""
import os

from config import ConfigurationSet, config_from_env, config_from_yaml

DEFAULT_PATH = "../.config/config.yaml"
LOCAL_PATH = "../.config-local/config.yaml"


def fix_path(file_path):
    """fixes a path so project files can be located via a relative path"""
    script_path = os.path.dirname(__file__)
    return os.path.normpath(os.path.join(script_path, file_path))


def get_config():
    """returns the computed deep merge of configurations, from env, yaml"""
    cfg = ConfigurationSet(
        config_from_yaml(fix_path(DEFAULT_PATH), read_from_file=True)
    )

    # the local config file is optional
    local_path = fix_path(LOCAL_PATH)
    if os.path.exists(local_path):
        cfg.update(config_from_yaml(local_path, read_from_file=True))

    cfg.update(config_from_env("FPD", "__", lowercase_keys=True))

    print(cfg)
    return cfg
