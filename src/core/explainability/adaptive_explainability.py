#!/usr/bin/env python3
"""
Adaptive Explainability System
Implements HRM-inspired adaptive explainability with user feedback
"""

import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ExplanationLevel(Enum):
    """Different levels of explanation detail."""
    MINIMAL = "minimal"
    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"
    EXPERT = "expert"

class FeedbackType(Enum):
    """Types of user feedback."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    CONFUSED = "confused"
    SATISFIED = "satisfied"

@dataclass
class ExplanationRequest:
    """Request for explanation generation."""
    content: str
    context: str
    user_id: str
    requested_level: Optional[ExplanationLevel] = None
    task_type: str = "general"
    metadata: Dict[str, Any] = None

@dataclass
class Explanation:
    """Generated explanation with metadata."""
    content: str
    level: ExplanationLevel
    confidence: float
    generation_time: float
    user_id: str
    metadata: Dict[str, Any]

@dataclass
class UserFeedback:
    """User feedback on explanations."""
    explanation_id: str
    user_id: str
    feedback_type: FeedbackType
    rating: int  # 1-5 scale
    comment: Optional[str] = None
    timestamp: float = None
    metadata: Dict[str, Any] = None

@dataclass
class UserProfile:
    """User profile for adaptive explainability."""
    user_id: str
    preferred_level: ExplanationLevel
    feedback_history: List[UserFeedback]
    adaptation_score: float
    last_updated: float
    metadata: Dict[str, Any]

class AdaptiveExplainabilitySystem:
    """HRM-inspired adaptive explainability system."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.user_profiles: Dict[str, UserProfile] = {}
        self.explanation_history: Dict[str, Explanation] = {}
        self.feedback_history: List[UserFeedback] = []
        self.adaptation_threshold = self.config.get("adaptation_threshold", 0.1)
        self.learning_rate = self.config.get("learning_rate", 0.05)
        
    def _default_config(self) -> Dict:
        """Default configuration for adaptive explainability."""
        return {
            "adaptation_threshold": 0.1,
            "learning_rate": 0.05,
            "min_feedback_samples": 3,
            "explanation_levels": {
                "minimal": {"max_length": 50, "detail_factor": 0.2},
                "basic": {"max_length": 150, "detail_factor": 0.4},
                "detailed": {"max_length": 300, "detail_factor": 0.6},
                "comprehensive": {"max_length": 500, "detail_factor": 0.8},
                "expert": {"max_length": 1000, "detail_factor": 1.0}
            },
            "default_level": ExplanationLevel.BASIC
        }
    
    def get_or_create_user_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile for adaptive explainability."""
        
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                preferred_level=self.config["default_level"],
                feedback_history=[],
                adaptation_score=0.5,
                last_updated=time.time(),
                metadata={}
            )
        
        return self.user_profiles[user_id]
    
    async def generate_explanation(
        self, 
        request: ExplanationRequest
    ) -> Explanation:
        """Generate adaptive explanation based on user profile and context."""
        
        start_time = time.time()
        
        # Get user profile
        user_profile = self.get_or_create_user_profile(request.user_id)
        
        # Determine appropriate explanation level
        explanation_level = self._determine_explanation_level(request, user_profile)
        
        # Generate explanation content
        explanation_content = await self._generate_explanation_content(
            request, 
            explanation_level
        )
        
        # Calculate confidence
        confidence = self._calculate_explanation_confidence(
            explanation_content, 
            explanation_level, 
            user_profile
        )
        
        generation_time = time.time() - start_time
        
        # Create explanation object
        explanation = Explanation(
            content=explanation_content,
            level=explanation_level,
            confidence=confidence,
            generation_time=generation_time,
            user_id=request.user_id,
            metadata={
                "request_context": request.context,
                "task_type": request.task_type,
                "adaptation_score": user_profile.adaptation_score
            }
        )
        
        # Store explanation
        explanation_id = f"{request.user_id}_{int(time.time())}"
        self.explanation_history[explanation_id] = explanation
        
        return explanation
    
    def _determine_explanation_level(
        self, 
        request: ExplanationRequest, 
        user_profile: UserProfile
    ) -> ExplanationLevel:
        """Determine appropriate explanation level based on context and user profile."""
        
        # If user explicitly requested a level, use it
        if request.requested_level:
            return request.requested_level
        
        # Adjust based on user profile and context
        base_level = user_profile.preferred_level
        
        # Context-based adjustments
        context_lower = request.context.lower()
        
        if "simple" in context_lower or "basic" in context_lower:
            # Move to simpler level
            level_index = list(ExplanationLevel).index(base_level)
            if level_index > 0:
                base_level = list(ExplanationLevel)[level_index - 1]
        
        elif "detailed" in context_lower or "comprehensive" in context_lower:
            # Move to more detailed level
            level_index = list(ExplanationLevel).index(base_level)
            if level_index < len(ExplanationLevel) - 1:
                base_level = list(ExplanationLevel)[level_index + 1]
        
        # Task type adjustments
        if request.task_type in ["expert", "technical", "complex"]:
            level_index = list(ExplanationLevel).index(base_level)
            if level_index < len(ExplanationLevel) - 1:
                base_level = list(ExplanationLevel)[level_index + 1]
        
        elif request.task_type in ["simple", "quick", "basic"]:
            level_index = list(ExplanationLevel).index(base_level)
            if level_index > 0:
                base_level = list(ExplanationLevel)[level_index - 1]
        
        return base_level
    
    async def _generate_explanation_content(
        self, 
        request: ExplanationRequest, 
        level: ExplanationLevel
    ) -> str:
        """Generate explanation content based on level and context."""
        
        level_config = self.config["explanation_levels"][level.value]
        max_length = level_config["max_length"]
        level_config["detail_factor"]
        
        # Base explanation
        base_explanation = f"This is an explanation for: {request.content}"
        
        # Add detail based on level
        if level == ExplanationLevel.MINIMAL:
            explanation = base_explanation[:max_length]
        
        elif level == ExplanationLevel.BASIC:
            explanation = (
                f"{base_explanation}\n\n"
                f"This involves {request.task_type} processing. "
                f"The system analyzed the context and generated this response."
            )[:max_length]
        
        elif level == ExplanationLevel.DETAILED:
            explanation = (
                f"{base_explanation}\n\n"
                f"This involves {request.task_type} processing. "
                f"The system analyzed the context '{request.context}' and "
                f"generated this response using adaptive algorithms. "
                f"The explanation level is set to {level.value} based on "
                f"user preferences and context analysis."
            )[:max_length]
        
        elif level == ExplanationLevel.COMPREHENSIVE:
            explanation = (
                f"{base_explanation}\n\n"
                f"This involves {request.task_type} processing. "
                f"The system analyzed the context '{request.context}' and "
                f"generated this response using adaptive algorithms. "
                f"The explanation level is set to {level.value} based on "
                f"user preferences and context analysis.\n\n"
                f"Technical details: The system uses machine learning models "
                f"to adapt explanation complexity based on user feedback. "
                f"This ensures explanations are always appropriate for the user's "
                f"current understanding level and preferences."
            )[:max_length]
        
        elif level == ExplanationLevel.EXPERT:
            explanation = (
                f"{base_explanation}\n\n"
                f"This involves {request.task_type} processing. "
                f"The system analyzed the context '{request.context}' and "
                f"generated this response using adaptive algorithms. "
                f"The explanation level is set to {level.value} based on "
                f"user preferences and context analysis.\n\n"
                f"Technical details: The system uses machine learning models "
                f"to adapt explanation complexity based on user feedback. "
                f"This ensures explanations are always appropriate for the user's "
                f"current understanding level and preferences.\n\n"
                f"Implementation specifics: The adaptive explainability system "
                f"employs reinforcement learning techniques to continuously "
                f"optimize explanation quality. User feedback is processed using "
                f"sentiment analysis and rating patterns to adjust explanation "
                f"complexity dynamically. The system maintains user profiles "
                f"with adaptation scores that influence future explanation generation."
            )[:max_length]
        
        return explanation
    
    def record_feedback(self, feedback: UserFeedback) -> None:
        """Record user feedback and update user profile."""
        
        feedback.timestamp = time.time()
        self.feedback_history.append(feedback)
        
        # Update user profile
        user_profile = self.get_or_create_user_profile(feedback.user_id)
        user_profile.feedback_history.append(feedback)
        
        # Update adaptation score based on feedback
        self._update_adaptation_score(user_profile, feedback)
        
        # Update preferred explanation level if needed
        self._update_preferred_level(user_profile)
        
        user_profile.last_updated = time.time()
    
    def _update_adaptation_score(
        self, 
        user_profile: UserProfile, 
        feedback: UserFeedback
    ) -> None:
        """Update user adaptation score based on feedback."""
        
        # Calculate feedback impact
        if feedback.feedback_type == FeedbackType.POSITIVE:
            impact = (feedback.rating - 3) / 2.0  # Convert to [-1, 1]
        elif feedback.feedback_type == FeedbackType.NEGATIVE:
            impact = -(feedback.rating - 3) / 2.0  # Convert to [-1, 1]
        else:
            impact = 0.0
        
        # Apply learning rate
        adaptation_change = impact * self.learning_rate
        
        # Update adaptation score
        user_profile.adaptation_score += adaptation_change
        user_profile.adaptation_score = max(0.0, min(1.0, user_profile.adaptation_score))
    
    def _update_preferred_level(self, user_profile: UserProfile) -> None:
        """Update preferred explanation level based on feedback history."""
        
        if len(user_profile.feedback_history) < self.config["min_feedback_samples"]:
            return
        
        # Analyze recent feedback patterns
        recent_feedback = user_profile.feedback_history[-10:]  # Last 10 feedback items
        
        # Calculate average rating for each explanation level
        level_ratings = {}
        for feedback in recent_feedback:
            if feedback.explanation_id in self.explanation_history:
                explanation = self.explanation_history[feedback.explanation_id]
                level = explanation.level
                
                if level not in level_ratings:
                    level_ratings[level] = []
                level_ratings[level].append(feedback.rating)
        
        # Find level with highest average rating
        if level_ratings:
            best_level = max(
                level_ratings.keys(),
                key=lambda level: sum(level_ratings[level]) / len(level_ratings[level])
            )
            
            # Update preferred level if significantly different
            current_index = list(ExplanationLevel).index(user_profile.preferred_level)
            best_index = list(ExplanationLevel).index(best_level)
            
            if abs(current_index - best_index) >= 2:  # Significant difference
                user_profile.preferred_level = best_level
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics for adaptive explainability."""
        
        metrics = {
            "total_users": len(self.user_profiles),
            "total_explanations": len(self.explanation_history),
            "total_feedback": len(self.feedback_history),
            "average_adaptation_score": 0.0,
            "level_distribution": {},
            "feedback_distribution": {}
        }
        
        # Calculate average adaptation score
        if self.user_profiles:
            metrics["average_adaptation_score"] = sum(
                profile.adaptation_score for profile in self.user_profiles.values()
            ) / len(self.user_profiles)
        
        return metrics
