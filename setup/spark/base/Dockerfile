FROM apache/spark:4.0.2

USER root

# Install hadoop-aws and aws-java-sdk-bundle
RUN curl -L -o /opt/spark/jars/hadoop-aws-3.4.1.jar \
    https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.4.1/hadoop-aws-3.4.1.jar && \
    curl -L -o /opt/spark/jars/bundle-2.29.38.jar \
    https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.29.38/bundle-2.29.38.jar

RUN chmod 644 /opt/spark/jars/hadoop-aws-3.4.1.jar /opt/spark/jars/bundle-2.29.38.jar

# Install Python packages
COPY requirements.txt /opt/requirements.txt

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install --no-cache-dir -r /opt/requirements.txt && \
    apt-get clean

# Set working directory
WORKDIR /opt/spark

# Set Environment variables
ENV SPARK_HOME=/opt/spark
ENV PATH=${SPARK_HOME}/bin:${SPARK_HOME}/sbin:${PATH}

# Set user to "spark"
USER spark
