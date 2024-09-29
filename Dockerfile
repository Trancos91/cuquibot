FROM python:3.12.2-alpine
WORKDIR /app
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
RUN pip3 install python-telegram-bot[job-queue]
COPY ./src/ ./
CMD python3 -u main.py
