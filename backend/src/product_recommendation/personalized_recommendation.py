from fastapi import HTTPException
import pandas as pd
import time
from backend.src.database.db_utils import download_all_videos_metadata, download_all_products_metadata,  download_user_interactions
import numpy as np
from datetime import datetime

def _df_to_records(df: pd.DataFrame) -> list[dict]:
    """Convert DataFrame to records replacing all NA/NaN variants with None for JSON safety."""
    return [
        {k: (None if pd.isna(v) else v) for k, v in rec.items()}
        for rec in df.to_dict(orient="records")
    ]

# Number of video categories user needs to watch until they get 80% preferred products and 70% preferred videos. (Represents the usual total number of categories the average user is interested in)
PROFILE_SATURATION_POINT = 4.0

# caching product recommendations
_products_recommendation_cache = {"data": None, "timestamp": 0, "ttl": 300, "n_recommended": 20}

def product_recommendation(n_recommended: int = 50) -> pd.DataFrame:
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
        # REFACTORED: Explode bucket_num so each bucket in the list gets its own row with the same watch_time
        # This handles videos with multiple assigned categories (e.g., video has bucket_num=[1,2,3])
        # After explode: each video-bucket pair gets attributed the full watch_time
        interactions_with_buckets = interactions_with_buckets.reset_index().explode("bucket_num").set_index("video_id")
        interactions_with_buckets["bucket_num"] = interactions_with_buckets["bucket_num"].astype(np.int32)
        
        # FEATURE: Distribute "other" category (bucket_num=13) watch time across all other categories
        # while retaining a small portion for the "other" category itself.
        other_bucket_id = 13
        other_mask = interactions_with_buckets["bucket_num"] == other_bucket_id
        other_interactions = interactions_with_buckets[other_mask].copy()
        
        if not other_interactions.empty:
            # Dynamically fetch all unique categories from products
            unique_categories = products_df["bucket_num"].dropna().astype(np.int32).unique()
            other_categories = [cat for cat in unique_categories if cat != other_bucket_id]
            
            if not other_categories:
                other_categories = [1]
                
            # Define how much weight stays with 'other' (e.g., 20%)
            retention_ratio = 0.10
            distribution_ratio = 1.0 - retention_ratio
                
            expanded_rows_list = []
            for cat_id in other_categories:
                expanded = other_interactions.copy()
                expanded["bucket_num"] = cat_id
                # Distribute the remaining watch_time equally across other categories
                expanded["watch_time_ms"] = expanded["watch_time_ms"] * (distribution_ratio / len(other_categories))
                expanded_rows_list.append(expanded)
            
            # Keep the original 'other' interactions but reduce their weight
            reduced_other = other_interactions.copy()
            reduced_other["watch_time_ms"] = reduced_other["watch_time_ms"] * retention_ratio
            
            # Combine expanded rows, reduced 'other' rows, and remove original full-weight "other" interactions
            expanded_df = pd.concat(expanded_rows_list + [reduced_other], ignore_index=False)
            interactions_with_buckets = interactions_with_buckets[~other_mask]
            interactions_with_buckets = pd.concat([interactions_with_buckets, expanded_df], ignore_index=False)
            
        if interactions_with_buckets.empty:
            # just recommend random products since no proper interaction data
            result = _df_to_records(products_df.sample(min(n_recommended, len(products_df))))

            _products_recommendation_cache["data"] = result
            _products_recommendation_cache["timestamp"] = current_time

            return result
    
        # step 4 build engagement scores per interaction
        buckets_watched = interactions_with_buckets["bucket_num"].values.astype(np.int32)
        watch_times = interactions_with_buckets["watch_time_ms"].values.astype(np.float32)

        skipped = interactions_with_buckets["skipped_quickly"].fillna(False).astype(bool).values
        watched_half = interactions_with_buckets["watched_50_pct"].fillna(False).astype(bool).values

        # Penalise quick skips (0.1×), reward videos watched past halfway (1.5×)
        engagement_scores = watch_times.copy()
        engagement_scores[skipped] *= 0.1
        engagement_scores[watched_half] *= 1.5
        
        # Recency weighting: exponential decay with 7-day half-life
        now = datetime.now()
        if 'interaction_timestamp' in interactions_with_buckets.columns:
            try:
                timestamps = interactions_with_buckets['interaction_timestamp']
                days_ago = np.array([(now - pd.to_datetime(ts)).days for ts in timestamps])
                recency_decay = np.exp(-days_ago / 7)
                engagement_scores *= recency_decay
            except Exception as e:
                # If timestamp parsing fails, use all interactions with equal weight
                print(f"Warning: Could not apply recency weighting: {e}")
        else:
            # Backward compatibility: interactions without timestamp column
            # Treat old interactions as if they're 30 days old (low weight)
            print("Warning: 'interaction_timestamp' column not found. Using uniform weights.")

        products_bucket_num_max = products_df["bucket_num"].astype(np.int32).max()
        max_bucket_id= int(max(buckets_watched.max(), products_bucket_num_max)) + 1

        bucket_watch_frequency_array = np.bincount(buckets_watched, weights=engagement_scores, minlength=max_bucket_id)

        # step 5 based on frequency of interaction weigh the preferred video buckets up that are available in products dataframe and normalize
        total_watch_time = np.sum(bucket_watch_frequency_array)

        if total_watch_time == 0:
            # user hasnt watched any videos so recommend random products
            result = _df_to_records(products_df.sample(min(n_recommended, len(products_df))))
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
            result = _df_to_records(products_df.sample(min(n_recommended, len(products_df))))
            _products_recommendation_cache["data"] = result
            _products_recommendation_cache["timestamp"] = current_time
            return result
        
        # weighing and ranking the relevant buckets available in products dataframe based on interaction frequency
        bucket_weights = bucket_watch_frequency_array[preferred_products_df["bucket_num"].values.astype(np.int32)]

        # normalizing because need a normalized value between 0 and 1 for np random choice sampling
        bucket_weights = bucket_weights.astype(np.float32)
        bucket_weights = bucket_weights / np.sum(bucket_weights)
        # --- Dynamic Exploration Warm-up ---
        # Calculate how many unique categories the user actually prefers
        n_unique_prefs = len(preferred_buckets)
        
        # Base split is 80-20, but scales down if they've seen very few categories
        # e.g., 1 category = 20% preferred, 2 = 40%, 3 = 60%, 4+ = 80%
        target_preferred_ratio = 0.80
        warmup_factor = min(1.0, n_unique_prefs / PROFILE_SATURATION_POINT) 
        dynamic_ratio = target_preferred_ratio * warmup_factor
        
        n_preferred = int(n_recommended * dynamic_ratio)
        # ----------------------------------------

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
        _products_recommendation_cache["data"] = _df_to_records(result_df)
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
        return _df_to_records(videos_df)

    # If fewer than n videos exist in the database , return all
    if len(videos_df) <= n_recommended:
        return _df_to_records(videos_df)

    user_interactions_df = download_user_interactions()

    try:
        # Step 1: Fallback if user has no interactions yet
        if user_interactions_df.empty:
            return _df_to_records(videos_df.sample(min(n_recommended, len(videos_df))))
            
        # step 2: Join interactions with video metadata to get bucket_num (category of videos interacted with)
        ui_df = user_interactions_df.set_index("video_id")
        v_df = videos_df.set_index("video_id")

        interactions_with_buckets = ui_df.join(v_df).dropna(subset=["bucket_num"])
        # Explode bucket_num so each bucket gets its own row with the same watch_time
        interactions_with_buckets = interactions_with_buckets.reset_index().explode("bucket_num").set_index("video_id")
        
        # FIX: Cast to int32 before creating the mask so `== 13` works correctly
        interactions_with_buckets["bucket_num"] = interactions_with_buckets["bucket_num"].astype(np.int32)
        
        # FEATURE: Distribute "other" category (bucket_num=13) watch time across all other categories
        # while retaining a small portion for the "other" category itself.
        other_bucket_id = 13
        other_mask = interactions_with_buckets["bucket_num"] == other_bucket_id
        other_interactions = interactions_with_buckets[other_mask].copy()
        
        if not other_interactions.empty:
            # Dynamically fetch all unique categories from the video catalog
            unique_categories = videos_df["bucket_num"].explode().dropna().astype(np.int32).unique()
            
            # Distribute evenly across all available categories EXCEPT 'other' (13)
            other_categories = [cat for cat in unique_categories if cat != other_bucket_id]
            
            # Fallback in case no other categories exist
            if not other_categories:
                other_categories = [1]
                
            # Define how much weight stays with 'other' (e.g., 10%)
            retention_ratio = 0.10
            distribution_ratio = 1.0 - retention_ratio
                
            expanded_rows_list = []
            for cat_id in other_categories:
                expanded = other_interactions.copy()
                expanded["bucket_num"] = cat_id
                # Distribute the remaining watch_time equally across other categories
                expanded["watch_time_ms"] = expanded["watch_time_ms"] * (distribution_ratio / len(other_categories))
                expanded_rows_list.append(expanded)
            
            # Keep the original 'other' interactions but reduce their weight
            reduced_other = other_interactions.copy()
            reduced_other["watch_time_ms"] = reduced_other["watch_time_ms"] * retention_ratio
            
            # Combine expanded rows, reduced 'other' rows, and remove original full-weight "other" interactions
            expanded_df = pd.concat(expanded_rows_list + [reduced_other], ignore_index=False)
            interactions_with_buckets = interactions_with_buckets[~other_mask]
            interactions_with_buckets = pd.concat([interactions_with_buckets, expanded_df], ignore_index=False)

        if interactions_with_buckets.empty:
            return _df_to_records(videos_df.sample(min(n_recommended, len(videos_df))))

        # Step 3: Calculate engagement scores per interaction
        buckets_watched = interactions_with_buckets["bucket_num"].values.astype(np.int32)
        watch_times = interactions_with_buckets["watch_time_ms"].values.astype(np.float32)

        skipped = interactions_with_buckets["skipped_quickly"].fillna(False).astype(bool).values
        watched_half = interactions_with_buckets["watched_50_pct"].fillna(False).astype(bool).values

        # Penalise quick skips (0.1×), reward videos watched past halfway (1.5×)
        engagement_scores = watch_times.copy()
        engagement_scores[skipped] *= 0.1
        engagement_scores[watched_half] *= 1.5
        
        # Recency weighting: exponential decay with 7-day half-life
        now = datetime.now()
        if 'interaction_timestamp' in interactions_with_buckets.columns:
            try:
                timestamps = interactions_with_buckets['interaction_timestamp']
                days_ago = np.array([(now - pd.to_datetime(ts)).days for ts in timestamps])
                recency_decay = np.exp(-days_ago / 7)
                engagement_scores *= recency_decay
            except Exception as e:
                # If timestamp parsing fails, use all interactions with equal weight
                print(f"Warning: Could not apply recency weighting: {e}")
        else:
            # Backward compatibility: interactions without timestamp column
            # Treat old interactions as if they're 30 days old (low weight)
            print("Warning: 'interaction_timestamp' column not found. Using uniform weights.")

        # determining max bucket id across all exploded video buckets for the category watch frequency array
        vid_bucket_num_max = videos_df["bucket_num"].explode().astype(np.int32).max()
        max_bucket_id = int(max(buckets_watched.max(), vid_bucket_num_max)) + 1

        bucket_watch_frequency_array = np.bincount(buckets_watched, weights=engagement_scores, minlength=max_bucket_id)

        # step 4: remove videos the user has already watched
        watched_video_ids = user_interactions_df["video_id"].unique()
        unwatched_videos_df = videos_df[~videos_df["video_id"].isin(watched_video_ids)].copy()

        if unwatched_videos_df.empty:
            # edge case: user literally watched every video in the database. So just give them random watched videos
            return _df_to_records(videos_df.sample(min(n_recommended, len(videos_df))))
        
        # Explode unwatched_videos_df so each bucket gets its own row
        # This allows proper filtering since unwatched_videos_df has bucket_num as lists (not single values)
        # After explode: can safely convert bucket_num to int32 and index into bucket_watch_frequency_array
        unwatched_videos_df = unwatched_videos_df.reset_index().explode("bucket_num").set_index("video_id")
        unwatched_videos_df["bucket_num"] = unwatched_videos_df["bucket_num"].astype(np.int32)
        
        # step 5: filtering unwatched videos into preferred categories
        unwatched_buckets = unwatched_videos_df["bucket_num"].values.astype(np.int32)
        preferred_mask = bucket_watch_frequency_array[unwatched_buckets] > 0

        # Reset index to make video_id a column before filtering
        # This preserves video_id as a column for later operations
        unwatched_videos_df = unwatched_videos_df.reset_index(drop=False)
        # NEW: Count unique preferred categories for dynamic scaling of relevant vs random video recommendation
        n_unique_prefs = np.count_nonzero(bucket_watch_frequency_array > 0)

        
        # only keeping unwatched videos whose category has been watched by the user before
        preferred_vids_df = unwatched_videos_df[preferred_mask]

        if preferred_vids_df.empty:
            # if no videos are preferred... maybe because all videos in categories user prefers are watched, recommend random videos watched or unwatched 
            return _df_to_records(videos_df.sample(min(n_recommended, len(videos_df))))
        
        # Drop duplicates to get unique videos (since explode created multiple rows per video with different buckets)
        preferred_vids_df = preferred_vids_df.drop_duplicates(subset=["video_id"])
        
        # Step 6: Preferred videos sampled weighted using bucket interaction frequency.
        # slowly increase the ratio of preferred videos recommended as we watch more categories
        # fixing issue where when app is started fresh with no interactions, the moment a user sees their first video, All subsequent product recommendations are 80% from that category and all subsequent video recommendations are 70% from that one category, since that is the only preferred category.

        # To fix this we slowly ramp up the percentage of preferred content recommended as a function of number of unique categories the user watched.

        # If the user watched videos from over 3 unique categories recommendation split is back to normal (70% for videos, 30% for products)
        target_preferred_ratio = 0.7
        warmup_factor = min(1.0, n_unique_prefs / PROFILE_SATURATION_POINT)
        dynamic_ratio = target_preferred_ratio * warmup_factor
        n_preferred = int(n_recommended * dynamic_ratio)
        # making sure the number of preferred videos we recommend does not exceed the number of those preferred videos available
        n_preferred_capped = min(n_preferred, len(preferred_vids_df))

        # Map the bucket weights to specififc rows in our preferred dataframe
        pref_vids_buckets = preferred_vids_df["bucket_num"].values.astype(np.int32)
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
        exploratory_vids_df = unwatched_videos_df[~unwatched_videos_df["video_id"].isin(picked_ids)]
        
        # Drop duplicates to get unique videos for exploration set
        exploratory_vids_df = exploratory_vids_df.drop_duplicates(subset=["video_id"])

        n_explore = n_recommended - n_preferred_capped
        # making sure that the number of exploratory videos recommended doesnt exceed the number of those videos available.
        n_explore_capped = min(n_explore, len(exploratory_vids_df))
        explore_sampled = pd.DataFrame()
        if n_explore_capped > 0:
            explore_sampled = exploratory_vids_df.sample(n = n_explore_capped, replace = False)
        
        # Step 8 combine and shuffle and return 

        result_df = pd.concat([preferred_sampled, explore_sampled], ignore_index = True)

        result_df = result_df.sample(frac = 1).reset_index(drop = True)
        
        return _df_to_records(result_df)

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"video recommendation failed: {str(e)}")
