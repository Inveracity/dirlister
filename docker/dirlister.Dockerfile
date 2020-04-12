FROM python:3.8-slim-buster

RUN mkdir -p dirlister
COPY . /dirlister
WORKDIR /dirlister

RUN pip install -r requirements.txt

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
