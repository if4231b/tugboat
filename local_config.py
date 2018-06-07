import logging
LOG_LEVEL = 30 # To be deprecated when all microservices use ADSFlask
LOGGING_LEVEL = "INFO"

ADS_DEBUG = ""
TEST = ""
ENVIRONMENT = ""
API_DEV_KEY = ""
VAULT_QUERY_URL = ""
BUMBLEBEE_URL = ""

GUNICORN_WORKERS = ""
GUNICORN_WORKER_CLASS = ""
GUNICORN_TIMEOUT = ""
GUNICORN_WORKER_CONNECTIONS = ""
GUNICORN_MAX_REQUESTS = ""
GUNICORN_MAX_REQUESTS_JITTER = ""

SQLALCHEMY_ECHO = ""
SQLALCHEMY_POOL_SIZE = ""
SQLALCHEMY_MAX_OVERFLOW = ""
SQLALCHEMY_POOL_TIMEOUT = ""
SQLALCHEMY_TRACK_MODIFICATIONS = ""
SQLALCHEMY_RECORD_QUERIES = ""

# added by eb-deploy (over-write config values) from environment
try:
    import os, json, ast
    G = globals()
    for k, v in os.environ.items():
        if k == k.upper() and k in G:
            logging.info("Overwriting constant '%s' old value '%s' with new value '%s'", k, G[k], v)
            try:
                w = json.loads(v)
                G[k] = w
            except:
                try:
                    # Interpret numbers, booleans, etc...
                    G[k] = ast.literal_eval(v)
                except:
                    # String
                    G[k] = v
except:
    pass
