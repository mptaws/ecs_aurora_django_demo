FROM python:3.9-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update --allow-releaseinfo-change \
    && apt-get install -y build-essential default-libmysqlclient-dev \
    && apt-get install -y python-mysqldb git gettext
RUN pip install --upgrade pip
RUN pip install mysql-connector-python

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
COPY entrypoint.sh /code/

RUN pip install --no-cache-dir -r requirements.txt
COPY . /code/

EXPOSE 8000
EXPOSE 3306

RUN ["chmod", "777", "entrypoint.sh"]
ENTRYPOINT ["./entrypoint.sh"]
