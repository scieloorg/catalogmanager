FROM python:3.6
ENV PYTHONUNBUFFERED 1

COPY . /app/

RUN pip --no-cache-dir install -r /app/requirements.txt

USER nobody
EXPOSE 6543

CMD gunicorn --paste /app/production.ini
