FROM --platform=linux/amd64 python:3.11-slim-buster

WORKDIR /app

COPY ./requirements.txt /app/

RUN pip install --no-cache-dir -r  requirements.txt uvicorn

COPY . /app/

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]