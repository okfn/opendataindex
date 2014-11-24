import os
import sys


def get_config():
    base_path = os.path.join(os.getcwd())
    sys.path.append(base_path)
    import config_default
    config = config_default.ODI
    sys.path.remove(base_path)
    return config
