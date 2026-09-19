# MP3 Converter

A microservice-based system that converts uploaded video files to MP3 audio. Clients upload a video through an API gateway, conversion is performed asynchronously by a worker service, and the user is notified by email when the audio file is ready for download.

The services communicate through Apache Kafka, store media in MongoDB GridFS, and manage user accounts in PostgreSQL. Each service ships with a Dockerfile and Kubernetes manifests.

## Table of Contents

- [Architecture](#architecture)
- [Services](#services)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Running Locally](#running-locally)
- [Deploying to Kubernetes](#deploying-to-kubernetes)
- [API Reference](#api-reference)
- [Known Limitations](#known-limitations)
- [License](#license)

## Architecture

```
                   +-------------+        +--------------+
   Client -------> |   Gateway   | -----> | Auth Service | ----> PostgreSQL
                   |  (FastAPI)  |        |  (FastAPI)   |
                   +-------------+        +--------------+
                      |       ^
          store video |       | stream MP3
                      v       |
                 +-------------------+
                 |  MongoDB (GridFS) |
                 +-------------------+
                      |       ^
                      |       | store MP3
    video_topic       v       |
   Gateway ------> Kafka ---> Converter ---> Kafka ---> Notification ---> SMTP (email)
                                            mp3_topic
```

A conversion request proceeds as follows:

1. The client authenticates with the gateway and receives a JSON Web Token (JWT) issued by the auth service.
2. The client uploads a video to the gateway. The gateway validates the token, stores the video in the `video_database` GridFS bucket, and publishes an event to the `video_topic` Kafka topic.
3. The converter service consumes the event, extracts the audio track, stores the resulting MP3 in the `mp3_db` GridFS bucket, and publishes an event to the `mp3_topic` Kafka topic.
4. The notification service consumes the event and emails the user a download link.
5. The client downloads the MP3 from the gateway.

## Services

| Service        | Path                | Type              | Port | Description                                                        |
| -------------- | ------------------- | ----------------- | ---- | ------------------------------------------------------------------ |
| Auth           | `src/auth`          | HTTP API          | 8000 | User registration, credential validation, and JWT issuance.        |
| Gateway        | `src/gateway`       | HTTP API          | 8001 | Public entry point for login, upload, and download.                |
| Converter      | `src/converter`     | Kafka consumer    | n/a  | Consumes `video_topic`, converts video to MP3, produces `mp3_topic`. |
| Notification   | `src/notification`  | Kafka consumer    | n/a  | Consumes `mp3_topic` and sends the download link by email.         |

## Technology Stack

- Python 3.11
- FastAPI and Uvicorn
- SQLAlchemy with PostgreSQL
- MongoDB with GridFS (via PyMongo)
- Apache Kafka (via `confluent-kafka`), configured for SASL_SSL, such as Confluent Cloud
- MoviePy (requires FFmpeg) for audio extraction
- python-jose for JWT handling
- Docker and Kubernetes

## Repository Structure

```
.
├── docker-compose.yml        # Local PostgreSQL instance for the auth service
├── requirements.txt
└── src
    ├── auth                  # Authentication service
    │   └── k8s               # Deployment and Service manifests
    ├── converter             # Video-to-MP3 worker
    │   ├── consumer
    │   ├── convert
    │   ├── producer
    │   └── k8s
    ├── gateway               # Public API gateway
    │   ├── auth_svc          # Client for the auth service
    │   ├── utils             # Upload, download, and Kafka producer helpers
    │   └── k8s               # Deployment, Service, Ingress, and ConfigMap manifests
    └── notification          # Email notification worker
        └── k8s
```

## Prerequisites

- Python 3.11 or later
- FFmpeg, available on the system `PATH`
- Docker and Docker Compose
- A MongoDB instance
- A Kafka cluster that accepts SASL_SSL connections with the PLAIN mechanism, with the topics `video_topic` and `mp3_topic` created
- A Gmail account with an app password, for sending notifications
- A Kubernetes cluster and `kubectl`, for cluster deployment only

## Configuration

Each service reads its configuration from environment variables. For local development, copy the provided template in each service directory and populate the values:

```bash
cp src/auth/.env.example src/auth/.env
cp src/gateway/.env.example src/gateway/.env
cp src/converter/.env.example src/converter/.env
cp src/notification/.env.example src/notification/.env
```

### Auth

| Variable     | Description                                                            |
| ------------ | ---------------------------------------------------------------------- |
| `SECRET_KEY` | Key used to sign JWTs (HS256).                                         |
| `DB_URI`     | SQLAlchemy database URL, for example `postgresql://admin:admin@localhost:5432/mydb`. |

### Gateway

| Variable                 | Description                                                       |
| ------------------------ | ----------------------------------------------------------------- |
| `AUTH_SVC`               | Base URL of the auth service, including a trailing slash, for example `http://localhost:8000/`. |
| `MONGO_URI`              | MongoDB connection string.                                        |
| `KAFKA_CLUSTER_SERVER`   | Kafka bootstrap server address.                                   |
| `KAFKA_CLUSTER_USERNAME` | Kafka SASL username.                                              |
| `KAFKA_CLUSTER_SECRET`   | Kafka SASL password.                                              |

### Converter

| Variable                 | Description                           |
| ------------------------ | ------------------------------------- |
| `MONGO_URI`              | MongoDB connection string.            |
| `KAFKA_CLUSTER_SERVER`   | Kafka bootstrap server address.       |
| `KAFKA_CLUSTER_USERNAME` | Kafka SASL username.                  |
| `KAFKA_CLUSTER_SECRET`   | Kafka SASL password.                  |
| `KAFKA_CONSUMER_GUID`    | Kafka consumer group ID.              |

### Notification

| Variable                 | Description                                                         |
| ------------------------ | ------------------------------------------------------------------- |
| `GMAIL_ADDRESS`          | Sender Gmail address.                                               |
| `GMAIL_PASSWORD`         | Gmail app password.                                                 |
| `GATEWAY_URL`            | Public base URL of the gateway, including a trailing slash.         |
| `DOWNLOAD_ENDPOINT`      | Download path template. Defaults to `download/{}/`, where `{}` is replaced by the MP3 ID. |
| `KAFKA_CLUSTER_SERVER`   | Kafka bootstrap server address.                                     |
| `KAFKA_CLUSTER_USERNAME` | Kafka SASL username.                                                |
| `KAFKA_CLUSTER_SECRET`   | Kafka SASL password.                                                |
| `KAFKA_CONSUMER_GUID`    | Kafka consumer group ID.                                            |

Environment files and Kubernetes `secret.yml` files are excluded from version control by `.gitignore`. Do not commit credentials.

## Running Locally

1. Start PostgreSQL:

   ```bash
   docker compose up -d
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install pymongo requests python-multipart moviepy
   ```

3. Start the auth and gateway services from the `src` directory, in separate terminals:

   ```bash
   cd src
   uvicorn auth.main:app --port 8000
   ```

   ```bash
   cd src
   uvicorn gateway.main:app --port 8001
   ```

4. Start the converter and notification workers from their own directories, in separate terminals:

   ```bash
   cd src/converter
   python main.py
   ```

   ```bash
   cd src/notification
   python main.py
   ```

5. Confirm that the HTTP services are available:

   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8001/health
   ```

## Deploying to Kubernetes

1. Build and push an image for each service:

   ```bash
   docker build -t <registry>/mp3-auth:latest src/auth
   docker build -t <registry>/mp3-gateway:latest src/gateway
   docker build -t <registry>/mp3-converter:latest src/converter
   docker build -t <registry>/mp3-notification:latest src/notification
   docker push <registry>/mp3-auth:latest
   # Repeat for the remaining images.
   ```

2. Replace the `<image url>` placeholder in each `src/<service>/k8s/deployment.yml` with the corresponding image reference.

3. Create a `secret.yml` for each service in its `k8s` directory. Each Secret must be named `<service>-secret` (for example, `auth-secret`) and contain the variables listed under [Configuration](#configuration) that are not supplied by a ConfigMap:

   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: auth-secret
   type: Opaque
   stringData:
     SECRET_KEY: "<value>"
     DB_URI: "<value>"
   ```

4. Apply the manifests:

   ```bash
   kubectl apply -f src/auth/k8s/
   kubectl apply -f src/gateway/k8s/
   kubectl apply -f src/converter/k8s/
   kubectl apply -f src/notification/k8s/
   ```

The gateway is exposed through a NodePort Service on port `30000` and an Ingress using the `nginx-gateway` ingress class. Inside the cluster, the gateway reaches the auth service at `http://auth-service:8000/`.

## API Reference

All public endpoints are served by the gateway on port 8001. Interactive OpenAPI documentation is available at `/docs` when the service is running.

### Create a user

```
POST /create-user?email=<email>&password=<password>
```

```bash
curl -X POST "http://localhost:8001/create-user?email=user@example.com&password=secret"
```

### Log in

```
POST /login
Authorization: Basic <base64(email:password)>
```

Returns a JWT that is valid for 30 minutes.

```bash
curl -X POST -u user@example.com:secret http://localhost:8001/login
```

```json
{ "access_token": "<jwt>" }
```

### Convert a video

```
POST /convert
Authorization: Bearer <jwt>
Content-Type: multipart/form-data
```

```bash
curl -X POST http://localhost:8001/convert \
  -H "Authorization: Bearer <jwt>" \
  -F "file=@video.mp4"
```

```json
{ "file_id": "<video id>" }
```

The conversion is performed asynchronously. The MP3 ID is delivered to the user by email once conversion completes.

### Download an MP3

```
GET /download/{mp3_id}
```

```bash
curl -o audio.mp3 http://localhost:8001/download/<mp3_id>
```

### Health check

```
GET /health
```

```json
{ "status": "ok" }
```

## Known Limitations

- The per-service `requirements.txt` files do not yet list every runtime dependency. The gateway additionally requires `pymongo`, `requests`, and `python-multipart`; the converter requires `pymongo` and `moviepy`.
- User passwords are stored in plain text. They should be hashed (for example, with bcrypt) before this system is used in production.
- The `/download/{mp3_id}` endpoint does not require authentication.
- There is no automated test suite.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
