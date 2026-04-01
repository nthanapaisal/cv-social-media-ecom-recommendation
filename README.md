# Social Media Feed and Ecommerce Recommendation

Supakjeera Thanapaisal, Suraj Jayakumar, Bryan Smith, Joel Jacob Stephen

---

## Description

{name} is a full stack application that demonstrates an end-to-end multi-modal social media feed and e-commerce recommendation system.

We use computer vision to integrate short-form video content with personalized product recommendations through a number of modalities including visual features, textual signal, and semantic descriptions.

## How to Run

### Backend

```cd cv-social-media-ecom-recommendation```<br>
```docker build -t cv-ecomm-rec-api```<br>
```docker run -p 127.0.0.1:8000:8000 cv-ecomm-rec-api```

### Frontend

## Architecture

<img src="./resources/architecture.png" alt="drawing" width="600"/>

## Data and Preprocessing

### Videos

Source: [UGC-VideoCap TikToks](https://huggingface.co/datasets/openinterx/UGC-VideoCap)

Database: 1000 samples (full dataset)

Test Data: 20 samples (random)

Preprocessing script: ```/data_processing/preprocess_videos.py```
1. Extract video metadata
2. Categorize with videomae-small-finetuned-kinetics
3. Generate parquet file and save to folder

### Products

Source: [Amazon Berkeley Objects (ABO) Dataset](https://amazon-berkeley-objects.s3.amazonaws.com/index.html)

Database: ~200 hand selected products, 10/category

Test Data: 20 products, 2/category

Preprocessing script: ```/data_processing/preprocess_products.py```
1. Extract metadata from product JSON
2. Discard known bad products
3. Predict category by keywords
   1. ```--interactive``` Manually verify or retag category 
4. Assemble parquet file and save product image to folder

### Evaluation

Source: Curated YouTube Shorts

Samples: 200 manually scraped videos

Samples were manually labeled according to the 10 categories

## Video Categorization

Categories
1. Fashion
2. Beauty
3. Electronics
4. Home
5. Fitness
6. Food
7. Baby
8. Automotive
9. Pets
10. Gaming

## User Interaction

## Recommendation System

## User Study
