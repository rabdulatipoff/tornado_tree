from typing import Optional
from tornado.options import define, options
from tornado_sqlalchemy import SQLAlchemy

define('db_username', type = str, help = 'DB username') # os.environ['TDB_USERNAME']
define('db_password', type = str, help = 'DB password') # os.environ['TDB_PASSWORD']
define('db_name', type = str, help = 'DB name') # os.environ['TDB_DBNAME']
define('db_hostname', type = str, help = 'DB connection hostname', default = 'localhost') # os.environ['TDB_HOSTNAME']
define('db_port', type = int, help = 'DB connection port', default = 5432) # os.environ['TDB_PORT']
define('port', type = int, help = 'Application port', default = 3000) # os.environ['APP_PORT']


def make_url(options) -> str:
    """
    Generate connection URL from provided options
    """
    # FIXME: hardcoded driver name (though we require postgresql)
    return 'postgresql://{db_username}:{db_password}@{db_hostname}:{db_port}/{db_name}'.format(
            db_username = options.db_username,
            db_password = options.db_password,
            db_hostname = options.db_hostname,
            db_port = options.db_port,
            db_name = options.db_name)


def db_object(url: str, binds: Optional[dict] = {}):
    return SQLAlchemy(url.strip(), **binds)


