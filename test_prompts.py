import os
import sys
from dotenv import load_dotenv

# Try to load .env from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Add ai-service-python to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-service-python'))

from main import PlanRequest, generate_healthcare_plan

prompts = [
    "I need a plan for managing type 2 diabetes.",
    "Insurance for a family of 4 with coverage for dental.",
    "Give me a detailed 5 year plan for cancer recovery.",
    "hello",
    "generate a very complex plan with lots of details",
]

for p in prompts:
    print(f"\n--- Testing prompt: {p} ---")
    try:
        req = PlanRequest(query=p)
        res = generate_healthcare_plan(req)
        print(f"Success! Treatment Plan Length: {len(res.treatment_plan)}")
        print(f"Schedule: {res.schedule[:50]}...")
    except Exception as e:
        print(f"Error for prompt '{p}': {e}")
