import uuid
import random
import string

def generate_custom_id(title: str) -> str:
    words = title.split()
    initials = ''.join(word[0].upper() for word in words if word.isalnum())[:3]
    alphanumeric = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"{initials}-{alphanumeric}"