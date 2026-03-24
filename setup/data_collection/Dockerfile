FROM python:3.14-slim

COPY requirements.txt /

RUN pip install --root-user-action ignore --upgrade pip
RUN pip install --root-user-action ignore --no-cache-dir -r /requirements.txt
