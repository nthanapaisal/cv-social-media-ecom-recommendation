# source ~/miniconda3/bin/activate
# conda create -n spark_env python=3.10 -y
# conda activate spark_env
# pip install pyspark
# conda install -c conda-forge openjdk=17 -y
# pip install opencv-python
# pip install requests

import cv2
from pyspark.sql import SparkSession
import requests
spark = (
        SparkSession.builder
        .appName("MyApp")
        .master("local[*]")   # use all cores
        .getOrCreate()
 )
API_URL = "http://localhost:8000/upload/video"

# ground truth
ground_truth_df = spark.read.csv("./data/eval_data/categorization_data.csv", header=True)
ground_truth_df.show()

results = []

for i in range(1, 209):
    file_path = f"./data/eval_data/{str(i).zfill(5)}.mp4"
    print(f"processing: {file_path}")
    with open(file_path, "rb") as f:
        files = {
            "video": (f"{i}.mp4", f, "video/mp4")
        }
        data = {
                "description": " "   
        }
        response = requests.post(API_URL, files=files, data=data)

    if response.status_code == 200:
        bucket_name = response.json()["bucket_name"]
        results.append((i, bucket_name))
        print(i, bucket_name)
    else:
        print(i, "ERROR", response.text)

results_df = spark.createDataFrame(results, ["video_id", "bucket_name"])
results_df.show()

results_df.coalesce(1).write.mode("overwrite").parquet("./data/eval_data/eval_predicted")