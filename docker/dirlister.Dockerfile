FROM python:3.9-slim-buster

RUN mkdir -p dirlister
COPY . /dirlister
WORKDIR /dirlister

RUN pip install pipenv
RUN pipenv sync
