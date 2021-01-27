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
        config_from_env("FPD", "__", lowercase_keys=True),
        config_from_yaml(fix_path(LOCAL_PATH), read_from_file=True),
        config_from_yaml(fix_path(DEFAULT_PATH), read_from_file=True)
    )

    print(cfg)
    return cfg
