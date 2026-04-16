import argparse
from common import create_spark_session


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Input directory: <bucket>[/path/to/files], e.g. processed-data/processed",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output directory: <bucket>[/path/to/files], e.g. analytics/output",
    )
    parser.add_argument(
        "-d",
        "--date",
        required=True,
        help="Target date: YYYY-MM-DD, e.g. 2026-11-05",
    )

    return parser.parse_args()


def transform(df):
    return df.filter(df.stopShortName == 1962)


# ------------------------------------------------------------------------
def main():

    # Parse arguments
    args = parse_args()

    # Initialize Spark Session
    spark = create_spark_session("Job 1: Clean Data")

    # Read data
    df = (
        spark.read.format("parquet")
        .option("mergeSchema", "false")
        .option("pathGlobFilter", "arrivals_*.parquet")
        .load(f"s3a://{args.input}/date={args.date}/")
    )

    # Transform data
    df_transformed = transform(df)

    # Write data
    df_transformed.write.mode("overwrite").parquet(f"s3a://{args.output}/{args.date}.parquet")

    # Stop spark
    spark.stop()


if __name__ == "__main__":
    main()
