# File: backend/api/constants.py

"""Constants for API endpoints and common string literals"""

class EventTypes:
    """Streaming event type constants"""
    COMPLETE = "complete"
    ERROR_EVENT = "error_event"
    SLIDE_COMPLETED = "slide_completed"
    STATUS = "status"
    PROGRESS = "progress"

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
