FROM python:3.9

ENV PYTHONPATH=/app
WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./ /app

CMD gunicorn -k uvicorn.workers.UvicornWorker -c gunicorn_conf.py main:app