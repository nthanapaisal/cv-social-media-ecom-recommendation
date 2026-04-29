"""
Product Recommendation Testing & Validation Script

Tests the product recommendation engine with REAL mock user interactions.
Generates histograms to visualize product category distribution.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta
import shutil
import pickle

# Add parent directory to path so we can import backend module
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_recency_post_warmup(videos_by_category, old_cat=6, new_cat=2, other_cats=[1, 3, 4]):
    old_name = CATEGORY_NAMES.get(old_cat, f"Category {old_cat}")
    new_name = CATEGORY_NAMES.get(new_cat, f"Category {new_cat}")
    print("\n" + "="*70)
    print(f"TEST: Recency Bias + Post-Warmup ({new_name} vs {old_name})")
    print("="*70)
    print(f"Scenario: 5 '{old_name}' videos watched 7 days ago. 10 '{new_name}' videos watched TODAY.")
    print(f"Plus 1 video from 3 other categories to break the warm-up.")
    print(f"Expected: '{new_name}' scales heavily and overshadows '{old_name}' due to recency decay.\n")
    
    # Old interactions (e.g., Food 7 days ago)
    for video_id in videos_by_category.get(old_cat, [])[:5]:
        save_mock_interaction(create_mock_interaction(video_id=video_id, watch_time_ms=60000, days_ago=7))
        
    # New interactions (e.g., Beauty today)
    for video_id in videos_by_category.get(new_cat, [])[:10]:
        save_mock_interaction(create_mock_interaction(video_id=video_id, watch_time_ms=60000, days_ago=0))
        
    # Diversity to clear the warmup penalty (1, 3, 4)
    for cat in other_cats:
        for video_id in videos_by_category.get(cat, [])[:1]:
            save_mock_interaction(create_mock_interaction(video_id=video_id, watch_time_ms=60000, days_ago=0))
            
    recs = product_recommendation(n_recommended=50)
    categories = [int(rec["bucket_num"]) for rec in recs if rec.get("bucket_num") is not None]
    
    plot_histogram(categories, f"Product Test: Recency Bias ({new_name} Today vs {old_name} 7d ago)")
    
    new_count = sum(1 for c in categories if c == new_cat)
    old_count = sum(1 for c in categories if c == old_cat)
    print(f"\n📊 Results:\n   '{new_name}' (today): {new_count}/50\n   '{old_name}' (7d old): {old_count}/50")
from backend.src.product_recommendation.personalized_recommendation import (
    product_recommendation,
    _products_recommendation_cache  # Import cache to clear it between tests
)

# Configuration (relative to project root)
TEST_DIR = project_root / "data" / "test_interactions"
VIDEO_PARQUET_DIR = project_root / "data" / "video_parquet"
PRODUCT_PARQUET_DIR = project_root / "data" / "product_parquet"
CACHE_FILE = project_root / ".product_test_cache.pkl"

# Category Name Mapping
CATEGORY_NAMES = {
    1: "Fashion",
    2: "Beauty",
    3: "Electronics",
    4: "Home",
    5: "Fitness",
    6: "Food",
    7: "Baby",
    8: "Hobby",
    9: "Pets",
    10: "Gaming",
    11: "Outdoor",
    12: "Automotives",
    13: "Other"
}


def test_actual_user_history_products(original_download_func):
    """
    Runs the recommendation engine using the REAL user interaction data
    instead of the mock test directory.
    """
    print("\n" + "="*70)
    print("TEST: Actual User History (Products)")
    print("="*70)
    print("Scenario: Generating recommendations using your REAL app usage data. (User interaction parquet) \n")
    
    from backend.src.database import db_utils
    import backend.src.product_recommendation.personalized_recommendation as rec_module
    
    # 1. Restore the original download function to hit the real data
    db_utils.download_user_interactions = original_download_func
    rec_module.download_user_interactions = original_download_func
    
    # 2. Force clear the cache so we don't just get Test 5's data
    _products_recommendation_cache["data"] = None
    _products_recommendation_cache["timestamp"] = 0
    
    try:
        # 3. Get recommendations
        recs = product_recommendation(n_recommended=50)
        
        # 4. Extract categories
        categories = [int(rec["bucket_num"]) for rec in recs if rec.get("bucket_num") is not None]
        
        # 5. Plot
        plot_histogram(categories, "Actual User History: Product Recommendations")
        print(f"\n📊 Successfully generated recommendations based on real app usage.")
        
    except Exception as e:
        print(f"❌ Failed to generate real recommendations: {e}")
    finally:
        # 6. Re-apply the monkey patch just to leave the environment as we found it
        monkey_patch_download_interactions()

def plot_database_distribution(items_by_category, title, total_categories=13):
    """Plot the total available items per category in the database."""
    if not items_by_category:
        print(f"❌ No data to plot for {title}")
        return
    
    # Determine the range of categories to plot
    max_cat_in_data = max(items_by_category.keys()) if items_by_category else 0
    max_cat = max(total_categories, max_cat_in_data)
    all_cats = list(range(1, max_cat + 1))
    
    # Count the total items available in each category
    counts = [len(items_by_category.get(cat, [])) for cat in all_cats]
    labels = [CATEGORY_NAMES.get(cat, f"Cat {cat}") for cat in all_cats]
    total_items = sum(counts)
    
    plt.figure(figsize=(14, 6))
    
    # NEW DISTINCT COLORS: Using tab20 for clear separation
    colors = plt.cm.tab20.colors[:len(all_cats)]
    
    bars = plt.bar(labels, counts, color=colors, edgecolor='black', linewidth=1.5)
    
    plt.title(title + f" (Total: {total_items})", fontsize=14, fontweight='bold')
    plt.xlabel('Category', fontsize=12, fontweight='bold')
    plt.ylabel('Total Items Available', fontsize=12, fontweight='bold')
    
    plt.xticks(rotation=45, ha='right', fontweight='bold')
    
    max_count = max(counts) if counts else 0
    plt.ylim(0, max_count * 1.15)
    
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        if count > 0:
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(count)}\n({count/total_items*100:.1f}%)',
                    ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    filename = title.replace(": ", "_").replace(" ", "_").lower() + ".png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"✅ Saved: {filename}")
    plt.close()

def load_catalog_by_category(parquet_dir, id_col) -> dict:
    if not os.path.exists(parquet_dir):
        print(f"❌ Error: {parquet_dir} not found")
        return {}
    
    items_by_category = {}
    for filename in os.listdir(parquet_dir):
        if not filename.endswith(".parquet"):
            continue
        filepath = os.path.join(parquet_dir, filename)
        try:
            df = pd.read_parquet(filepath)
            for _, row in df.iterrows():
                item_id = row.get(id_col)
                bucket_num = row.get("bucket_num")
                if pd.notna(item_id) and pd.notna(bucket_num):
                    categories = bucket_num if isinstance(bucket_num, (list, np.ndarray)) else [bucket_num]
                    for cat in categories:
                        cat_id = int(cat) if not isinstance(cat, int) else cat
                        if cat_id not in items_by_category:
                            items_by_category[cat_id] = []
                        items_by_category[cat_id].append(item_id)
        except Exception:
            pass
    return items_by_category

def setup_test_environment():
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR, exist_ok=True)
    _products_recommendation_cache["data"] = None
    _products_recommendation_cache["timestamp"] = 0
    print(f"✅ Created fresh test directory and cleared product cache.\n")

def create_mock_interaction(
    video_id: str,
    watch_time_ms: int = 45000,
    skipped_quickly: bool = False,
    watched_50_pct: bool = True,
    days_ago: int = 0,
) -> dict:
    timestamp = datetime.now() - timedelta(days=days_ago)
    return {
        "video_id": video_id,
        "watch_time_ms": watch_time_ms,
        "skipped_quickly": skipped_quickly,
        "watched_50_pct": watched_50_pct,
        "interaction_timestamp": timestamp.isoformat(),
    }

def save_mock_interaction(interaction: dict):
    df = pd.DataFrame([interaction])
    os.makedirs(TEST_DIR, exist_ok=True)
    file_key = f"{interaction['video_id']}-{int(datetime.now().timestamp() * 1000000)}"
    out_path = os.path.join(TEST_DIR, f"part-{file_key}.parquet")
    df.to_parquet(out_path, engine="pyarrow", index=False)

def monkey_patch_download_interactions():
    from backend.src.database import db_utils
    import backend.src.product_recommendation.personalized_recommendation as rec_module
    
    original_download = db_utils.download_user_interactions
    def test_download():
        if not os.path.exists(TEST_DIR):
            return pd.DataFrame()
        parquet_files = list(Path(TEST_DIR).glob("*.parquet"))
        if not parquet_files:
            return pd.DataFrame()
        dfs = [pd.read_parquet(f) for f in parquet_files]
        return pd.concat(dfs, ignore_index=True)
    
    db_utils.download_user_interactions = test_download
    rec_module.download_user_interactions = test_download
    return original_download

def plot_histogram(categories, title, total_categories=13):
    if not categories:
        print("❌ No products recommended to plot")
        return
    
    max_cat_in_data = max(categories) if categories else 0
    max_cat = max(total_categories, max_cat_in_data)
    all_cats = list(range(1, max_cat + 1))
    
    counts = [categories.count(cat) for cat in all_cats]
    labels = [CATEGORY_NAMES.get(cat, f"Cat {cat}") for cat in all_cats]
    
    plt.figure(figsize=(14, 6))
    
    # NEW DISTINCT COLORS
    colors = plt.cm.tab20.colors[:len(all_cats)]
    
    bars = plt.bar(labels, counts, color=colors, edgecolor='black', linewidth=1.5)
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Product Category', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Products Recommended', fontsize=12, fontweight='bold')
    plt.ylim(0, max(counts) + 5)
    
    plt.xticks(rotation=45, ha='right', fontweight='bold')
    
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        if count > 0:
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(count)}\n({count/len(categories)*100:.1f}%)',
                    ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    filename = title.replace(": ", "_").replace(" ", "_").lower() + ".png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"✅ Saved: {filename}")
    plt.close()

def test_one_category(videos_by_category: dict, category: int):
    cat_name = CATEGORY_NAMES.get(category, f"Category {category}")
    print("\n" + "="*70)
    print(f"TEST: Category-Only User ({cat_name})")
    print("="*70)
    print(f"Scenario: User watches 5 videos from the '{cat_name}' category only.")
    print(f"Expected: Warm-up restricts exploitation. '{cat_name}' products will be capped at ~20-30%.\n")
    
    if category not in videos_by_category:
        print(f"❌ Category '{cat_name}' not found in video database")
        return
    
    video_ids = videos_by_category[category][:5]
    for video_id in video_ids:
        save_mock_interaction(create_mock_interaction(video_id=video_id, watch_time_ms=60000, days_ago=0))
    
    recs = product_recommendation(n_recommended=50)
    categories = [int(rec["bucket_num"]) for rec in recs if rec.get("bucket_num") is not None]
    
    plot_histogram(categories, f"Product Test: Cold Start ({cat_name}-Only User)")
    
    target_count = sum(1 for c in categories if c == category)
    print(f"\n📊 Results: {target_count}/50 recommended products from '{cat_name}'")

def test_warmup_scaling(videos_by_category: dict, main_cat: int = 6, other_cats: list = [2, 3, 4]):
    main_name = CATEGORY_NAMES.get(main_cat, f"Category {main_cat}")
    print("\n" + "="*70)
    print(f"TEST: Post-Warmup Scaling ({main_name} + Diversity)")
    print("="*70)
    print(f"Scenario: User watches 15 '{main_name}' videos AND 1 video from 3 other categories.")
    print(f"Expected: The warm-up penalty is lifted (>4 categories). '{main_name}' scales to >80%.\n")
    
    # 15 videos from the main category (e.g. Food)
    for video_id in videos_by_category.get(main_cat, [])[:15]:
        save_mock_interaction(create_mock_interaction(video_id=video_id, watch_time_ms=60000, days_ago=0))
        
    # 1 video each from the 3 other categories
    for cat in other_cats:
        for video_id in videos_by_category.get(cat, [])[:1]:
            save_mock_interaction(create_mock_interaction(video_id=video_id, watch_time_ms=60000, days_ago=0))
            
    recs = product_recommendation(n_recommended=50)
    categories = [int(rec["bucket_num"]) for rec in recs if rec.get("bucket_num") is not None]
    
    plot_histogram(categories, f"Product Test: Post-Warmup ({main_name} Focused)")
    
    target_count = sum(1 for c in categories if c == main_cat)
    print(f"\n📊 Results: {target_count}/50 recommended products from '{main_name}'")

def run_all_tests():
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " PRODUCT RECOMMENDATION TEST SUITE ".center(68) + "║")
    print("╚" + "═"*68 + "╝")
    
    videos_by_category = load_catalog_by_category(VIDEO_PARQUET_DIR, "video_id")
    products_by_category = load_catalog_by_category(PRODUCT_PARQUET_DIR, "product_id")
    
    if not videos_by_category or not products_by_category:
        print("❌ Missing video or product data in database. Cannot run tests.")
        return
    
    plot_database_distribution(videos_by_category, "Database Distribution: Total Videos per Category")
    plot_database_distribution(products_by_category, "Database Distribution: Total Products per Category")
    
    original_download_function = monkey_patch_download_interactions()
    
    try:
        # Actual history test
        test_actual_user_history_products(original_download_function)

        # ---------------------------------------------------------
        # COLD START (Only Food)
        setup_test_environment()
        test_one_category(videos_by_category, category=6)
        
        # POST WARM-UP (Food + Beauty, Electronics, Home)
        setup_test_environment()
        test_warmup_scaling(videos_by_category, main_cat=6, other_cats=[2, 3, 4])
        # ---------------------------------------------------------
        
        # RECENCY BIAS (Beauty Today vs Food 7 Days Ago)
        setup_test_environment()
        test_recency_post_warmup(videos_by_category, old_cat=6, new_cat=2, other_cats=[1, 3, 4])
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED")
        print("="*70)
        
    finally:
        if os.path.exists(TEST_DIR):
            shutil.rmtree(TEST_DIR)
        print(f"\n🧹 Cleaned up test directory: {TEST_DIR}")

if __name__ == "__main__":
    run_all_tests()