FROM node:14.7.0-alpine3.12 as build-stage

WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY ./frontend/ .

RUN npm run build


# -------------------------------
FROM python:3.8.3-slim as production-stage
COPY --from=build-stage /app/dist /frontend/dist

ARG project_directory
WORKDIR $project_directory
ADD ./backend/requirements.txt $project_directory
COPY ./backend $project_directory

RUN pip install -r requirements.txt

CMD flask run --host 0.0.0.0 --port 5000