from enum import Enum
import enum

class Status(str, Enum):
    COMPLETE = "Complete"
    ON_TRACK = "On Track"
    AT_RISK = "At Risk" 
    BLOCKED = "Blocked"
    COMPLETED = "Completed"

class DependencyStatus(enum.Enum):
    ACTIVE = "Active"        
    BLOCKED = "Blocked"     
    COMPLETED = "Completed" 
    CANCELLED = "Cancelled"  
    FAILED = "Failed"    

class HealthStatus(enum.Enum):
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    OFF_TRACK = "off_track"
    CANCELED = "canceled"
    COMPLETED = "completed"
    BACKLOG = "backlog"
