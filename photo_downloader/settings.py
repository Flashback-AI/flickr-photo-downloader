import os

from config import config_from_yaml
from config import config_from_dict

path = "../.config/config.yaml"

cfg = config_from_yaml(path)

print(cfg)
