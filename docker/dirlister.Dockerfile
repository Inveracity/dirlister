FROM python:3.8-slim-buster

ENV PIPENV_VENV_IN_PROJECT=1
ENV PIPENV_IGNORE_VIRTUALENVS=1
ENV PIPENV_NOSPIN=1
ENV PIPENV_HIDE_EMOJIS=1

RUN mkdir -p dirlister
COPY . /dirlister
WORKDIR /dirlister

RUN pip install -r requirements.txt

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
