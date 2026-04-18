"""
Simple Recommendation System Evaluation Dashboard

Shows:
1. Overall satisfaction percentage
2. Satisfaction trend over time (line graph)
3. Preference vs Exploration trend (user wants more preferred items or more random)
4. Per-user satisfaction comparison
5. Preference/exploration preferences by user
"""

import sys
from pathlib import Path
import logging
from datetime import datetime
import json

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from survey_framework import SurveyCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_header(title: str, char: str = "="):
    """Print formatted section header"""
    width = 70
    padding = (width - len(title) - 2) // 2
    print(f"\n{char * width}")
    print(f"{char} {title.center(width - 4)} {char}")
    print(f"{char * width}\n")


def print_metric(name: str, value: float, unit: str = ""):
    """Print a formatted metric"""
    print(f"  {name:.<45} {value:>8.1f} {unit}")


def display_overall_stats():
    """Display overall system statistics"""
    print_header("OVERALL SYSTEM SATISFACTION", "─")

    collector = SurveyCollector("production")

    if not collector.responses:
        print("  ⚠️  No survey responses collected yet.")
        print("  Start watching videos or browsing products and submit surveys.\n")
        return None

    stats = collector.get_summary_stats()

    print(f"  Total Responses: {stats['total_responses']}")
    print(f"\n  📊 Key Metrics:")
    print_metric("Overall Satisfaction", stats["satisfaction_percentage"], "%")
    print_metric("Avg Satisfaction (1-5)", stats["avg_satisfaction"], "")
    print_metric("Avg Relevance (1-5)", stats["avg_serendipity"], "")
    print_metric("Avg Diversity (1-5)", stats["avg_diversity"], "")
    print_metric("Preference-Exploration", stats["avg_preference_vs_exploration"], "(1=prefer, 10=explore)")

    # Interpretation
    print("\n  📋 Interpretation:")
    sat = stats["satisfaction_percentage"]
    if sat >= 80:
        print(f"    ✅ EXCELLENT - {sat}% satisfaction (users very happy)")
    elif sat >= 60:
        print(f"    ⚠️  GOOD - {sat}% satisfaction (acceptable, room to improve)")
    elif sat >= 40:
        print(f"    ⚠️  FAIR - {sat}% satisfaction (needs improvement)")
    else:
        print(f"    ❌ POOR - {sat}% satisfaction (significant issues)")

    pref_expl = stats["avg_preference_vs_exploration"]
    if pref_expl < 4:
        print("    👁️  Users prefer more recommendations from their favorite categories")
    elif pref_expl > 7:
        print("    🎲 Users prefer more random exploration and new discoveries")
    else:
        print("    ⚖️  Users are satisfied with the balance of preferred vs new items")

    return collector


def plot_satisfaction_trend(collector: SurveyCollector):
    """Plot satisfaction trend over time"""
    print_header("PLOTTING SATISFACTION TREND", "─")

    satisfaction_df = collector.get_satisfaction_trend()
    if satisfaction_df.empty:
        print("  ⚠️  Not enough data to plot trends.\n")
        return

    # Group by user
    users = satisfaction_df["user_id"].unique()

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Recommendation System Trends Over Time", fontsize=16, fontweight="bold")

    # Plot 1: Satisfaction over time (per user)
    ax = axes[0, 0]
    for user_id in users:
        user_data = satisfaction_df[satisfaction_df["user_id"] == user_id]
        ax.plot(
            user_data["survey_number"],
            user_data["satisfaction"],
            marker="o",
            label=f"User {user_id[:4]}...",
            linewidth=2,
            markersize=6,
        )
    ax.set_xlabel("Survey #", fontweight="bold")
    ax.set_ylabel("User overall satisfaction", fontweight="bold", fontsize=10)
    ax.set_title("Satisfaction Trend")
    ax.set_ylim(0.5, 5.5)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    ax.set_xticks(range(1, len(satisfaction_df) + 1, max(1, len(satisfaction_df) // 10)))

    # Plot 2: Relevance trend
    ax = axes[0, 1]
    for user_id in users:
        user_data = satisfaction_df[satisfaction_df["user_id"] == user_id]
        ax.plot(
            user_data["survey_number"],
            user_data["serendipity"],
            marker="s",
            label=f"User {user_id[:4]}...",
            linewidth=2,
            markersize=6,
        )
    ax.set_xlabel("Survey #", fontweight="bold")
    ax.set_ylabel("User predicted relevance", fontweight="bold", fontsize=10)
    ax.set_title("How relevant are the recommendations to your interests?")
    ax.set_ylim(0.5, 5.5)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    ax.set_xticks(range(1, len(satisfaction_df) + 1, max(1, len(satisfaction_df) // 10)))

    # Plot 3: Diversity trend
    ax = axes[1, 0]
    for user_id in users:
        user_data = satisfaction_df[satisfaction_df["user_id"] == user_id]
        ax.plot(
            user_data["survey_number"],
            user_data["diversity"],
            marker="^",
            label=f"User {user_id[:4]}...",
            linewidth=2,
            markersize=6,
        )
    ax.set_xlabel("Survey #", fontweight="bold")
    ax.set_ylabel("User predicted diversity", fontweight="bold", fontsize=10)
    ax.set_title("How diverse / exploratory are these recommendations?")
    ax.set_ylim(0.5, 5.5)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    ax.set_xticks(range(1, len(satisfaction_df) + 1, max(1, len(satisfaction_df) // 10)))

    # Plot 4: Moving average of satisfaction (smoothed)
    ax = axes[1, 1]
    for user_id in users:
        user_data = satisfaction_df[satisfaction_df["user_id"] == user_id].copy()
        # 3-point moving average
        user_data["satisfaction_ma"] = user_data["satisfaction"].rolling(window=3, center=True).mean()
        ax.plot(
            user_data["survey_number"],
            user_data["satisfaction_ma"],
            marker="D",
            label=f"User {user_id[:4]}...",
            linewidth=2,
            markersize=6,
        )
    ax.set_xlabel("Survey #", fontweight="bold")
    ax.set_ylabel("Satisfaction (smooth)", fontweight="bold")
    ax.set_title("Smoothed Satisfaction Trend (3-point MA)")
    ax.set_ylim(0.5, 5.5)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    ax.set_xticks(range(1, len(satisfaction_df) + 1, max(1, len(satisfaction_df) // 10)))

    plt.tight_layout()
    plt.savefig("survey_trends.png", dpi=150, bbox_inches="tight")
    print(f"  ✅ Saved: survey_trends.png\n")
    plt.close()


def plot_preference_exploration(collector: SurveyCollector):
    """Plot preference vs exploration trend"""
    print_header("PLOTTING PREFERENCE VS EXPLORATION TREND", "─")

    pref_expl_df = collector.get_preference_exploration_trend()
    if pref_expl_df.empty:
        print("  ⚠️  Not enough data to plot preference trends.\n")
        return

    users = pref_expl_df["user_id"].unique()

    fig, ax = plt.subplots(figsize=(12, 6))

    for user_id in users:
        user_data = pref_expl_df[pref_expl_df["user_id"] == user_id]
        ax.plot(
            user_data["survey_number"],
            user_data["preference_vs_exploration"],
            marker="o",
            label=f"User {user_id[:4]}...",
            linewidth=2.5,
            markersize=8,
        )

    # Add reference lines
    ax.axhline(y=5.5, color="gray", linestyle="--", alpha=0.5, label="Balanced (5.5)")
    ax.axhspan(1, 5.5, alpha=0.1, color="blue", label="Prefers Preferred Items")
    ax.axhspan(5.5, 10, alpha=0.1, color="orange", label="Prefers Exploration")

    ax.set_xlabel("Survey #", fontweight="bold")
    ax.set_ylabel("Preference ← (1 to 10) → Exploration", fontweight="bold")
    ax.set_title("User Preference for New vs Recommended Categories Over Time", fontweight="bold", fontsize=12)
    ax.set_ylim(0.5, 10.5)
    ax.set_yticks([1, 2, 3, 4, 5, 5.5, 6, 7, 8, 9, 10])
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best", fontsize=9)
    ax.set_xticks(range(1, len(pref_expl_df) + 1, max(1, len(pref_expl_df) // 10)))

    plt.tight_layout()
    plt.savefig("preference_exploration_trend.png", dpi=150, bbox_inches="tight")
    print(f"  ✅ Saved: preference_exploration_trend.png\n")
    plt.close()


def display_per_user_summary(collector: SurveyCollector):
    """Display per-user summary statistics"""
    print_header("PER-USER SUMMARY", "─")

    user_satisfaction = collector.get_per_user_satisfaction()
    user_pref_expl = collector.get_preference_exploration_preference()

    if not user_satisfaction:
        print("  ⚠️  No user data available.\n")
        return

    print(f"  {'User ID':<20} {'Satisfaction':<15} {'Preference-Exploration':<20}")
    print("  " + "─" * 55)

    for user_id in sorted(user_satisfaction.keys()):
        sat = user_satisfaction[user_id]
        pref = user_pref_expl.get(user_id, 5.5)

        # Emoji based on satisfaction
        if sat >= 80:
            sat_emoji = "✅"
        elif sat >= 60:
            sat_emoji = "⚠️ "
        else:
            sat_emoji = "❌"

        # Emoji based on preference
        if pref < 4:
            pref_emoji = "📚"
        elif pref > 7:
            pref_emoji = "🎲"
        else:
            pref_emoji = "⚖️ "

        print(f"  {user_id:<20} {sat_emoji} {sat:>6.1f}%        {pref_emoji} {pref:>6.2f}/10")

    print()


def generate_report():
    """Generate complete evaluation report"""
    print("\n" * 2)
    print("╔" + "═" * 68 + "╗")
    print("║" + " RECOMMENDATION SYSTEM EVALUATION DASHBOARD (SIMPLIFIED) ".center(68) + "║")
    print("║" + f" Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")

    # Display overall stats
    collector = display_overall_stats()

    if collector and collector.responses:
        # Plot trends
        plot_satisfaction_trend(collector)
        plot_preference_exploration(collector)

        # Per-user summary
        display_per_user_summary(collector)

    # Recommendations
    print_header("NEXT STEPS", "─")
    print("""
  1️⃣  COLLECT MORE DATA:
     • Aim for 20+ surveys to see trends
     • Watch videos and browse products
     • Submit surveys to build statistical significance
     
  2️⃣  MONITOR TRENDS:
     • Check satisfaction_trends.png for overall satisfaction
     • Check preference_exploration_trend.png to see if users want:
       - More from their preferred categories (low scores ~1-3)
       - More random exploration (high scores ~7-10)
       - A balanced mix (scores ~5-6)
     
  3️⃣  INTERPRET SATISFACTION:
     • 80%+  = Excellent - System is working great
     • 60-79% = Good - Minor improvements needed
     • 40-59% = Fair - Significant improvement needed
     • <40%  = Poor - Major issues to address
     
  4️⃣  INTERPRETATION FOR PREFERENCE DATA:
     • Score 1-3: User wants to see mostly their preferred categories
     • Score 5-6: User is happy with current balance
     • Score 7-10: User wants to discover new categories/items
     
  5️⃣  EXPORT DATA:
     >>> from recommendation_evaluation.survey_framework import SurveyCollector
     >>> collector = SurveyCollector("production")
     >>> collector.export_to_csv()
     
  📊 GENERATED FILES:
     - survey_trends.png: Shows satisfaction, serendipity, diversity over time
     - preference_exploration_trend.png: Shows balance of recommended vs exploratory items
""")

    print_header("DATA LOCATION", "─")
    print("""
  Survey responses stored in: data/surveys/production_responses.jsonl
  Each line is one user survey response (JSON format)
  
  To view raw data:
  >>> cat data/surveys/production_responses.jsonl | python -m json.tool
""")


if __name__ == "__main__":
    generate_report()
