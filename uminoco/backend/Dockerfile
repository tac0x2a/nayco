FROM python:3.8.3-slim

ARG project_directory
ADD requirements.txt $project_directory
WORKDIR $project_directory

RUN pip install -r requirements.txt
