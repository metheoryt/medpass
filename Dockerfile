FROM python:3.7

RUN mkdir -p /opt/app
WORKDIR /opt/app

# copy requirements and install (so that changes to files do not mean rebuild cannot be cached)
COPY Pipfile .
COPY Pipfile.lock .
EXPOSE 8000

RUN pip install --no-cache-dir pipenv && pipenv sync

ENTRYPOINT ["pipenv", "run"]