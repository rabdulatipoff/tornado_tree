# tornado_tree
A microservice application written in Python with Tornado and SQLAlchemy, which implements an asynchronous REST API for adding and retrieving values from the tree-like data structure.

- Nodes have non-unique names, optional text data
- Each node has exactly one parent
- Each node can have unlimited number of children nodes
- A node GET request returns its name, data, number of ancestors and list of their IDs
- A node POST request returns the created node's data, along with number of ancestors and their IDs.

## [API endpoints](#api)
| Route | Method | Type | Description |
| ----- | ------ | ---- | ----------- |
| / | GET | Text |Get the whole tree (for testing purposes) |
| /api/v1/get/{id} | GET | JSON | Get a single node data |
| /api/v1/add | POST | JSON | Add a node on the tree. 'name' parameter is required. A request without a 'parent' ID provided will fail if the tree is not empty. |

## [Installation](#install)
Attention: this package is not indexed on PyPI, use the included `setup.py` in order to build and install it. Using a separate virtualenv is advised. For manual installation, get the dependencies and install the package using `setup.py`:

```sh
$ cd tornado_tree
$ pip install -r requirements.txt
$ pip install ..
```

*tornado_tree* makes use of PostgreSQL (9.5+) and psycopg2 as a DB adapter. If you install it manually, you'd have to create the application's DB with PGSQL extension 'ltree' - instead of tampering with 'template1', **entrypoint.sh** only creates the extension on the database specified by `APP_DB_NAME` env variable. Please ensure that you have appropriate versions installed, along with *postgresql-client* if you use `psql`. Assuming local PGSQL installation and that `sudo` works on your system:

```sh
# User postgres must have password set

$ sudo -u postgres psql -c "CREATE DATABASE $APP_DB_NAME;"
$ sudo -u postgres psql $APP_DB_NAME -c "CREATE EXTENSION IF NOT EXISTS LTREE;"
```

Alternatively, you can [deploy](#docker) with docker-compose, which will handle this automatically.
After you've set up the database, you may proceed with schema migrations and running the app. 

## Migrations and running the app 

### [Environment variables](#envs)
These variables are provided by the `.env` script, adjust these settings in the file if necessary before running migrations and launching the app:

| Name | Default | Description |
| ---- | ------- | -------- |
| `APP_DB_USERNAME` | 'treeuser' | DB account's username. |
| `APP_DB_PASSWORD` | 'tree123' | DB account's password. |
| `APP_DB_NAME` | 'treedb' | Name of app's database. |
| `APP_DB_HOSTNAME` | 'localhost' | DB server hostname, used for app instances outside a container. |
| `APP_DB_PORT` | 5432 | DB server port, exposed in docker-compose configuration. |
| `APP_PORT` | 3000 | DB server port, exposed in docker-compose configuration. |
| `MIGRATE` | 1 | Run migrations before starting the app. |
| `DEBUG` | 1 | Enable debug mode (pretty logging). |

In order to apply migrations and run the application, you must first set certain [environment variables](#envs) to provide the application settings. You can source the `.env` file to do so:

```sh
$ . ../.env
```

### [Migrations](#migrations)
*tornado_tree* uses Alembic to detect major DB schema changes and generate migration scripts. If you're using a separate virtualenv, it should be available on your path at this point. In order to apply the latest migrations, execute:

```sh
$ alembic upgrade head
```

### [Running](#running)
After you have installed the required packages and successfully ran DB migrations, you should be able to run the service:

```sh
$ python entry.py
```

Make sure that the service is working:

```sh
$ curl localhost:$APP_PORT
{"error": "The tree is empty yet"}
```

## [Docker deployment](#docker)
The default docker-compose configuration is intended for development use. Please refer to [Environment variables](#envs) section for additional information.
You can also provide custom settings in docker-compose.yml or pass them with `-e` key when calling `docker-compose run`. Remember that `docker-compose run` overrides the entrypoint command defined in the app configuration.

Building images and deploying is easy:

```sh
$ docker-compose up
```
