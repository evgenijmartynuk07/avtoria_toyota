# avtoria_toyota


## Installation

Python3 must be already installed

```shell

python -m venv venv
source venv/bin/activate

create .env based on .env.sample

run alembic upgrade head

run python main.py
```

If you have any problem with OS dependency -> Run in Docker container

```shell

python -m venv venv
source venv/bin/activate

create .env based on .env.sample

run: docker-compose up -d
```


