FROM python:3.12.2-alpine
# WORKDIR /app/modulos
# COPY ./src/modulos/* .
# WORKDIR /app/secretos
# COPY ./src/secretos/* .
WORKDIR /app
COPY ./src/ ./
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
RUN pip3 install python-telegram-bot[job-queue]
CMD python3 -u main.py
