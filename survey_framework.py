"""
User Survey & Feedback Collection Framework

Professional approach to collecting user feedback on recommendations.
Includes survey templates and analysis methods.

SERENDIPITY means RELEVANCE (PREFERRED CATEGORY) HERE
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
import json
from pathlib import Path

# Survey data folder
SURVEY_DATA_DIR = Path(__file__).parent / "data" / "surveys"
SURVEY_DATA_DIR.mkdir(exist_ok=True)


@dataclass
class RecommendationSurveyResponse:
    """Single survey response for a recommendation"""
    user_id: str
    recommendation_id: str
    items_shown: List[str]  # Video/product IDs shown
    timestamp: str
    
    # Survey Questions (all required)
    serendipity_rating: int  # 1-5: How relevant were recommendations?
    diversity_rating: int  # 1-5: How diverse were recommendations?
    satisfaction_rating: int  # 1-5: Overall happiness?
    preference_vs_exploration: int  # 1-10: Preferred vs Random exploration?
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON storage"""
        return {
            "user_id": self.user_id,
            "recommendation_id": self.recommendation_id,
            "items_shown": self.items_shown,
            "timestamp": self.timestamp,
            "serendipity_rating": self.serendipity_rating,
            "diversity_rating": self.diversity_rating,
            "satisfaction_rating": self.satisfaction_rating,
            "preference_vs_exploration": self.preference_vs_exploration,
        }


class SurveyCollector:
    """Collect and manage user feedback on recommendations"""
    
    def __init__(self, survey_name: str = "default"):
        self.survey_name = survey_name
        self.survey_file = SURVEY_DATA_DIR / f"{survey_name}_responses.jsonl"
        self.responses: List[RecommendationSurveyResponse] = []
        self.load_existing()
    
    def load_existing(self):
        """Load existing survey responses"""
        if self.survey_file.exists():
            with open(self.survey_file, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    response = RecommendationSurveyResponse(**data)
                    self.responses.append(response)
    
    def add_response(self, response: RecommendationSurveyResponse) -> None:
        """Add a new survey response"""
        self.responses.append(response)
        
        # Append to file
        with open(self.survey_file, 'a') as f:
            f.write(json.dumps(response.to_dict()) + '\n')
    
    def get_summary_stats(self) -> Dict[str, float]:
        """Get summary statistics from responses"""
        if not self.responses:
            return {"satisfaction_percentage": 0, "total_responses": 0}
        
        serendipity_scores = [r.serendipity_rating for r in self.responses if r.serendipity_rating]
        diversity_scores = [r.diversity_rating for r in self.responses if r.diversity_rating]
        satisfaction_scores = [r.satisfaction_rating for r in self.responses if r.satisfaction_rating]
        preference_vs_expl = [r.preference_vs_exploration for r in self.responses if r.preference_vs_exploration]
        
        # Convert satisfaction (1-5) to percentage (0-100%)
        avg_satisfaction_raw = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
        satisfaction_percentage = (avg_satisfaction_raw / 5.0) * 100
        
        # Average preference/exploration rating (1-10 scale)
        avg_pref_vs_expl = sum(preference_vs_expl) / len(preference_vs_expl) if preference_vs_expl else 5.5
        
        stats = {
            "total_responses": len(self.responses),
            "satisfaction_percentage": round(satisfaction_percentage, 1),  # 0-100%
            "avg_satisfaction": round(avg_satisfaction_raw, 2),  # 1-5 scale
            "avg_serendipity": round(sum(serendipity_scores) / len(serendipity_scores), 2) if serendipity_scores else 0,
            "avg_diversity": round(sum(diversity_scores) / len(diversity_scores), 2) if diversity_scores else 0,
            "avg_preference_vs_exploration": round(avg_pref_vs_expl, 2),  # 1-10, where 5.5 is balanced
        }
        
        return stats
    
    def export_to_csv(self, output_path: Optional[str] = None) -> str:
        """Export responses to CSV for analysis"""
        if not self.responses:
            print("No responses to export")
            return ""
        
        data = [r.to_dict() for r in self.responses]
        df = pd.DataFrame(data)
        
        output_path = output_path or SURVEY_DATA_DIR / f"{self.survey_name}_responses.csv"
        df.to_csv(output_path, index=False)
        print(f"Exported {len(df)} responses to {output_path}")
        
        return str(output_path)
    
    def get_satisfaction_trend(self) -> pd.DataFrame:
        """Get satisfaction ratings over time (for line graph)"""
        if not self.responses:
            return pd.DataFrame()
        
        data = []
        for i, resp in enumerate(self.responses, 1):
            data.append({
                "survey_number": i,
                "satisfaction": resp.satisfaction_rating,
                "serendipity": resp.serendipity_rating,
                "diversity": resp.diversity_rating,
                "user_id": resp.user_id,
                "timestamp": resp.timestamp,
            })
        
        return pd.DataFrame(data)
    
    def get_preference_exploration_trend(self) -> pd.DataFrame:
        """Get preference vs exploration trend over time"""
        if not self.responses:
            return pd.DataFrame()
        
        data = []
        for i, resp in enumerate(self.responses, 1):
            # Convert 1-10 scale to more intuitive metric
            # 1-5 = prefers more from preferred categories
            # 5-10 = prefers more exploration
            pref_score = resp.preference_vs_exploration
            data.append({
                "survey_number": i,
                "preference_vs_exploration": pref_score,
                "user_id": resp.user_id,
                "timestamp": resp.timestamp,
            })
        
        return pd.DataFrame(data)
    
    def get_per_user_satisfaction(self) -> Dict[str, float]:
        """Get average satisfaction percentage per user"""
        if not self.responses:
            return {}
        
        user_satisfaction = {}
        for resp in self.responses:
            if resp.user_id not in user_satisfaction:
                user_satisfaction[resp.user_id] = []
            user_satisfaction[resp.user_id].append(resp.satisfaction_rating)
        
        # Convert to percentage
        result = {}
        for user_id, ratings in user_satisfaction.items():
            avg_rating = sum(ratings) / len(ratings)
            avg_percentage = (avg_rating / 5.0) * 100
            result[user_id] = round(avg_percentage, 1)
        
        return result
    
    def get_preference_exploration_preference(self) -> Dict[str, float]:
        """Get average preference vs exploration rating per user"""
        if not self.responses:
            return {}
        
        user_pref_expl = {}
        for resp in self.responses:
            if resp.user_id not in user_pref_expl:
                user_pref_expl[resp.user_id] = []
            user_pref_expl[resp.user_id].append(resp.preference_vs_exploration)
        
        # Average the 1-10 scale
        result = {}
        for user_id, ratings in user_pref_expl.items():
            result[user_id] = round(sum(ratings) / len(ratings), 2)
        
        return result


class SurveyTemplate:
    """Survey templates for different recommendation scenarios"""
    
    @staticmethod
    def get_minimal_survey() -> str:
        """Minimal survey for quick feedback (post-recommendation)"""
        return """
QUICK SURVEY - Your Feedback (30 seconds)

After viewing these recommendations:

1. How relevant were these recommendations to your interests?
   ☐ 1 - Not relevant
   ☐ 2 - Slightly relevant
   ☐ 3 - Moderately relevant
   ☐ 4 - Very relevant
   ☐ 5 - Extremely relevant

2. Would you click on any of these?
   ☐ Yes
   ☐ No

3. Optional: Any feedback?
   [Open text field]
        """
    
    @staticmethod
    def get_full_survey() -> str:
        """Comprehensive survey (post-session)"""
        return """
RECOMMENDATION SYSTEM SURVEY - Your Feedback (5 minutes)

Thank you for using our recommendation system!

SECTION A: RELEVANCE
1. How relevant were today's recommendations to your interests?
   ☐ 1 - Not relevant
   ☐ 2 - Slightly relevant
   ☐ 3 - Moderately relevant
   ☐ 4 - Very relevant
   ☐ 5 - Extremely relevant

2. Did the recommendations match what you're currently interested in?
   ☐ 1 - Not at all
   ☐ 2 - Somewhat
   ☐ 3 - Partially
   ☐ 4 - Mostly
   ☐ 5 - Perfectly

SECTION B: DIVERSITY
3. How diverse were the recommendations?
   ☐ 1 - All same category
   ☐ 2 - Mostly same
   ☐ 3 - Mix of categories
   ☐ 4 - Good variety
   ☐ 5 - Excellent variety

4. Did you find any unexpected/surprising recommendations?
   ☐ 1 - None
   ☐ 2 - Very few
   ☐ 3 - Some
   ☐ 4 - Several
   ☐ 5 - Many delightful surprises

SECTION C: ENGAGEMENT
5. Would you click on any of these recommendations?
   ☐ Definitely yes
   ☐ Probably yes
   ☐ Maybe
   ☐ Probably no
   ☐ Definitely no

6. Overall, how satisfied are you with the recommendations?
   ☐ 1 - Very unsatisfied
   ☐ 2 - Unsatisfied
   ☐ 3 - Neutral
   ☐ 4 - Satisfied
   ☐ 5 - Very satisfied

SECTION D: OPEN FEEDBACK
7. What did you like about these recommendations?
   [Open text field]

8. How could recommendations be improved?
   [Open text field]

9. What categories/topics interest you most?
   [Open text field]
        """
    
    @staticmethod
    def get_ab_test_survey() -> str:
        """A/B test survey (comparing two recommenders)"""
        return """
RECOMMENDER COMPARISON SURVEY

You saw recommendations from TWO different systems.

SYSTEM A (first set):
1. Relevance (1-5): ___
2. Diversity (1-5): ___
3. Would click (Yes/No): ___

SYSTEM B (second set):
4. Relevance (1-5): ___
5. Diversity (1-5): ___
6. Would click (Yes/No): ___

COMPARISON:
7. Which system had better recommendations?
   ☐ System A
   ☐ System B
   ☐ About the same

8. Why did you prefer one system?
   [Open text field]
        """


def create_survey_templates():
    """Create survey template files for reference"""
    templates_dir = SURVEY_DATA_DIR / "templates"
    templates_dir.mkdir(exist_ok=True)
    
    with open(templates_dir / "minimal_survey.txt", 'w') as f:
        f.write(SurveyTemplate.get_minimal_survey())
    
    with open(templates_dir / "full_survey.txt", 'w') as f:
        f.write(SurveyTemplate.get_full_survey())
    
    with open(templates_dir / "ab_test_survey.txt", 'w') as f:
        f.write(SurveyTemplate.get_ab_test_survey())
    
    print(f"Survey templates created in {templates_dir}")


# EXAMPLE: How to use in your frontend
"""
# In your Next.js frontend (after recommendations shown):

async function collectUserFeedback(items: string[], relevanceRating: number) {
    const response = await fetch('/api/surveys', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            items_shown: items,
            relevance_rating: relevanceRating,
            would_click: userClickedAny,
            diversity_rating: diversityScore,  // if user provided
            feedback_text: userComments,
            timestamp: new Date().toISOString(),
        })
    });
    return response.json();
}
"""


if __name__ == "__main__":
    # Create templates
    create_survey_templates()
    
    # Example: Add a test response
    collector = SurveyCollector("test_survey")
    
    response = RecommendationSurveyResponse(
        user_id="user_123",
        recommendation_id="rec_001",
        items_shown=["video_1", "video_2", "video_3"],
        timestamp=datetime.now().isoformat(),
        would_click=True,
        diversity_rating=4,
        serendipity_rating=3,
        satisfaction_rating=4,
        feedback_text="Generally good recommendations",
        improvements="Could show more diverse categories"
    )
    
    collector.add_response(response)
    
    # Print stats
    stats = collector.get_summary_stats()
    print("\nSurvey Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value:.2f}")
