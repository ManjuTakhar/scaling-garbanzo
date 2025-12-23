import requests
import random
import json

# ✅ API Endpoints
BASE_URL = "http://13.60.203.173:8000/api"
GET_USERS_URL = f"{BASE_URL}/users"
CREATE_TEAM_URL = f"{BASE_URL}/teams"

# ✅ Step 1: Fetch Users
print("Fetching all users...")
response = requests.get(GET_USERS_URL)

if response.status_code != 200:
    print(f"❌ Failed to fetch users. Status Code: {response.status_code}")
    exit()

users = response.json()
user_ids = [user["user_id"] for user in users]

if len(user_ids) < 15:
    print("❌ Not enough users to distribute into 15 teams.")
    exit()

# ✅ Step 2: Create 15 Teams (Distribute Users)
random.shuffle(user_ids)  # Shuffle users for randomness
teams = [user_ids[i::15] for i in range(15)]  # Divide users into 15 groups

team_names = [
    "Alpha Team", "Beta Squad", "Gamma Force", "Delta Crew", "Echo Warriors",
    "Zeta League", "Sigma Titans", "Omega Champions", "Apex Hunters", "Nova Strikers",
    "Thunder Wolves", "Shadow Rangers", "Iron Legion", "Phoenix Knights", "Vortex Elites"
]

# ✅ Step 3: Create Teams via API
print("\nCreating 15 teams...\n")
for i, team_users in enumerate(teams):
    team_data = {
        "name": team_names[i],
        "user_ids": team_users,
        "tenant_id": "STR-SYN-4a225d63"
    }
    response = requests.post(CREATE_TEAM_URL, json=team_data)

    if response.status_code == 200 or response.status_code == 201:
        print(f"✅ Created Team: {team_names[i]} with {len(team_users)} members")
    else:
        print(f"❌ Failed to create team {team_names[i]}. Status: {response.status_code}")
        print("Response:", response.text)

print("\n🚀 All teams created successfully!")
