import requests
import random
from faker import Faker

# API Endpoint
API_URL = "http://13.60.203.173:8000/api/users"  # Change this if running remotely

# Initialize Faker for generating fake user data
fake = Faker()

# Predefined roles
ROLES = ["Manager", "Engineer", "Designer", "Program Manager"]

def create_fake_user():
    """Generate fake user data."""
    return {
        "name": fake.name(),
        "email": fake.email(),
        "role": random.choice(ROLES),
        "picture": fake.image_url(),
        "tenant_id": "STR-SYN-4a225d63"
    }

def insert_users(n=100):
    """Insert `n` users by calling the API."""
    for i in range(n):
        user_data = create_fake_user()
        response = requests.post(API_URL, json=user_data)
        
        if response.status_code == 200:
            print(f"✅ User {i+1} created: {user_data['name']} ({user_data['email']})")
        else:
            print(f"❌ Failed to create user {i+1}: {response.text}")

if __name__ == "__main__":
    insert_users(100)  # Insert 100 users
