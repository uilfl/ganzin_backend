#!/usr/bin/env python3
"""
R5: Adaptation Service  
Rule engine that triggers real-time WebSocket feedback commands
≤200ms end-to-end latency requirement
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class FeedbackCommand:
    """WebSocket feedback command structure"""
    type: str  # 'showHint', 'grammarPopup', 'vocabularyCard', etc.
    payload: Dict[str, Any]
    timestamp: int
    session_id: str

class AdaptationRule:
    """Base class for adaptation rules"""
    
    def __init__(self, rule_id: str, condition: Dict, action: Dict):
        self.rule_id = rule_id
        self.condition = condition
        self.action = action
    
    def evaluate(self, event_data: Dict) -> bool:
        """Evaluate if rule condition is met"""
        try:
            # Check event type
            if 'event_type' in self.condition:
                if event_data.get('event_type') != self.condition['event_type']:
                    return False
            
            # Check duration threshold
            if 'min_duration_ms' in self.condition:
                if event_data.get('duration_ms', 0) < self.condition['min_duration_ms']:
                    return False
            
            # Check AOI type
            if 'aoi_type' in self.condition:
                # Would need to look up AOI details from database
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Rule evaluation error: {e}")
            return False
    
    def create_command(self, event_data: Dict, session_id: str) -> FeedbackCommand:
        """Create feedback command from rule action"""
        return FeedbackCommand(
            type=self.action['type'],
            payload=self.action['payload'],
            timestamp=int(datetime.utcnow().timestamp() * 1000),
            session_id=session_id
        )

class AdaptationEngine:
    """
    R5: Rule engine for real-time adaptive feedback
    Evaluates rules and pushes WebSocket commands
    """
    
    def __init__(self):
        self.rules = []
        self.session_states = {}  # session_id -> state data
        self.websocket_connections = {}  # session_id -> websocket
        self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default adaptation rules based on requirements"""
        
        # R7: Vocabulary assistance rule (>1.5s fixation on unknown word)
        vocab_rule = AdaptationRule(
            rule_id="vocabulary_assistance",
            condition={
                "event_type": "fixation",
                "min_duration_ms": 1500,  # >1.5s fixation
                "aoi_type": "word"
            },
            action={
                "type": "vocabularyCard",
                "payload": {
                    "message": "Unknown word detected",
                    "show_definition": True,
                    "show_pronunciation": True
                }
            }
        )
        
        # R8: Grammar assistance rule (complex sentence stalling)
        grammar_rule = AdaptationRule(
            rule_id="grammar_assistance", 
            condition={
                "event_type": "fixation",
                "min_duration_ms": 2000,  # >2s stalling
                "aoi_type": "sentence"
            },
            action={
                "type": "grammarPopup",
                "payload": {
                    "message": "Complex sentence detected",
                    "show_grammar_help": True,
                    "show_translation": True
                }
            }
        )
        
        # General hint rule for extended fixations
        hint_rule = AdaptationRule(
            rule_id="general_hint",
            condition={
                "event_type": "fixation", 
                "min_duration_ms": 3000  # >3s fixation
            },
            action={
                "type": "showHint",
                "payload": {
                    "message": "Need help with this section?",
                    "hint_type": "reading_assistance"
                }
            }
        )
        
        self.rules = [vocab_rule, grammar_rule, hint_rule]
        logger.info(f"Loaded {len(self.rules)} adaptation rules")
    
    def register_websocket(self, session_id: str, websocket):
        """Register WebSocket connection for feedback"""
        self.websocket_connections[session_id] = websocket
        self.session_states[session_id] = {
            'last_feedback_time': 0,
            'feedback_count': 0,
            'fixation_history': []
        }
        logger.info(f"Registered WebSocket for session {session_id}")
    
    def unregister_websocket(self, session_id: str):
        """Unregister WebSocket connection"""
        if session_id in self.websocket_connections:
            del self.websocket_connections[session_id]
        if session_id in self.session_states:
            del self.session_states[session_id]
        logger.info(f"Unregistered WebSocket for session {session_id}")
    
    async def process_event(self, event_data: Dict) -> List[FeedbackCommand]:
        """
        R5: Process gaze event and trigger feedback
        End-to-end latency ≤200ms
        """
        session_id = event_data.get('session_id')
        if not session_id:
            return []
        
        commands = []
        current_time = int(datetime.utcnow().timestamp() * 1000)
        
        # Update session state
        if session_id in self.session_states:
            state = self.session_states[session_id]
            
            # Rate limiting: max 1 feedback per 5 seconds
            if current_time - state['last_feedback_time'] < 5000:
                return []
            
            # Track fixation history for pattern detection
            if event_data.get('event_type') == 'fixation':
                state['fixation_history'].append({
                    'timestamp': current_time,
                    'duration_ms': event_data.get('duration_ms', 0),
                    'aoi_id': event_data.get('aoi_id')
                })
                
                # Keep only last 10 fixations
                state['fixation_history'] = state['fixation_history'][-10:]
        
        # Evaluate rules
        for rule in self.rules:
            try:
                if rule.evaluate(event_data):
                    # Check for word difficulty (R7 requirement)
                    if rule.rule_id == "vocabulary_assistance":
                        aoi_id = event_data.get('aoi_id')
                        if aoi_id and await self._is_difficult_word(aoi_id):
                            command = rule.create_command(event_data, session_id)
                            command.payload['word_id'] = aoi_id
                            commands.append(command)
                    
                    # Check for sentence complexity (R8 requirement)
                    elif rule.rule_id == "grammar_assistance":
                        if await self._is_complex_sentence(event_data):
                            command = rule.create_command(event_data, session_id)
                            commands.append(command)
                    
                    # General feedback
                    else:
                        command = rule.create_command(event_data, session_id)
                        commands.append(command)
                        
            except Exception as e:
                logger.error(f"Rule {rule.rule_id} evaluation error: {e}")
        
        # Send feedback via WebSocket
        for command in commands:
            await self._send_feedback(command)
            
            # Update session state
            if session_id in self.session_states:
                state = self.session_states[session_id]
                state['last_feedback_time'] = current_time
                state['feedback_count'] += 1
        
        return commands
    
    async def _is_difficult_word(self, aoi_id: str) -> bool:
        """R7: Check if word is difficult/unknown (NLP frequency analysis)"""
        # Simplified implementation - in production, use NLP service
        # This would query word frequency databases or NLP models
        difficult_words = ['sophisticated', 'comprehension', 'articulate', 'endeavor']
        return any(word in aoi_id.lower() for word in difficult_words)
    
    async def _is_complex_sentence(self, event_data: Dict) -> bool:
        """R8: Detect complex sentence structure"""
        # Simplified implementation - in production, use NLP complexity analysis
        # This would analyze sentence structure, length, grammatical complexity
        duration_ms = event_data.get('duration_ms', 0)
        return duration_ms > 2000  # >2s indicates complexity/confusion
    
    async def _send_feedback(self, command: FeedbackCommand):
        """Send feedback command via WebSocket"""
        session_id = command.session_id
        
        if session_id not in self.websocket_connections:
            logger.warning(f"No WebSocket connection for session {session_id}")
            return
        
        websocket = self.websocket_connections[session_id]
        
        try:
            # R5: JSON schema validation
            feedback_message = {
                "type": "feedback",
                "command": {
                    "type": command.type,
                    "payload": command.payload,
                    "timestamp": command.timestamp
                }
            }
            
            await websocket.send_text(json.dumps(feedback_message))
            logger.info(f"Sent {command.type} feedback to session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to send feedback to session {session_id}: {e}")
            # Remove broken connection
            self.unregister_websocket(session_id)

class MockAdaptationService:
    """Mock adaptation service for testing"""
    
    def __init__(self):
        self.feedback_count = 0
    
    async def process_event(self, event_data: Dict) -> List[Dict]:
        """Mock feedback generation"""
        if event_data.get('event_type') == 'fixation' and event_data.get('duration_ms', 0) > 1500:
            self.feedback_count += 1
            return [{
                'type': 'vocabularyCard',
                'payload': {'word': 'example', 'definition': 'mock definition'},
                'timestamp': int(datetime.utcnow().timestamp() * 1000)
            }]
        return []

# Global adaptation engine instance
adaptation_engine = AdaptationEngine()

def get_adaptation_service():
    """Get adaptation service instance"""
    return adaptation_engine

async def init_adaptation_service():
    """Initialize adaptation service"""
    logger.info("Adaptation service initialized")
    return adaptation_engine