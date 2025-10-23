"""
Inspection data model.

Simple dataclass for representing inspection entities.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Inspection:
    """
    Inspection entity model.
    
    Represents an inspection with basic details like ID, status, dates, etc.
    """
    id: Optional[str] = None
    title: str = ""
    description: str = ""
    status: str = "pending"
    inspector: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    findings: Optional[str] = None
    
    def is_completed(self) -> bool:
        """Check if inspection is completed."""
        return self.status == "completed"
    
    def is_pending(self) -> bool:
        """Check if inspection is pending."""
        return self.status == "pending"
    
    def is_in_progress(self) -> bool:
        """Check if inspection is in progress."""
        return self.status == "in_progress"
