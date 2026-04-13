FROM apache/spark:4.0.2

USER root

# Install python packages
COPY requirements.txt /opt/requirements.txt

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install --no-cache-dir -r /opt/requirements.txt && \
    apt-get clean

# Set environment variables
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Set working directory
WORKDIR /opt/notebooks
