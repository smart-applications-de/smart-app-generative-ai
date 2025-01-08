FROM ubuntu:latest
LABEL authors="ainea"

ENTRYPOINT ["top", "-b"]