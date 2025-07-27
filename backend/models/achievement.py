#!/usr/bin/env python3
"""
Achievement data model and logic
Following your decision: 後端統一維護與存檔（資料可信），前端只負責展示通知
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
import time

@dataclass
class Achievement:
    """
    Achievement definition and tracking
    Backend maintains authoritative achievement state
    """
    id: str  # Unique achievement ID
    title: str  # Display title
    description: str  # Achievement description
    category: str  # "vocabulary", "focus", "reading", "session"
    
    # Requirements
    target_value: float  # Target value to achieve
    current_value: float = 0.0  # Current progress
    
    # State
    unlocked: bool = False
    unlocked_at: Optional[float] = None  # Timestamp when unlocked
    
    # Metadata
    icon: str = "🏆"  # Display icon
    points: int = 10  # Achievement points value
    created_at: float = None  # Creation timestamp
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
    
    def update_progress(self, new_value: float) -> bool:
        """
        Update achievement progress
        
        Args:
            new_value: New progress value
        
        Returns:
            True if achievement was just unlocked
        """
        self.current_value = new_value
        
        # Check if achievement should be unlocked
        if not self.unlocked and self.current_value >= self.target_value:
            self.unlocked = True
            self.unlocked_at = time.time()
            return True  # Just unlocked!
        
        return False
    
    def get_progress_percentage(self) -> float:
        """Get progress as percentage (0-100)"""
        if self.target_value <= 0:
            return 100.0 if self.unlocked else 0.0
        
        return min(100.0, (self.current_value / self.target_value) * 100.0)
    
    def to_frontend_format(self) -> dict:
        """Convert to frontend notification format"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "icon": self.icon,
            "points": self.points,
            "progress": self.get_progress_percentage(),
            "unlocked": self.unlocked,
            "unlocked_at": int(self.unlocked_at * 1000) if self.unlocked_at else None,
            "current_value": self.current_value,
            "target_value": self.target_value
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return asdict(self)

class AchievementManager:
    """
    Backend achievement system manager
    Authoritative source for achievement state and logic
    """
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id
        self.achievements: Dict[str, Achievement] = {}
        self.recent_unlocks: List[Achievement] = []
        
        # Initialize standard achievements
        self._create_standard_achievements()
    
    def _create_standard_achievements(self):
        """Create standard set of achievements"""
        
        # Vocabulary achievements
        vocab_achievements = [
            ("first_word", "First Discovery", "Discover your first vocabulary word", "vocabulary", 1, "📚"),
            ("vocab_explorer", "Word Explorer", "Discover 5 vocabulary words", "vocabulary", 5, "🔍"),
            ("vocab_master", "Vocabulary Master", "Discover 10 vocabulary words", "vocabulary", 10, "🎓"),
            ("vocab_genius", "Word Genius", "Discover 20 vocabulary words", "vocabulary", 20, "🧠")
        ]
        
        for achievement_id, title, desc, category, target, icon in vocab_achievements:
            self.achievements[achievement_id] = Achievement(
                id=achievement_id,
                title=title,
                description=desc,
                category=category,
                target_value=target,
                icon=icon,
                points=target * 5  # 5 points per word
            )
        
        # Focus achievements
        focus_achievements = [
            ("focused_reader", "Focused Reader", "Maintain focus for 2 minutes", "focus", 120, "🎯"),
            ("deep_focus", "Deep Focus", "Maintain focus for 5 minutes", "focus", 300, "🧘"),
            ("laser_focus", "Laser Focus", "Maintain focus for 10 minutes", "focus", 600, "⚡"),
        ]
        
        for achievement_id, title, desc, category, target, icon in focus_achievements:
            self.achievements[achievement_id] = Achievement(
                id=achievement_id,
                title=title,
                description=desc,
                category=category,
                target_value=target,
                icon=icon,
                points=int(target / 10)  # Points based on duration
            )
        
        # Reading achievements
        reading_achievements = [
            ("speed_reader", "Speed Reader", "Read 100 words per minute", "reading", 100, "💨"),
            ("comprehension_king", "Comprehension King", "Complete reading with 90% accuracy", "reading", 90, "👑"),
            ("session_complete", "Session Complete", "Complete a full reading session", "session", 1, "✅")
        ]
        
        for achievement_id, title, desc, category, target, icon in reading_achievements:
            self.achievements[achievement_id] = Achievement(
                id=achievement_id,
                title=title,
                description=desc,
                category=category,
                target_value=target,
                icon=icon,
                points=25  # Standard points for reading achievements
            )
    
    def update_vocabulary_progress(self, vocabulary_count: int) -> List[Achievement]:
        """
        Update vocabulary-related achievements
        
        Args:
            vocabulary_count: Current vocabulary discoveries count
        
        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked = []
        
        vocab_achievement_ids = ["first_word", "vocab_explorer", "vocab_master", "vocab_genius"]
        
        for achievement_id in vocab_achievement_ids:
            if achievement_id in self.achievements:
                achievement = self.achievements[achievement_id]
                if achievement.update_progress(vocabulary_count):
                    newly_unlocked.append(achievement)
                    self.recent_unlocks.append(achievement)
                    print(f"🏆 Achievement unlocked: {achievement.title}")
        
        return newly_unlocked
    
    def update_focus_progress(self, session_duration_seconds: float) -> List[Achievement]:
        """
        Update focus-related achievements
        
        Args:
            session_duration_seconds: Current session duration
        
        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked = []
        
        focus_achievement_ids = ["focused_reader", "deep_focus", "laser_focus"]
        
        for achievement_id in focus_achievement_ids:
            if achievement_id in self.achievements:
                achievement = self.achievements[achievement_id]
                if achievement.update_progress(session_duration_seconds):
                    newly_unlocked.append(achievement)
                    self.recent_unlocks.append(achievement)
                    print(f"🏆 Achievement unlocked: {achievement.title}")
        
        return newly_unlocked
    
    def update_reading_progress(self, words_per_minute: float, completion_percentage: float) -> List[Achievement]:
        """
        Update reading-related achievements
        
        Args:
            words_per_minute: Reading speed
            completion_percentage: Session completion percentage
        
        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked = []
        
        # Speed reading achievement
        if "speed_reader" in self.achievements:
            achievement = self.achievements["speed_reader"]
            if achievement.update_progress(words_per_minute):
                newly_unlocked.append(achievement)
                self.recent_unlocks.append(achievement)
        
        # Session completion achievement
        if "session_complete" in self.achievements and completion_percentage >= 90:
            achievement = self.achievements["session_complete"]
            if achievement.update_progress(1):
                newly_unlocked.append(achievement)
                self.recent_unlocks.append(achievement)
        
        return newly_unlocked
    
    def get_recent_unlocks(self, limit: int = 3) -> List[Achievement]:
        """Get recently unlocked achievements for frontend notification"""
        return self.recent_unlocks[-limit:] if self.recent_unlocks else []
    
    def get_all_achievements(self) -> List[Achievement]:
        """Get all achievements with current progress"""
        return list(self.achievements.values())
    
    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get only unlocked achievements"""
        return [a for a in self.achievements.values() if a.unlocked]
    
    def get_total_points(self) -> int:
        """Get total points earned"""
        return sum(a.points for a in self.achievements.values() if a.unlocked)
    
    def to_frontend_format(self) -> dict:
        """Convert entire achievement system to frontend format"""
        return {
            "recent_unlocks": [a.to_frontend_format() for a in self.get_recent_unlocks()],
            "all_achievements": [a.to_frontend_format() for a in self.get_all_achievements()],
            "total_unlocked": len(self.get_unlocked_achievements()),
            "total_points": self.get_total_points(),
            "session_id": self.session_id
        }
    
    def export_session_achievements(self) -> dict:
        """Export achievements for session data"""
        return {
            "achievements_unlocked": [a.to_dict() for a in self.get_unlocked_achievements()],
            "total_points_earned": self.get_total_points(),
            "session_unlocks": [a.to_dict() for a in self.recent_unlocks],
            "export_timestamp": time.time()
        }