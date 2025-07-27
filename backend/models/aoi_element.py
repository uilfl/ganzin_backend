#!/usr/bin/env python3
"""
AOI (Area of Interest) Element data model
Based on frontend integration testing and vocabulary discovery insights
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Any
import time

@dataclass
class AOIElement:
    """
    Area of Interest element for gaze hit detection
    Based on frontend testing with vocabulary words and interactive content
    """
    # Basic AOI Properties
    id: str  # Unique identifier (e.g., "word_1", "biodiversity", "main_text")
    x: float  # Top-left X coordinate in pixels
    y: float  # Top-left Y coordinate in pixels  
    width: float  # Width in pixels
    height: float  # Height in pixels
    
    # Content Properties
    text: str  # Display text content
    tag: str = "span"  # HTML tag type (span, div, p, button, etc.)
    
    # Interaction Properties
    interactive: bool = True  # Whether this AOI triggers interactions
    vocabulary_word: bool = False  # Whether this is a vocabulary target
    difficulty_level: str = "medium"  # easy, medium, hard, expert
    
    # Metadata
    created_at: float = None  # Creation timestamp
    lesson_context: Optional[str] = None  # Associated lesson or content area
    
    def __post_init__(self):
        """Initialize default values after creation"""
        if self.created_at is None:
            self.created_at = time.time()
    
    @classmethod
    def create_vocabulary_word(cls, word_id: str, text: str, x: float, y: float, 
                              width: float, height: float, difficulty: str = "medium") -> 'AOIElement':
        """
        Create an AOI element for vocabulary words
        
        Args:
            word_id: Unique word identifier
            text: The vocabulary word
            x, y, width, height: Bounding box coordinates
            difficulty: Word difficulty level
        
        Returns:
            AOIElement configured for vocabulary interaction
        """
        return cls(
            id=word_id,
            x=x, y=y, width=width, height=height,
            text=text,
            tag="span",
            interactive=True,
            vocabulary_word=True,
            difficulty_level=difficulty,
            lesson_context="vocabulary_discovery"
        )
    
    @classmethod
    def create_content_area(cls, area_id: str, text: str, x: float, y: float,
                           width: float, height: float, tag: str = "div") -> 'AOIElement':
        """
        Create an AOI element for content areas (paragraphs, sections, etc.)
        
        Args:
            area_id: Unique area identifier
            text: Content description
            x, y, width, height: Bounding box coordinates
            tag: HTML tag type
        
        Returns:
            AOIElement configured for content tracking
        """
        return cls(
            id=area_id,
            x=x, y=y, width=width, height=height,
            text=text,
            tag=tag,
            interactive=False,
            vocabulary_word=False,
            lesson_context="content_reading"
        )
    
    @classmethod
    def from_frontend_aoi(cls, frontend_data: dict) -> 'AOIElement':
        """
        Create AOI element from frontend AOI data
        
        Args:
            frontend_data: Dictionary from frontend AOI detection
        
        Returns:
            AOIElement instance
        """
        return cls(
            id=frontend_data.get("id", "unknown"),
            x=float(frontend_data.get("x", 0)),
            y=float(frontend_data.get("y", 0)),
            width=float(frontend_data.get("width", 100)),
            height=float(frontend_data.get("height", 20)),
            text=frontend_data.get("text", ""),
            tag=frontend_data.get("tag", "span"),
            interactive=frontend_data.get("interactive", True),
            vocabulary_word=frontend_data.get("vocabulary_word", False),
            difficulty_level=frontend_data.get("difficulty_level", "medium")
        )
    
    def contains_point(self, x: float, y: float) -> bool:
        """
        Check if a point (gaze coordinate) is within this AOI
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Returns:
            True if point is within AOI bounds
        """
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def get_center_point(self) -> tuple[float, float]:
        """Get the center point of this AOI"""
        center_x = self.x + (self.width / 2)
        center_y = self.y + (self.height / 2)
        return center_x, center_y
    
    def get_bounding_box(self) -> dict:
        """Get bounding box coordinates"""
        return {
            "top_left": (self.x, self.y),
            "top_right": (self.x + self.width, self.y),
            "bottom_left": (self.x, self.y + self.height),
            "bottom_right": (self.x + self.width, self.y + self.height)
        }
    
    def expand_bounds(self, padding: float = 5.0) -> 'AOIElement':
        """
        Create expanded version of this AOI with padding
        
        Args:
            padding: Pixels to expand in all directions
        
        Returns:
            New AOIElement with expanded bounds
        """
        return AOIElement(
            id=f"{self.id}_expanded",
            x=max(0, self.x - padding),
            y=max(0, self.y - padding),
            width=self.width + (2 * padding),
            height=self.height + (2 * padding),
            text=self.text,
            tag=self.tag,
            interactive=self.interactive,
            vocabulary_word=self.vocabulary_word,
            difficulty_level=self.difficulty_level,
            lesson_context=self.lesson_context
        )
    
    def to_frontend_format(self) -> dict:
        """
        Convert to frontend-compatible format
        
        Returns:
            Dictionary suitable for frontend AOI systems
        """
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "text": self.text,
            "tag": self.tag,
            "interactive": self.interactive,
            "vocabulary_word": self.vocabulary_word,
            "difficulty_level": self.difficulty_level
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class AOICollection:
    """
    Collection manager for multiple AOI elements
    Based on lessons learned from vocabulary discovery testing
    """
    
    def __init__(self):
        self.elements: Dict[str, AOIElement] = {}
        self.vocabulary_words: List[AOIElement] = []
        self.content_areas: List[AOIElement] = []
    
    def add_element(self, aoi: AOIElement) -> None:
        """Add AOI element to collection"""
        self.elements[aoi.id] = aoi
        
        if aoi.vocabulary_word:
            self.vocabulary_words.append(aoi)
        else:
            self.content_areas.append(aoi)
    
    def remove_element(self, aoi_id: str) -> Optional[AOIElement]:
        """Remove AOI element by ID"""
        if aoi_id in self.elements:
            removed = self.elements.pop(aoi_id)
            
            # Remove from specialized lists
            if removed in self.vocabulary_words:
                self.vocabulary_words.remove(removed)
            if removed in self.content_areas:
                self.content_areas.remove(removed)
                
            return removed
        return None
    
    def find_hit(self, x: float, y: float) -> Optional[AOIElement]:
        """
        Find which AOI element (if any) contains the given point
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Returns:
            AOIElement that contains the point, or None
        """
        # Prioritize vocabulary words for hit detection
        for aoi in self.vocabulary_words:
            if aoi.contains_point(x, y):
                return aoi
        
        # Check content areas
        for aoi in self.content_areas:
            if aoi.contains_point(x, y):
                return aoi
        
        return None
    
    def get_vocabulary_words(self) -> List[AOIElement]:
        """Get all vocabulary word AOIs"""
        return self.vocabulary_words.copy()
    
    def get_content_areas(self) -> List[AOIElement]:
        """Get all content area AOIs"""
        return self.content_areas.copy()
    
    def to_frontend_format(self) -> List[dict]:
        """Convert entire collection to frontend format"""
        return [aoi.to_frontend_format() for aoi in self.elements.values()]
    
    def create_standard_lesson_aois(self, center_x: float = 756, center_y: float = 491) -> None:
        """
        Create standard set of AOIs for lesson content
        Based on testing insights and vocabulary discovery patterns
        
        Args:
            center_x: Screen center X coordinate
            center_y: Screen center Y coordinate
        """
        # Environmental Science vocabulary
        vocab_words = [
            ("biodiversity", center_x-200, center_y-100, 100, 20, "hard"),
            ("ecosystem", center_x-50, center_y-100, 80, 20, "medium"),
            ("conservation", center_x+50, center_y-100, 110, 20, "medium"),
            ("sustainable", center_x-100, center_y-70, 90, 20, "medium"),
            
            # Technology vocabulary  
            ("unprecedented", center_x-150, center_y-40, 120, 20, "hard"),
            ("trajectory", center_x, center_y-40, 85, 20, "medium"),
            ("artificial", center_x-200, center_y, 80, 20, "medium"),
            ("algorithm", center_x-100, center_y, 85, 20, "hard"),
            
            # Basic test words
            ("challenging", center_x-165, center_y+50, 80, 20, "medium"),
            ("vocabulary", center_x-80, center_y+50, 75, 20, "easy")
        ]
        
        for word, x, y, w, h, difficulty in vocab_words:
            aoi = AOIElement.create_vocabulary_word(word, word, x, y, w, h, difficulty)
            self.add_element(aoi)
        
        # Content areas
        content_areas = [
            ("main_text", "Main reading content", center_x-250, center_y-25, 500, 50, "p"),
            ("lesson_content", "Lesson area", center_x-300, center_y-150, 600, 300, "div"),
            ("instructions", "Reading instructions", center_x-200, center_y+100, 400, 30, "div")
        ]
        
        for area_id, text, x, y, w, h, tag in content_areas:
            aoi = AOIElement.create_content_area(area_id, text, x, y, w, h, tag)
            self.add_element(aoi)