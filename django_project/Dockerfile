FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1

COPY . .
COPY download_from_azure.py ./download_from_azure.py
COPY ./requirements.txt /requirements.txt
COPY data_preparation.py ./data_preparation.py
COPY model_training.py ./model_training.py
COPY visualise.py ./visualise.py
COPY upload_to_azure.py ./upload_to_azure.py

RUN pip install -r /requirements.txt

EXPOSE 8000
CMD python manage.py runserver 0.0.0.0:8000

