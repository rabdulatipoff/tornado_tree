# tornado_tree
A microservice application written in Python with Tornado and SQLAlchemy, which implements an asynchronous REST API for adding and retrieving values from the tree-like data structure.

- Nodes have non-unique names, optional text data
- Each node has exactly one parent
- Each node can have unlimited number of children nodes
- A node GET request returns its name, data, number of ancestors and list of their IDs
- A node POST request returns the created node's data, along with number of ancestors and their IDs.

### API endpoints
| Route | Method | Type | Description |
| ----- | ------ | ---- | ----------- |
| / | GET | Text |Get the whole tree (for testing purposes) |
| /api/v1/get/{id} | GET | JSON | Get a single node data |
| /api/v1/add | POST | JSON | Add a node on the tree. 'name' parameter is required. A request without a 'parent' ID provided will fail if the tree is not empty. |

### Installation
Attention: this package is not indexed on PyPI, use the included setup.py in order to build and install it. Using a separate virtualenv is advised. For manual installation, get the dependencies and install the package using setup.py:

```sh
$ cd tornado_tree
$ pip install -r requirements.txt
$ pip install ..
```

*tornado_tree* makes use of PostgreSQL (9.5+) and psycopg2 as a DB adapter. If you install it manually, you'd have to create the application's DB with PGSQL extension 'ltree' - instead of tampering with 'template1', **entrypoint.sh** only creates the extension on the database specified by `APP_DB_NAME` env var. Please ensure that you have appropriate versions installed, along with *postgresql-client* if you use `psql`. Assuming local PGSQL installation and that `sudo` works on your system:

```sh
# User postgres must have password set

$ sudo -u postgres psql -c "CREATE DATABASE $APP_DB_NAME;"
$ sudo -u postgres psql $APP_DB_NAME -c "CREATE EXTENSION IF NOT EXISTS LTREE;"
```

Alternatively, you may use the provided *docker-compose* configuration for automated deployment. After you've set up the database, you may proceed with schema migrations and running the app. 

### Migrations and running
*tornado_tree* uses Alembic to detect major DB schema changesand generate migration scripts. If you're using a separate virtualenv, it should be available on your path at this point. In order to apply the latest migrations, execute:

```sh
$ alembic upgrade head
```

Running and migrating requires certain env variables to be set. See the `tree_envvars` script to adjust them if necessary and then source it:

```sh
$ . ../tree_envvars
```

Now you should be able to run the application:

```sh
$ python entry.py
```

### Docker deployment
The default docker-compose configuration is intended for development use. Certain env vars are passed to the service:

| Name | Default | Function |
| ---- | ------- | -------- |
| MIGRATE | 1 | Run migrations before starting the app |
| DEBUG | 1 | Enable debug mode (pretty logging) |

You can edit those in docker-compose.yml or pass them with `-e` key when calling `docker-compose run`. Remember that `docker-compose run` overrides the entrypoint command defined in the app configuration.

Building images and deploying is easy:

```sh
$ docker-compose up
```

Make sure the app is running:

```sh
$ curl localhost:$APP_PORT
{"error": "The tree is empty yet"}
```
