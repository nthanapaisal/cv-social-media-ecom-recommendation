
"""
Recommendation System Testing & Validation Script

Tests the recommendation engine with REAL mock user interactions using actual video IDs.
Generates histograms to visualize category distribution.
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
    video_recommendation,
    product_recommendation,
)

# Configuration (relative to project root)
TEST_DIR = project_root / "data" / "test_interactions"
VIDEO_PARQUET_DIR = project_root / "data" / "video_parquet"
CACHE_FILE = project_root / ".video_cache.pkl"


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

def load_videos_by_category() -> dict:
    """
    Load all videos from video_parquet_dir and group by category (bucket_num).
    Uses cached pickle file if available to save computation.
    
    Returns:
        dict: {category_id: [list of video_ids]}
    """
    # Check if cached version exists
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'rb') as f:
                videos_by_category = pickle.load(f)
                print(f"✅ Loaded videos from cache: {CACHE_FILE}")
                for cat_id, vids in sorted(videos_by_category.items()):
                    print(f"   Category {cat_id}: {len(vids)} videos")
                print()
                return videos_by_category
        except Exception as e:
            print(f"⚠️  Could not load cache: {e}. Rebuilding...\n")
    
    # Load from scratch if cache doesn't exist
    if not os.path.exists(VIDEO_PARQUET_DIR):
        print(f"❌ Error: {VIDEO_PARQUET_DIR} not found")
        return {}
    
    videos_by_category = {}
    
    for filename in os.listdir(VIDEO_PARQUET_DIR):
        if not filename.endswith(".parquet"):
            continue
        
        filepath = os.path.join(VIDEO_PARQUET_DIR, filename)
        try:
            df = pd.read_parquet(filepath)
            
            for _, row in df.iterrows():
                video_id = row.get("video_id")
                bucket_num = row.get("bucket_num")
                
                if video_id and bucket_num:
                    # bucket_num might be a list or single value
                    if isinstance(bucket_num, (list, np.ndarray)):
                        categories = bucket_num
                    else:
                        categories = [bucket_num]
                    
                    for cat in categories:
                        cat_id = int(cat) if not isinstance(cat, int) else cat
                        if cat_id not in videos_by_category:
                            videos_by_category[cat_id] = []
                        videos_by_category[cat_id].append(video_id)
        
        except Exception as e:
            print(f"Warning: Could not read {filename}: {e}")
    
    # Save to cache
    try:
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(videos_by_category, f)
        print(f"✅ Saved videos to cache: {CACHE_FILE}")
    except Exception as e:
        print(f"⚠️  Could not save cache: {e}")
    
    print(f"✅ Loaded videos by category:")
    for cat_id, vids in sorted(videos_by_category.items()):
        print(f"   Category {cat_id}: {len(vids)} videos")
    print()
    
    return videos_by_category

def create_mock_interaction(
    video_id: str,
    watch_time_ms: int = 45000,
    skipped_quickly: bool = False,
    watched_50_pct: bool = True,
    days_ago: int = 0,
) -> dict:
    """Create a mock user interaction"""
    timestamp = datetime.now() - timedelta(days=days_ago)
    
    return {
        "video_id": video_id,
        "watch_time_ms": watch_time_ms,
        "skipped_quickly": skipped_quickly,
        "watched_50_pct": watched_50_pct,
        "interaction_timestamp": timestamp.isoformat(),
    }


def save_mock_interaction(interaction: dict):
    """Save mock interaction to test directory"""
    df = pd.DataFrame([interaction])
    os.makedirs(TEST_DIR, exist_ok=True)
    
    file_key = f"{interaction['video_id']}-{int(datetime.now().timestamp() * 1000000)}"
    out_path = os.path.join(TEST_DIR, f"part-{file_key}.parquet")
    df.to_parquet(out_path, engine="pyarrow", index=False)
    
    return out_path


def setup_test_directory():
    """Create fresh test directory"""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR, exist_ok=True)
    print(f"✅ Created test directory: {TEST_DIR}\n")


def monkey_patch_download_interactions():
    """Monkey-patch the download function to use test directory - must patch both modules!"""
    from backend.src.database import db_utils
    import backend.src.product_recommendation.personalized_recommendation as rec_module
    
    original_download = db_utils.download_user_interactions
    
    def test_download():
        """Load interactions from test directory"""
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

def test_one_category(videos_by_category: dict, category: int = 6):
    """
    Test 1: User watches ONLY one category
    Expected: Recommendations heavily weighted toward that category
    """
    print("\n" + "="*70)
    print(f"TEST 1: Category-Only User (Category {category})")
    print("="*70)
    print(f"Scenario: User watches 5 videos from category {category} only")
    print(f"Expected: 70%+ of recommendations should be from category {category}\n")
    
    if category not in videos_by_category:
        print(f"❌ Category {category} not found in video database")
        return
    
    # Get real video IDs from the category - only use first 5 to leave some unwatched
    video_ids = videos_by_category[category][:5]
    
    print(f"Using video IDs: {video_ids}\n")
    
    # Create interactions
    for video_id in video_ids:
        interaction = create_mock_interaction(
            video_id=video_id,
            watch_time_ms=60000,
            watched_50_pct=True,
            days_ago=0
        )
        save_mock_interaction(interaction)
    
    # Get recommendations
    recs = video_recommendation(n_recommended=50)
    
    # Extract categories
    categories = [rec["bucket_num"][0] if isinstance(rec["bucket_num"], list) else rec["bucket_num"] 
                  for rec in recs if rec.get("bucket_num")]
    
    plot_histogram(categories, f"Test 1: Category {category}-Only User")
    
    # Analysis
    target_count = sum(1 for c in categories if c == category)
    print(f"\n📊 Results: {target_count}/50 recommendations from category {category}")
    if target_count >= 35:
        print(f"✅ PASS: Category {category} dominates ({target_count/50*100:.1f}%)")
    else:
        print(f"⚠️  Category {category} represents {target_count/50*100:.1f}% (expected 70%+)")


def test_two_categories_old_and_recent(videos_by_category: dict, old_cat: int = 12, new_cat: int = 11):
    """
    Test 2: Recency Weighting
    User watched old_cat 30 days ago, new_cat today
    Expected: new_cat should appear more frequently than old_cat
    """
    print("\n" + "="*70)
    print(f"TEST 2: Recency Weighting")
    print("="*70)
    print(f"Scenario:")
    print(f"  - 5 videos from category {old_cat} watched 30 days ago")
    print(f"  - 5 videos from category {new_cat} watched TODAY")
    print(f"Expected: Category {new_cat} videos > Category {old_cat} videos\n")
    
    if old_cat not in videos_by_category or new_cat not in videos_by_category:
        print(f"❌ One or both categories not found")
        return
    
    # Old interactions (30 days ago) - only 5 videos
    old_videos = videos_by_category[old_cat][:5]
    for video_id in old_videos:
        interaction = create_mock_interaction(
            video_id=video_id,
            watch_time_ms=60000,
            watched_50_pct=True,
            days_ago=30
        )
        save_mock_interaction(interaction)
    
    # Recent interactions (today) - only 5 videos
    new_videos = videos_by_category[new_cat][:5]
    for video_id in new_videos:
        interaction = create_mock_interaction(
            video_id=video_id,
            watch_time_ms=60000,
            watched_50_pct=True,
            days_ago=0
        )
        save_mock_interaction(interaction)
    
    recs = video_recommendation(n_recommended=50)
    categories = [rec["bucket_num"][0] if isinstance(rec["bucket_num"], list) else rec["bucket_num"] 
                  for rec in recs if rec.get("bucket_num")]
    
    plot_histogram(categories, f"Test 2: Recency Weighting (Cat {old_cat}=30d ago, Cat {new_cat}=today)")
    
    # Analysis
    old_count = sum(1 for c in categories if c == old_cat)
    new_count = sum(1 for c in categories if c == new_cat)
    print(f"\n📊 Results:")
    print(f"   Category {old_cat} (30d old):  {old_count}/50")
    print(f"   Category {new_cat} (today):   {new_count}/50")
    if new_count > old_count:
        print(f"✅ PASS: Recency weighting working! {new_cat}({new_count}) > {old_cat}({old_count})")
    else:
        print(f"❌ FAIL: {old_cat}({old_count}) >= {new_cat}({new_count})")


def test_scenario_3_engagement_levels(videos_by_category: dict, fullyWatched: int = 7, skippedQuickly: int = 5):
    """
    Test 3: Engagement Levels
    Compare skip/watched behavior impact
    """
    print("\n" + "="*70)
    print(f"TEST 3: Engagement Levels")
    print("="*70)
    print(f"Scenario:")
    print(f"  - 5 videos from category {fullyWatched}: fully watched (watched_50_pct=True)")
    print(f"  - 5 videos from category {skippedQuickly}: skipped quickly (skipped_quickly=True)")
    print(f"Expected: Category {fullyWatched} videos >> Category {skippedQuickly} videos\n")
    
    if fullyWatched not in videos_by_category or skippedQuickly not in videos_by_category:
        print(f"❌ One or both categories not found")
        return
    
    # Fully watched
    watched_videos = videos_by_category[fullyWatched][:5]
    for video_id in watched_videos:
        interaction = create_mock_interaction(
            video_id=video_id,
            watch_time_ms=60000,
            watched_50_pct=True,
            skipped_quickly=False,
            days_ago=0
        )
        save_mock_interaction(interaction)
    
    # Skipped videos
    skipped_videos = videos_by_category[skippedQuickly][:5]
    for video_id in skipped_videos:
        interaction = create_mock_interaction(
            video_id=video_id,
            watch_time_ms=5000,
            watched_50_pct=False,
            skipped_quickly=True,
            days_ago=0
        )
        save_mock_interaction(interaction)
    
    recs = video_recommendation(n_recommended=50)
    categories = [rec["bucket_num"][0] if isinstance(rec["bucket_num"], list) else rec["bucket_num"] 
                  for rec in recs if rec.get("bucket_num")]
    
    plot_histogram(categories, f"Test 3: Engagement (Cat {fullyWatched}=watched, Cat {skippedQuickly}=skipped)")
    
    # Analysis
    watched_count = sum(1 for c in categories if c == fullyWatched)
    skipped_count = sum(1 for c in categories if c == skippedQuickly)
    print(f"\n📊 Results:")
    print(f"   Category {fullyWatched} (watched): {watched_count}/50")
    print(f"   Category {skippedQuickly} (skipped): {skipped_count}/50")
    if watched_count > skipped_count:
        print(f"✅ PASS: Engagement weighting working! {fullyWatched}({watched_count}) > {skippedQuickly}({skipped_count})")
    else:
        print(f"❌ FAIL: Engagement not working")


def test_scenario_4_balanced_watch(videos_by_category: dict):
    """
    Test 4: Balanced Watch History
    User watches equal amounts across multiple categories
    Expected: Roughly equal distribution in recommendations
    """
    print("\n" + "="*70)
    print(f"TEST 4: Balanced Category Distribution")
    print("="*70)
    print(f"Scenario: User watches 5 videos in each of 4 different categories")
    print(f"Expected: Roughly 25% each category in recommendations\n")
    
    # Select 4 categories
    selected_cats = sorted(list(videos_by_category.keys()))[3:12]
    
    if len(selected_cats) < 3:
        print(f"❌ Not enough categories in database (found {len(selected_cats)}, need 3)")
        return
    
    print(f"Using categories: {selected_cats}\n")
    
    # Watch 4 videos from each category
    for cat in selected_cats:
        cat_videos = videos_by_category[cat][:4]
        for video_id in cat_videos:
            interaction = create_mock_interaction(
                video_id=video_id,
                watch_time_ms=50000,
                watched_50_pct=True,
                days_ago=0
            )
            save_mock_interaction(interaction)
    
    recs = video_recommendation(n_recommended=50)
    categories = [rec["bucket_num"][0] if isinstance(rec["bucket_num"], list) else rec["bucket_num"] 
                  for rec in recs if rec.get("bucket_num")]
    
    plot_histogram(categories, f"Test 4: Balanced Distribution (Categories {selected_cats})")
    
    # Analysis
    print(f"\n📊 Results:")
    for cat in selected_cats:
        count = sum(1 for c in categories if c == cat)
        pct = (count / len(categories)) * 100
        print(f"   Category {cat}: {count:2}/50 ({pct:5.1f}%)")


def test_scenario_5_other_category_distribution(videos_by_category: dict):
    """
    Test 5: "Other" Category Distribution
    When user watches "other" videos (bucket_num=13), weight should be distributed
    """
    print("\n" + "="*70)
    print(f"TEST 5: 'Other' Category Distribution")
    print("="*70)
    print(f"Scenario:")
    print(f"  - User watches 5 'other' (bucket_num=13) videos")
    print(f"  - Expected: Weight distributed equally across all other categories\n")
    
    # Try to use category 13 if it exists
    if 13 in videos_by_category:
        other_videos = videos_by_category[13][:5]
        print(f"Using category 13 (other) videos\n")
    else:
        print(f"⚠️  Category 13 not found, using category {max(videos_by_category.keys())} instead\n")
        cat = max(videos_by_category.keys())
        other_videos = videos_by_category[cat][:5]
    
    # Create interactions
    for video_id in other_videos:
        interaction = create_mock_interaction(
            video_id=video_id,
            watch_time_ms=50000,
            watched_50_pct=True,
            days_ago=0
        )
        save_mock_interaction(interaction)
    
    recs = video_recommendation(n_recommended=50)
    categories = [rec["bucket_num"][0] if isinstance(rec["bucket_num"], list) else rec["bucket_num"] 
                  for rec in recs if rec.get("bucket_num")]
    
    plot_histogram(categories, f"Test 5: 'Other' Category Distribution")


def clear_cache():
    """Clear the cached videos data"""
    if os.path.exists(CACHE_FILE):
        try:
            os.remove(CACHE_FILE)
            print(f"✅ Cleared cache: {CACHE_FILE}")
        except Exception as e:
            print(f"❌ Error clearing cache: {e}")
    else:
        print(f"ℹ️  No cache file found: {CACHE_FILE}")


def run_all_tests():
    """Run all test scenarios"""
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " RECOMMENDATION SYSTEM TEST SUITE ".center(68) + "║")
    print("╚" + "═"*68 + "╝")
    
    # Load videos by category (uses cache if available)
    videos_by_category = load_videos_by_category()
    
    if not videos_by_category:
        print("❌ No videos found in database. Cannot run tests.")
        return
    
    plot_database_distribution(videos_by_category, "Database Distribution: Total Videos per Category")
    # Setup
    setup_test_directory()
    monkey_patch_download_interactions()
    
    try:
        # Test 1 - Use category 5 (168 videos) instead of 1 (10 videos) for better variety
        test_one_category(videos_by_category)
        
        
        # Test 2 - Use categories with more videos
        setup_test_directory()
        test_two_categories_old_and_recent(videos_by_category)
        
        
        # Test 3
        setup_test_directory()
        test_scenario_3_engagement_levels(videos_by_category)
        
        
        # Test 4
        setup_test_directory()
        test_scenario_4_balanced_watch(videos_by_category)
        
        
        # Test 5
        setup_test_directory()
        test_scenario_5_other_category_distribution(videos_by_category)
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED")
        print("="*70)
        
    finally:
        # Cleanup
        if os.path.exists(TEST_DIR):
            shutil.rmtree(TEST_DIR)
        print(f"\n🧹 Cleaned up test directory: {TEST_DIR}")


if __name__ == "__main__":
    # Allow clearing cache via command line argument
    if len(sys.argv) > 1 and sys.argv[1] == "--clear-cache":
        clear_cache()
        sys.exit(0)
    
    run_all_tests()

