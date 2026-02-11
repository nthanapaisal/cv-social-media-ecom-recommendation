from fastapi import HTTPException
import pandas as pd
import time
from backend.src.database.db_utils import download_all_videos_metadata, download_all_products_metadata,  download_user_interactions
import numpy as np
import logging
logger = logging.getLogger(__name__)

# caching product recommendations
_recommendation_cache = {"data": None, "timestamp": 0, "ttl": 300}

def product_recommendation_service(n_recommended: int = 20):
    """
    Recommendation service that returns top 20 products in preferred categories

    making it as efficient as possible using 
    1) caching
    2) vectorization
    3) early filtering
    4) numpy operations
    """
    try:

        # NOTE: here "bucket" means category / genre
        current_time = time.time()

        # Step 1 check cache (5 minute TTL)

        if _recommendation_cache["data"] is not None:
            if current_time - _recommendation_cache["timestamp"] < _recommendation_cache["ttl"]:
                return _recommendation_cache["data"]
        
        

        # Step 2 get the parquet files and make dataframes out of:
        # 1) user_interactions
        # 2) video metadata
        # 3) products metadata

        user_interactions_df = download_user_interactions()
        videos_df = download_all_videos_metadata()
        products_df = download_all_products_metadata()

        if user_interactions_df.empty or products_df.empty or videos_df.empty:
            empty_result = []
            _recommendation_cache["data"] = empty_result
            _recommendation_cache["timestamp"] = current_time
            return empty_result

        # Step 3 join user_interactions + video metadata on video_id column and keep only the rows for vids user watched

        # Set indices on the dataframes for faster accessing modifying dataframe itself.
        user_interactions_df = user_interactions_df.set_index("video_id")
        videos_df = videos_df.setIndex("video_id")

        # left join dataframes keeping video info for the ones the user watched
        interactions_with_buckets = user_interactions_df.join(videos_df)
        
        interactions_with_buckets = interactions_with_buckets.dropna(subset = ["bucket_num"])

        interactions_with_buckets["bucket_num"] = interactions_with_buckets["bucket_num"].astype(np.int32)

        if interactions_with_buckets.empty:
            # just recommend random products since no proper interaction data
            result = products_df.saple(min(n_recommended, len(products_df))).to_dict(orient = "records")

            _recommendation_cache["data"] = result
            _recommendation_cache["timestamp"] = current_time

            return result
    
        
        # step 4 get the frequency of interaction for each bucket weighted by watch time 
        buckets_watched = interactions_with_buckets["bucket_num"].values.astype(np.int32)
        watch_times = interactions_with_buckets["watch_time_ms"].values.astype(np.float32)

        max_bucket_id= int(max(buckets_watched.max(), products_df["bucket_num"].max())) + 1

        bucket_watch_frequency_array = np.bincount(buckets_watched, weights = watch_times, minlength= max_bucket_id)

        # step 5 based on frequency of interaction weigh the preferred video buckets up that are available in products dataframe and normalize
        total_watch_time = np.sum(bucket_watch_frequency_array)

        if total_watch_time == 0:
            # user hasnt watched any videos so recommend random products
            result = products_df.sample(min(n_recommended, len(products_df))).to_dict(orient = "records")
            _recommendation_cache["data"] = result
            _recommendation_cache["timestamp"] = current_time
            return result
        
        # step 6 sample from available products dataframe randomly picking rows with higher likelihood of choosing rows in higher weight buckets.

        preferred_buckets = np.where(bucket_watch_frequency_array > 0)[0]

        

        product_buckets = products_df["bucket"].values.astype(np.int32)
        preferred_product_buckets = np.isin(product_buckets, preferred_buckets)

        # only recommending relevant products in subset of dataframe that are in buckets user interacted 
        preferred_products_df = products_df[preferred_product_buckets].reset_index(drop = True)

        if len(preferred_products_df) == 0:
            # edge case where no products in preferred categories
            result = products_df.sample(min(n_recommended, len(products_df))).to_dict(orient = "records")
            _recommendation_cache["data"] = result
            _recommendation_cache["timestamp"] = current_time
            return result
        
        # weighing and ranking the relevant buckets available in products dataframe based on interaction frequency
        bucket_weights = bucket_watch_frequency_array[preferred_products_df["bucket_num"].values.astype(np.int32)]

        # normalizing because need a normalized value between 0 and 1 for np random choice sampling
        bucket_weights = bucket_weights.astype(np.float32)
        bucket_weights = bucket_weights / np.sum(bucket_weights)

        # 80-20 split preferred and random
        n_preferred = int(n_recommended * 0.8)

        n_preferred_capped = min(n_preferred, len(preferred_products_df))
        preferred_indices = np.random.choice(
            len(preferred_products_df),
            size = n_preferred_capped,
            p = bucket_weights,
            replace = False
        )

        # dataframe of recommended products based on user video preferences 
        preferred_sampled = preferred_products_df.iloc[preferred_indices]


        picked_ids = preferred_sampled["product_id"].values

        # EXCLUSION MASK - get product ids series in preferred_products dataframe that have not been picked
        remaining_products = ~products_df["product_id"].isin(picked_ids)
        # reset index not required since we will just use pandas sample later (no fancy indexing operations)
        exploratory_products_df = products_df[remaining_products].reset_index(drop = True)


        # step 7 randomly sample from all products and mix in some randomness as well (EXPLORATION)
        
        n_explore = n_recommended - n_preferred_capped

        n_explore_capped = min(n_explore, len(exploratory_products_df))

        if n_explore_capped > 0:
            explore_sampled = exploratory_products_df.sample(
                n = n_explore_capped,
                replace = False
            )
        else:
            # empty dataframe if no more unique products available in dataframe to explore
            explore_sampled = pd.DataFrame()

        result_df = pd.concat([preferred_sampled, explore_sampled], ignore_index = True)

        # shuffling result
        result_df = result_df.sample(frac = 1).reset_index(drop= True)

        # cache result and return 

        _recommendation_cache["data"] = result_df.to_dict(orient = "records")
        _recommendation_cache["timestamp"] = current_time

        return result
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code = 500, detail = f"product recommendation failed: {str(e)}")











