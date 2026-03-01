from fastapi import HTTPException
import pandas as pd
import time
from backend.src.database.db_utils import download_all_videos_metadata, download_all_products_metadata,  download_user_interactions
import numpy as np


# caching product recommendations
_products_recommendation_cache = {"data": None, "timestamp": 0, "ttl": 300, "n_recommended": 20}

def product_recommendation(n_recommended: int = 20) -> pd.DataFrame:
    """
    Recommendation service that returns products in preferred categories with added randomness

    making it as efficient as possible using 
    1) caching
    2) vectorization
    3) early filtering
    4) numpy operations

    Note: if you want to override caching either request a different number of products next time or refresh the shop
    """
    try:

        # NOTE: here "bucket" means category / genre
        current_time = time.time()

        # step 0 if n_recommended products requested is different from last time or the refresh button is clicked then clear the cache.
        # TODO: add refresh logic
        if n_recommended != _products_recommendation_cache["n_recommended"]:
            _products_recommendation_cache["data"] = None

        # Step 1 check cache (5 minute TTL)

        if _products_recommendation_cache["data"] is not None:
            if current_time - _products_recommendation_cache["timestamp"] < _products_recommendation_cache["ttl"]:
                return _products_recommendation_cache["data"]
        
        # Step 2 get the parquet files and make dataframes out of:
        # 1) user_interactions
        # 2) video metadata
        # 3) products metadata

        user_interactions_df = download_user_interactions()
        videos_df = download_all_videos_metadata()
        products_df = download_all_products_metadata()

        if user_interactions_df.empty or products_df.empty or videos_df.empty:
            empty_result = []
            _products_recommendation_cache["data"] = empty_result
            _products_recommendation_cache["timestamp"] = current_time
            return empty_result

        # Step 3 join user_interactions + video metadata on video_id column and keep only the rows for vids user watched

        # Set indices on the dataframes for faster accessing modifying dataframe itself.
        user_interactions_df = user_interactions_df.set_index("video_id")
        videos_df = videos_df.set_index("video_id")

        # left join dataframes keeping video info for the ones the user watched
        interactions_with_buckets = user_interactions_df.join(videos_df)
        
        interactions_with_buckets = interactions_with_buckets.dropna(subset = ["bucket_num"])

        interactions_with_buckets["bucket_num"] = interactions_with_buckets["bucket_num"].astype(np.int32)

        if interactions_with_buckets.empty:
            # just recommend random products since no proper interaction data
            result = products_df.sample(min(n_recommended, len(products_df))).to_dict(orient = "records")

            _products_recommendation_cache["data"] = result
            _products_recommendation_cache["timestamp"] = current_time

            return result
    
        # step 4 get the frequency of interaction for each bucket weighted by watch time 
        buckets_watched = interactions_with_buckets["bucket_num"].values.astype(np.int32)
        watch_times = interactions_with_buckets["watch_time_ms"].values.astype(np.float32)

        products_bucket_num_max = products_df["bucket_num"].astype(np.int32).max()
        max_bucket_id= int(max(buckets_watched.max(), products_bucket_num_max)) + 1

        bucket_watch_frequency_array = np.bincount(buckets_watched, weights = watch_times, minlength= max_bucket_id)

        # step 5 based on frequency of interaction weigh the preferred video buckets up that are available in products dataframe and normalize
        total_watch_time = np.sum(bucket_watch_frequency_array)

        if total_watch_time == 0:
            # user hasnt watched any videos so recommend random products
            result = products_df.sample(min(n_recommended, len(products_df))).to_dict(orient = "records")
            _products_recommendation_cache["data"] = result
            _products_recommendation_cache["timestamp"] = current_time
            return result
        
        # step 6 sample from available products dataframe randomly picking rows with higher likelihood of choosing rows in higher weight buckets.
        preferred_buckets = np.where(bucket_watch_frequency_array > 0)[0]

        product_buckets = products_df["bucket_num"].values.astype(np.int32)
        preferred_product_buckets = np.isin(product_buckets, preferred_buckets)

        # only recommending relevant products in subset of dataframe that are in buckets user interacted 
        preferred_products_df = products_df[preferred_product_buckets].reset_index(drop = True)

        if len(preferred_products_df) == 0:
            # edge case where no products in preferred categories
            result = products_df.sample(min(n_recommended, len(products_df))).to_dict(orient = "records")
            _products_recommendation_cache["data"] = result
            _products_recommendation_cache["timestamp"] = current_time
            return result
        
        # weighing and ranking the relevant buckets available in products dataframe based on interaction frequency
        bucket_weights = bucket_watch_frequency_array[preferred_products_df["bucket_num"].values.astype(np.int32)]

        # normalizing because need a normalized value between 0 and 1 for np random choice sampling
        bucket_weights = bucket_weights.astype(np.float32)
        bucket_weights = bucket_weights / np.sum(bucket_weights)
        print(bucket_weights)
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
        _products_recommendation_cache["data"] = result_df.to_dict(orient = "records")
        _products_recommendation_cache["timestamp"] = current_time
        _products_recommendation_cache["n_recommended"] = n_recommended

        result = _products_recommendation_cache["data"]
        return result
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"product recommendation failed: {str(e)}")

def video_recommendation(n_recommended: int = 10) -> list[dict]:
    """
    70/30 mix of weighted preferred videos and random exploration.
    Keeps track of videos already recommended (assumes all were watched or user doesnt want to watch'em and recommends new ones)
    If no unwatched videos period or even in user preferred categories then videos are randomly selected 
    """
    videos_df = download_all_videos_metadata()

    if videos_df.empty:
        raise HTTPException("No video metadata available in database")
    
    if len(videos_df) <= n_recommended:
        return videos_df.to_dict(orient = "records")
    
    # If fewer than n videos exist in the database , return all
    if len(videos_df) <= n_recommended:
        return videos_df.to_dict(orient="records")
    
    user_interactions_df = download_user_interactions()

    try:
        # Step 1: Fallback if user has no interactions yet
        if user_interactions_df.empty:
            return videos_df.sample(min(n_recommended, len(videos_df))).to_dict(orient="records")
        

        # step 2: Join interactions with video metadata to get bucket_num (category of videos interacted with)
        ui_df = user_interactions_df.set_index("video_id")
        v_df = videos_df.set_index("video_id")

        interactions_with_buckets = ui_df.join(v_df).dropna(subset=["bucket_num"])

        if interactions_with_buckets.empty:
            return videos_df.sample(min(n_recommended, len(videos_df))).to_dict(orient="records")
        
        # Step 3: Calculate weights for each bucket based on watch time
        buckets_watched = interactions_with_buckets["bucket_num"].astype(np.int32).values
        watch_times = interactions_with_buckets["watch_time_ms"].astype(np.float32).values

        # determing max bucket id across both dataframes so that the right number of bins can be made in category watch frequency array
        vid_bucket_num_max = videos_df["bucket_num"].astype(np.int32).max()
        max_bucket_id = int(max(buckets_watched.max(), vid_bucket_num_max)) + 1

        bucket_watch_frequency_array = np.bincount(buckets_watched, weights = watch_times, minlength = max_bucket_id)

        # step 4: remove videos the user has already watched
        watched_video_ids = user_interactions_df["video_id"].unique()
        unwatched_videos_df = videos_df[~videos_df["video_id"].isin(watched_video_ids)].copy()

        if unwatched_videos_df.empty:
            # edge case: user literally watched every video in the database. So just give them random watched videos
            return videos_df.sample(min(n_recommended, len(videos_df))).to_dict(orient = "records")
        
        # step 5: filtering unwatched videos into preferred categories
        unwatched_buckets = unwatched_videos_df["bucket_num"].astype(np.int32).values
        preferred_mask = bucket_watch_frequency_array[unwatched_buckets] > 0

        #only keeping unwatched videos whose category has been watched by the user before
        preferred_vids_df = unwatched_videos_df[preferred_mask].reset_index(drop = True)

        if preferred_vids_df.empty:
            # if no videos are preferred... maybe because all videos in categories user prefers are watched, recommend random videos watched or unwatched 
            return videos_df.sample(min(n_recommended, len(videos_df))).to_dict(orient = "records")
        
        # Step 6: 70% preferred videos sampled weighted using bucket interaction frequency.
        n_preferred = int(n_recommended * 0.7)
        # making sure the number of preferred videos we recommend does not exceed the number of those preferred videos available
        n_preferred_capped = min(n_preferred, len(preferred_vids_df))

        # Map the bucket weights to specififc rows in our preferred dataframe
        pref_vids_buckets = preferred_vids_df["bucket_num"].astype(np.int32).values
        vid_weights = bucket_watch_frequency_array[pref_vids_buckets].astype(np.float32)
        vid_weights /= np.sum(vid_weights) #normalize to bring weights between 0 and 1 so that np random choice can do its thing

        preferred_indices = np.random.choice(
            len(preferred_vids_df),
            size = n_preferred_capped,
            p = vid_weights,
            replace = False # no duplicates
        )

        preferred_sampled = preferred_vids_df.iloc[preferred_indices]

        # step 7: 30% exploratory sampling (randomly choose from remaining set of unwatched videos)
        picked_ids = preferred_sampled["video_id"].values
        exploratory_vids_df = unwatched_videos_df[~unwatched_videos_df["video_id"].isin(picked_ids)].reset_index(drop = True)

        n_explore = n_recommended - n_preferred_capped
        # making sure that the number of exploratory videos recommended doesnt exceed the number of those videos available.
        n_explore_capped = min(n_explore, len(exploratory_vids_df))
        explore_sampled = pd.DataFrame()
        if n_explore_capped > 0:
            explore_sampled = exploratory_vids_df.sample(n = n_explore_capped, replace = False)
        
        # Step 8 combine and shuffle and return 

        result_df = pd.concat([preferred_sampled, explore_sampled], ignore_index = True)

        result_df = result_df.sample(frac = 1).reset_index(drop = True)
        
        return result_df.to_dict(orient = "records")

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"video recommendation failed: {str(e)}")
