import random
import string
from sqlalchemy import text
import re
from datetime import datetime
from typing import Optional, Union

def get_team_initials(team_name: str) -> str:
    """Extract the first three characters of the team name."""
    return team_name[:3].upper()

def generate_id(name: str) -> str:
    """Generate a URL-friendly ID from a name."""
    cleaned_name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    words = cleaned_name.split()
    initials = ''.join(word[:3].upper() for word in words)
    initials = initials[:6]
    alphanumeric = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"{initials}-{alphanumeric}"

def utc_timestamp_sql() -> text:
    """Generate SQL expression for UTC Unix timestamp."""
    return text("EXTRACT(EPOCH FROM TIMEZONE('UTC', CURRENT_TIMESTAMP))::INTEGER")

def unix_to_datetime(timestamp: Optional[Union[int, datetime]]) -> Optional[datetime]:
    """Convert Unix timestamp to datetime object."""
    if timestamp is None:
        return None
    if isinstance(timestamp, datetime):
        return timestamp
    return datetime.fromtimestamp(timestamp)

def datetime_to_unix(dt: Optional[Union[int, datetime]]) -> Optional[int]:
    """Convert datetime to Unix timestamp."""
    if dt is None:
        return None
    if isinstance(dt, int):
        return dt
    return int(dt.timestamp())

def generate_alphanumeric_id(length=10):
    """Generate a random alphanumeric string."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_display_id(team_name: str, sequence_number: int) -> str:
    """Generate a display ID for an issue."""
    initials = get_team_initials(team_name)
    return f"{initials}-{sequence_number}"


