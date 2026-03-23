FROM python:3.14-slim

WORKDIR /opt

COPY setup/data_collection/requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
