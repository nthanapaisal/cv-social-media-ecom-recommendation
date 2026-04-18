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

from backend.src.product_recommendation.personalized_recommendation import (
    product_recommendation,
    _products_recommendation_cache  # Import cache to clear it between tests
)

# Configuration (relative to project root)
TEST_DIR = project_root / "data" / "test_interactions"
VIDEO_PARQUET_DIR = project_root / "data" / "video_parquet"
PRODUCT_PARQUET_DIR = project_root / "data" / "product_parquet"
CACHE_FILE = project_root / ".product_test_cache.pkl"


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
    
    # Determine the range of categories to plot (1 to 13, or higher if data exists)
    max_cat_in_data = max(items_by_category.keys()) if items_by_category else 0
    max_cat = max(total_categories, max_cat_in_data)
    all_cats = list(range(1, max_cat + 1))
    
    # Count the total items available in each category
    counts = [len(items_by_category.get(cat, [])) for cat in all_cats]
    labels = [f"Cat {cat}" for cat in all_cats]
    total_items = sum(counts)
    
    plt.figure(figsize=(14, 6))
    # Using a slightly different color map to distinguish from recommendation plots
    colors = plt.cm.Set3(np.linspace(0, 1, len(all_cats)))
    bars = plt.bar(labels, counts, color=colors, edgecolor='black', linewidth=1.5)
    
    plt.title(title + f" (Total: {total_items})", fontsize=14, fontweight='bold')
    plt.xlabel('Category', fontsize=12, fontweight='bold')
    plt.ylabel('Total Items Available', fontsize=12, fontweight='bold')
    
    # Add 15% padding to the top so labels don't get cut off
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
    plt.show()
def load_catalog_by_category(parquet_dir, id_col) -> dict:
    """
    Load items from a parquet directory and group by category (bucket_num).
    """
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
                    if isinstance(bucket_num, (list, np.ndarray)):
                        categories = bucket_num
                    else:
                        categories = [bucket_num]
                    
                    for cat in categories:
                        cat_id = int(cat) if not isinstance(cat, int) else cat
                        if cat_id not in items_by_category:
                            items_by_category[cat_id] = []
                        items_by_category[cat_id].append(item_id)
        
        except Exception as e:
            pass
            
    return items_by_category


def setup_test_environment():
    """Create fresh test directory and clear product cache"""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR, exist_ok=True)
    
    # Force clear the product recommendation cache
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
    """Monkey-patch the download function to use test directory."""
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
    """Plot category histogram for products"""
    if not categories:
        print("❌ No products recommended to plot")
        return
    
    # Force the x-axis to include categories 1 through 13 (or higher if present)
    max_cat_in_data = max(categories) if categories else 0
    max_cat = max(total_categories, max_cat_in_data)
    all_cats = list(range(1, max_cat + 1))
    
    # Count occurrences, defaulting to 0 for missing categories
    counts = [categories.count(cat) for cat in all_cats]
    labels = [f"Cat {cat}" for cat in all_cats]  # Shortened label to fit 13 bars nicely
    
    # Made the figure slightly wider to accommodate all 13+ bars
    plt.figure(figsize=(14, 6))
    colors = plt.cm.Pastel1(np.linspace(0, 1, len(all_cats)))
    bars = plt.bar(labels, counts, color=colors, edgecolor='black', linewidth=1.5)
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Product Category', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Products Recommended', fontsize=12, fontweight='bold')
    plt.ylim(0, max(counts) + 5)
    
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        # Only print the text if the count is greater than 0 to keep the chart clean
        if count > 0:
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(count)}\n({count/len(categories)*100:.1f}%)',
                    ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    filename = title.replace(": ", "_").replace(" ", "_").lower() + ".png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"✅ Saved: {filename}")
    plt.show()


def test_one_category(videos_by_category: dict, category: int = 5):
    print("\n" + "="*70)
    print(f"TEST 1: Category-Only User (Category {category})")
    print("="*70)
    print(f"Scenario: User watches 5 videos from category {category} only")
    print(f"Expected: ~80% of products from category {category} (due to 80/20 preferred/explore split)\n")
    
    if category not in videos_by_category:
        print(f"❌ Category {category} not found in video database")
        return
    
    video_ids = videos_by_category[category][:5]
    
    for video_id in video_ids:
        interaction = create_mock_interaction(video_id=video_id, watch_time_ms=60000, days_ago=0)
        save_mock_interaction(interaction)
    
    recs = product_recommendation(n_recommended=50)
    categories = [int(rec["bucket_num"]) for rec in recs if rec.get("bucket_num") is not None]
    
    plot_histogram(categories, f"Product Test 1: Category {category}-Only User")
    
    target_count = sum(1 for c in categories if c == category)
    print(f"\n📊 Results: {target_count}/50 recommended products from category {category}")


def test_two_categories_old_and_recent(videos_by_category: dict, old_cat: int = 2, new_cat: int = 5):
    print("\n" + "="*70)
    print(f"TEST 2: Recency Weighting")
    print("="*70)
    print(f"Scenario: 5 videos from cat {old_cat} watched 30 days ago, 5 from cat {new_cat} watched TODAY")
    print(f"Expected: Product Category {new_cat} >> Product Category {old_cat}\n")
    
    for video_id in videos_by_category.get(old_cat, [])[:5]:
        save_mock_interaction(create_mock_interaction(video_id, watch_time_ms=60000, days_ago=30))
        
    for video_id in videos_by_category.get(new_cat, [])[:5]:
        save_mock_interaction(create_mock_interaction(video_id, watch_time_ms=60000, days_ago=0))
    
    recs = product_recommendation(n_recommended=50)
    categories = [int(rec["bucket_num"]) for rec in recs if rec.get("bucket_num") is not None]
    
    plot_histogram(categories, f"Product Test 2: Recency (Cat {old_cat}=30d, Cat {new_cat}=Today)")
    
    old_count = sum(1 for c in categories if c == old_cat)
    new_count = sum(1 for c in categories if c == new_cat)
    print(f"\n📊 Results:\n   Category {old_cat} (30d old): {old_count}/50\n   Category {new_cat} (today): {new_count}/50")


def test_scenario_3_engagement_levels(videos_by_category: dict, fullyWatched: int = 6, skippedQuickly: int = 4):
    print("\n" + "="*70)
    print(f"TEST 3: Engagement Levels")
    print("="*70)
    print(f"Scenario: 5 fully watched videos (Cat {fullyWatched}) vs 5 quickly skipped (Cat {skippedQuickly})")
    print(f"Expected: Product Category {fullyWatched} >> Product Category {skippedQuickly}\n")
    
    for video_id in videos_by_category.get(fullyWatched, [])[:5]:
        save_mock_interaction(create_mock_interaction(video_id, watch_time_ms=60000, watched_50_pct=True, skipped_quickly=False))
        
    for video_id in videos_by_category.get(skippedQuickly, [])[:5]:
        save_mock_interaction(create_mock_interaction(video_id, watch_time_ms=5000, watched_50_pct=False, skipped_quickly=True))
    
    recs = product_recommendation(n_recommended=50)
    categories = [int(rec["bucket_num"]) for rec in recs if rec.get("bucket_num") is not None]
    
    plot_histogram(categories, f"Product Test 3: Engagement (Cat {fullyWatched}=watched, Cat {skippedQuickly}=skipped)")
    
    watched_count = sum(1 for c in categories if c == fullyWatched)
    skipped_count = sum(1 for c in categories if c == skippedQuickly)
    print(f"\n📊 Results:\n   Category {fullyWatched} (watched): {watched_count}/50\n   Category {skippedQuickly} (skipped): {skipped_count}/50")


def test_scenario_4_balanced_watch(videos_by_category: dict):
    print("\n" + "="*70)
    print(f"TEST 4: Balanced Category Distribution")
    print("="*70)
    
    selected_cats = sorted(list(videos_by_category.keys()))[5:12]
    print(f"Scenario: User watches 5 videos evenly across categories: {selected_cats}")
    
    for cat in selected_cats:
        for video_id in videos_by_category.get(cat, [])[:5]:
            save_mock_interaction(create_mock_interaction(video_id, watch_time_ms=50000))
    
    recs = product_recommendation(n_recommended=50)
    categories = [int(rec["bucket_num"]) for rec in recs if rec.get("bucket_num") is not None]
    
    plot_histogram(categories, f"Product Test 4: Balanced Distribution ({selected_cats})")


def test_scenario_5_other_category_distribution(videos_by_category: dict):
    print("\n" + "="*70)
    print(f"TEST 5: 'Other' Category Distribution")
    print("="*70)
    
    other_cat = 13 if 13 in videos_by_category else max(videos_by_category.keys())
    print(f"Scenario: User watches 5 'other' (bucket_num={other_cat}) videos")
    print("Expected: Weight distributed equally across all other product categories\n")
    
    for video_id in videos_by_category.get(other_cat, [])[:5]:
        save_mock_interaction(create_mock_interaction(video_id, watch_time_ms=50000))
    
    recs = product_recommendation(n_recommended=50)
    categories = [int(rec["bucket_num"]) for rec in recs if rec.get("bucket_num") is not None]
    
    plot_histogram(categories, f"Product Test 5: 'Other' Category Distribution")


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
        
        test_actual_user_history_products(original_download_function)


        setup_test_environment()
        test_one_category(videos_by_category, category=5)
        
        
        setup_test_environment()
        test_two_categories_old_and_recent(videos_by_category, old_cat=5, new_cat=2)
        
        
        setup_test_environment()
        test_scenario_3_engagement_levels(videos_by_category)
        
        
        setup_test_environment()
        test_scenario_4_balanced_watch(videos_by_category)
        
        
        setup_test_environment()
        test_scenario_5_other_category_distribution(videos_by_category)
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED")
        print("="*70)
        
    finally:
        if os.path.exists(TEST_DIR):
            shutil.rmtree(TEST_DIR)
        print(f"\n🧹 Cleaned up test directory: {TEST_DIR}")

if __name__ == "__main__":
    run_all_tests()