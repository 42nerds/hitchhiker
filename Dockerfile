FROM alpine:3.19

WORKDIR /app

RUN apk add --no-cache py3-pip

COPY . ./hitchhiker
RUN pip3 install --break-system-packages "./hitchhiker[release, copier, gcloud]"
RUN rm -rf ./hitchhiker

RUN adduser --uid 101 --home /app app -D
USER app
