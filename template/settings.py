NAME = "{{name}}"
DEBUG = False
SECRET_KEY = "{{secret_key}}"             # Keep secret!
REDIS = (1, 'localhost', 6379)            # Databsase, Host, Port

try:
    from settings_local.py import *
except ImportError:
    pass
