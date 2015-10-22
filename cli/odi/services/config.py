import os
import sys


def get_config(key=None):
    """Return config module.

    If key is passed it returns value of key.
    """
    base_path = os.path.join(os.getcwd())
    sys.path.append(base_path)
    import config_default as config
    if key:
        config = getattr(config, key)
    sys.path.remove(base_path)
    return config
