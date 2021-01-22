import os

from config import *
# from config import config
# from config import ConfigurationSet
# from config import config_from_env
# from config import config_from_yaml
# from config import config_from_dict

default_path = "../.config/config.yaml"
local_path = "../.config-local/config.yaml"

cfg = ConfigurationSet(
    config_from_env("FPD", "__", lowercase_keys=True),
    config_from_yaml(local_path, read_from_file=True),
    config_from_yaml(default_path, read_from_file=True)
)

print(cfg)