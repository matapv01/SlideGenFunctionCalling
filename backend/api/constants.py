# File: backend/api/constants.py

"""Constants for API endpoints and common string literals"""

class EventTypes:
    """Streaming event type constants"""
    COMPLETE = "complete"
    ERROR_EVENT = "error_event"
    SLIDE_COMPLETED = "slide_completed"
    STATUS = "status"
    PROGRESS = "progress"

class SourceTypes:
    """Project source type constants"""
    DOCX = "docx"
    IDEA = "idea"
    MANUAL_STRUCTURE = "manual_structure"

class FilePatterns:
    """Common file naming patterns"""
    IDEA_SESSION = "idea_{}.json"
    APPROVED_STRUCTURE = "approved_structure_{}.json"

class ContentLengths:
    """Content length option constants"""
    BRIEF = "brief"
    STANDARD = "standard"
    DETAILED = "detailed"
    EXTENSIVE = "extensive"

class SlideTypes:
    """Slide type constants"""
    INTRO = "intro"
    CONTENT = "content"
    TRANSITION = "transition"
    THANK_YOU = "thank_you"

class RateLimitConfig:
    """Rate limiting configuration constants"""
    IDEA_STRUCTURE_MAX_REQUESTS = 100  # Increased for testing
    IDEA_STRUCTURE_WINDOW = 300  # 5 minutes
    IDEA_STREAM_MAX_REQUESTS = 50  # Increased for testing
    IDEA_STREAM_WINDOW = 600  # 10 minutes
    CLEANUP_INTERVAL = 60  # 1 minute

class EndpointNames:
    """Rate limiting endpoint name constants"""
    IDEA_STRUCTURE = "idea_structure"
    IDEA_STREAM = "idea_stream"