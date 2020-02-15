FROM python:3.8-slim-buster

RUN apt-get -q update && apt-get -qy install netcat postgresql-client

COPY tornado_tree/requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . .
RUN pip install .

RUN chmod +x ./entrypoint.sh
CMD [ "./entrypoint.sh" ]
