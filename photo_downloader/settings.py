import os

from config import config
from config import config_from_yaml
# from config import config_from_dict

default_path = "../.config/config.yaml"
local_path = "../.config-local/config.yaml"

# cfg = config_from_dict(data)
cfg = config(
    ('yaml', local_path, True),
    ('yaml', default_path, True)
)

print(cfg)
