from pyspark.sql import SparkSession


def create_spark_session() -> SparkSession:
    builder = SparkSession.builder.appName("MinIO Connectivity Test")

    # Init MinIO connectivity
    #fmt: off
    builder = builder \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    
    builder = builder \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescencePartitions.enabled", "true")
    # fmt: on

    spark = builder.getOrCreate()
    return spark


spark = create_spark_session()
