FROM python:3.6

WORKDIR /app

COPY app/requirements /app/requirements
RUN apt-get update && apt-get install -y gettext && pip install --trusted-host pypi.python.org -r requirements/base.txt

COPY .env /
COPY ./app /app

EXPOSE 8000
