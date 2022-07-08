FROM python:3-slim

WORKDIR /usr/src/app

COPY dependency ./
RUN pip install --no-cache-dir -r dependency

COPY ./source ./source

WORKDIR /usr/src/app/source

CMD [ "python", "-u", "./main.py" ]
