from datetime import datetime
from typing import Optional

def datetime_to_epoch(dt: Optional[datetime]) -> Optional[int]:
    """Convert a datetime object to an epoch timestamp."""
    if dt is None:
        return None
    return int(dt.timestamp())

def epoch_to_datetime(epoch: Optional[int]) -> Optional[datetime]:
    """Convert an epoch timestamp to a datetime object."""
    if epoch is None:
        return None
    return datetime.fromtimestamp(epoch)

# Example usage
if __name__ == "__main__":
    now = datetime.utcnow()
    epoch_time = datetime_to_epoch(now)
    print(f"Current datetime: {now}, Epoch time: {epoch_time}")

    converted_back = epoch_to_datetime(epoch_time)
    print(f"Converted back to datetime: {converted_back}")