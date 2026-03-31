
import cv2
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import requests

spark = (
        SparkSession.builder
        .appName("MyApp")
        .master("local[*]")   # use all cores
        .getOrCreate()
)

# labels
ground_truth_df = spark.read.csv("./data/eval_data/categorization_data.csv", header=True)
ground_truth_df.show()

# predicted
predicted_df = spark.read.parquet("./data/eval_data/eval_predicted/", header=True)
predicted_df.show()
print(predicted_df.count())

joined_df = ground_truth_df.join(predicted_df, ground_truth_df.video == predicted_df.video_id, how="inner").drop(col("video_id"))
joined_df.show()

correct_df = joined_df.filter(col("category") == col("bucket_name"))
rows = correct_df.count()
print(rows)
print(str(rows/208 * 100) + "%")

incorrect_df = joined_df.filter(col("category") != col("bucket_name"))

incorrect_df.coalesce(1).write \
    .option("header", True) \
    .mode("overwrite") \
    .csv("./data/eval_data/incorrect_predicted_data.csv")
