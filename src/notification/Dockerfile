FROM --platform=linux/amd64 python:3.11-slim-buster

WORKDIR /app

COPY ./requirements.txt /app/

RUN pip install --no-cache-dir -r  requirements.txt

CMD [ "python", "main.py" ]