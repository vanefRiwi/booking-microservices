initialize project step by step with
``` bash
mkdir booking
``` 
Then
``` bash
cd booking
``` 
then initialize every microservice
### 1.
``` bash
uv init user-service
```
### 2.
``` bash
uv init resources-service
```
### 3.
``` bash
uv init payments-service
```
### 4.
``` bash
uv init notifications-service
```
### 5.
``` bash
uv init booking-service
```
Now let's start with one of them to set up our microservices, for example
cd user-service

on this we'll start the installation process of the tool we are going to need, first fastapi , then sqlmodel for our orm and alembic for migrations

``` bash
 uv add "fastapi[standard]"
```
``` bash
 uv add sqlmodel
```
``` bash
 uv add alembic
```

en el toml se van a ver todas las dependencias instaladas

Ahora vamos a inicializar alembic con este comando 

```bash
uv run alembic init alembic
```
abro alembic y edito el .env y ahí edito el .env
en esta parte para que tome el DATABASE_URL
```python
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
```

Ahora me dirigo a la carpeta de versions donde esteb el archivo script.py.mako el cual vamos a editar con esto:

en esta parte añado `import sqlmodel`

``` python
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
${imports if imports else ""}
```

siguiente paso es ir a alembic.ini para comentar una linea `sqlalchemy.url = driver://user:pass@localhost/dbname`
esta: 
```python
# database URL.  This is consumed by the user-maintained env.py script only.
# other means of configuring database URLs may be customized within the env.py
# file.
#sqlalchemy.url = driver://user:pass@localhost/dbname
```

Ahora se crean las carpetas de las buenas practicas: `app` y dentro de app crear folder `src` y dentro (`application`,`domain`,`infrastructure` y `presentation`)

dentro `/domain` folder crear otra carpeta que se llame `/models` y dentro del folder models crear un archivo que se llame`user_model.py`

en el file `user_model.py` vamos a crear el moder de user.

ejemplo:

```python
from sqlmodel import Field, SQLModel
import datetime
import uuid

class User(SQLModel, table=True):  
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(index=True)
    email: str = Field(index=True)
    identification_type: str
    identification_number: str
    birth_date: datetime.date
    is_active: bool = True
    is_superuser: bool = False

    __tablename__ = "usr_users"
```
Luego me voy a la carpeta de alembic y busco el archivo `.env` esto para editar e importar el modelo, importar sqlmodel y editar target_metadata

```python
from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from sqlmodel import SQLModel

#import the models to ensure they are registered with SQLAlchemy's metadata
from app.src.domain.models.user_model import User



# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata


```

al final antes de crear la primera migración colocar el link del en el archivo `.env` en `DATABASE_URL` en neon conexión directa con session pooling

```python
DATABASE_URL="url_ de_tu_base_de_datos"
```
antes de la primera migración ocurrieron cosas por ejemplo el toml tiene que estar así
```
[project]
name = "user-service"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
authors = [
    { name = "vreniz", email = "vreniz@uninorte.edu.co" }
]
requires-python = ">=3.12"
dependencies = [
    "alembic>=1.20.0",
    "fastapi[standard]>=0.156.8",
    "psycopg>=3.3.6",
    "psycopg-binary>=3.3.6",
    "python-dotenv>=1.2.4",
    "sqlmodel>=0.0.48",
]

[project.scripts]
user-service = "user_service:main"

[build-system]
requires = ["uv_build>=0.12.17,<0.13.0"]
build-backend = "uv_build"
```
y el .toml debe verse así:

```python
[project]
name = "user-service"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
authors = [
    { name = "vreniz", email = "vreniz@uninorte.edu.co" }
]
requires-python = ">=3.12"
dependencies = [
    "alembic>=1.20.0",
    "fastapi[standard]>=0.156.8",
    "psycopg>=3.3.6",
    "psycopg-binary>=3.3.6",
    "python-dotenv>=1.2.4",
    "sqlmodel>=0.0.48",
]

[project.scripts]
user-service = "user_service:main"

[build-system]
requires = ["uv_build>=0.12.17,<0.13.0"]
build-backend = "uv_build"
```
también asegurarse de cambiar en el alembic.ini esta linea que hay que descomentar

```python
sqlalchemy.url = "postgresql://neondb_owner:npg_xlB21mKgVdbh@ep-dawn-queen-b59hwwxy-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
```

ahora se hace la primera migracción así
```bash
alembic revision --autogenarate -m "First migration"
```
si no funciona y me sale el error de no module name psycopg2-binary, lo instalo

```bash
uv add psycopg2-binary
```
if that doesnt work use this on your .toml by hand
"psycopg>=3.3.6" then install this

"uv add psycopg_binary"

then once you have all of this try to do your first migration again

```bash
uv run alembic revision --autogenarate -m "First migration"
```
then once that is done do this

```bash
uv run alembic upgrade head
```
then check that the migration and table is created on your database in my case using neon, check my database to find that the migration and new table structure is there


on the other day i had to edit the pyproject.toml para solucionar el problema que tenia por haber borrado el __init__.py así

```python
[project]
name = "user-service"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
authors = [
    { name = "vreniz", email = "vreniz@uninorte.edu.co" }
]
requires-python = ">=3.12"
dependencies = [
    "alembic>=1.20.0",
    "fastapi[standard]>=0.156.8",
    "psycopg>=3.3.6",
    "psycopg-binary>=3.3.6",
    "python-dotenv>=1.2.4",
    "sqlmodel>=0.0.48",
]
[tool.uv]
package = false

```

Luego agregue el __init__.py dentro de `/src` y otro dentro de `/app`

Luego de lo anterior cree la migracion con el `uv run revision --autogenerate -m "migration"` y luego el `uv run alembic upgrade head` y ya funciona okay
