# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/

ARG PYTHON_VERSION=3.10

FROM python:${PYTHON_VERSION}-slim as builder

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

FROM python:${PYTHON_VERSION}-slim-bullseye

RUN adduser --system --no-create-home nonroot


# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN adduser --system --no-create-home nonroot

USER nonroot

EXPOSE 8000

COPY . /code/

