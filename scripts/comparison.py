
import cv2
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, array_contains, concat_ws
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
predicted_df = spark.read.parquet("./data/eval_data/eval_predicted/")
predicted_df.show()
print(predicted_df.count())

joined_df = ground_truth_df.join(predicted_df, on="video", how="inner")
joined_df.show()

correct_df = joined_df.filter(
    array_contains(col("bucket_names"), col("category"))
)

rows = correct_df.count()
print(rows)
print(str(rows/208 * 100) + "%")

joined_df = joined_df.withColumn(
    "is_correct",
    array_contains(col("bucket_names"), col("category")),
)
output_df = joined_df.withColumn(
    "bucket_names",
    concat_ws(", ", col("bucket_names"))
)

output_df.coalesce(1).write \
    .option("header", True) \
    .mode("overwrite") \
    .csv("./data/eval_data/predicted_data.csv")

# incorrect_df = joined_df.filter(col("category") != col("bucket_names"))
incorrect_df = joined_df.filter(
    ~array_contains(col("bucket_names"), col("category"))
)

output_df = incorrect_df.withColumn(
    "bucket_names",
    concat_ws(", ", col("bucket_names"))
)
output_df.coalesce(1).write \
    .option("header", True) \
    .mode("overwrite") \
    .csv("./data/eval_data/incorrect_predicted_data.csv")

