FROM kielometer/spark:4.0.2

# Run as root user
USER root

# Set HOME
RUN mkdir -p /home/spark && chown spark:spark /home/spark
ENV HOME=/home/spark

# Install Python packages
COPY requirements.txt /opt/requirements.txt

RUN pip3 install --no-cache-dir -r /opt/requirements.txt && \
    apt-get clean

# Set working directory
WORKDIR /opt/notebooks

# Set Environment variables
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3
