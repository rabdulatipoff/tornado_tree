from typing import Optional

from tornado.options import define, options
from tornado_sqlalchemy import SQLAlchemy

import os


# Keep options saved from custom define( wrapper
__options__ = list()


def app_define(*args, **kwargs):
    """tornado.options.define( wrapper.
    Stores defined options for later initialization.
    """
    define(*args, **kwargs)

    option = dict()
    # name is probably a positional argument
    # define( is expected to raise an exception on incorrect input
    if len(args) == 1:
        option['name'] = args[0]
    else:
        option['name'] = kwargs['name']

    for kw in kwargs:
        option[kw] = kwargs[kw]

    __options__.append(option)


class EnvironmentVarNotSet(Exception):
    """Exception raised while parsing config vars from environment."""
    pass


def config_from_env(options):
    """
    Try to set options from environment vars.
    """
    for option in __options__:
        try:
            parsed = os.environ['APP_' + option['name'].upper()]
            # Explicit type casting (for retrieving int values, etc.)
            type_cast = option['type'] if 'type' in option else type(option['default'])
            setattr(options, option['name'], type_cast(parsed))
        except KeyError:
            if 'default' not in option:
                raise EnvironmentVarNotSet(f'{option["name"]} is not provided; APP_{option["name"].upper()} must be set')


def make_url(options) -> str:
    """
    Generate connection URL string from provided options.
    """
    # FIXME: hardcoded driver name (though we require postgresql)
    return f'postgresql://{options.db_username}:{options.db_password}@{options.db_hostname}:{options.db_port}/{options.db_name}'


def db_object(url: str, binds: Optional[dict] = {}):
    """
    Return tornado_sqlalchemy session interface object.
    Used for SA Model class and ThreadPoolExecutor interfaces.
    """
    return SQLAlchemy(url.strip(), **binds)


app_define('db_username', type = str, help = 'DB username')
app_define('db_password', type = str, help = 'DB password')
app_define('db_name', type = str, help = 'DB name')
app_define('db_hostname', type = str, help = 'DB connection hostname', default = 'localhost')
app_define('db_port', type = int, help = 'DB connection port', default = 5432)
app_define('port', type = int, help = 'Application port', default = 3000)


