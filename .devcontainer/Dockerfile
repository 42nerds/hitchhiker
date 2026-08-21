FROM mcr.microsoft.com/devcontainers/python:2-3.11-bullseye

ENV PYTHONUNBUFFERED 1

RUN    apt-get update \
    && apt-get install bash-completion --no-install-recommends -yq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
