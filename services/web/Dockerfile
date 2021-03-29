FROM python:3.8

RUN pip3 install pipenv

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

#Installing system dependencies
RUN apt-get update && apt-get install -y netcat



#Installing dependencies
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system --deploy --ignore-pipfile

COPY . /usr/src/app/

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]