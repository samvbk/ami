# backend/test_medical.py
import google.generativeai as genai
from config import config
from gemini_simple import get_health_response, detect_emotion

print("🩺 Testing A.M.I. Medical Responses")
print("="*50)

# Configure Gemini
genai.configure(api_key=config.GEMINI_API_KEY)

# Test different scenarios
test_cases = [
    ("Hi there!", "John", "Son"),
    ("I have fever, what should I do?", "Priya", "Daughter"),
    ("My head is hurting", "Raj", "Father"),
    ("I have stomach pain", "Meera", "Mother"),
    ("Emergency! I cut my finger and it's bleeding!", "Arun", "Son"),
    ("Just feeling lonely today", "Sneha", "Grandmother"),
    ("What medicine for cough?", "Rohan", "Brother"),
]

print(f"🔑 Using API key: {config.GEMINI_API_KEY[:12]}...")
print(f"🤖 Model: gemini-2.5-flash\n")

for i, (message, name, role) in enumerate(test_cases, 1):
    print(f"\n{'='*40}")
    print(f"Test {i}: {name} ({role})")
    print(f"Message: '{message}'")
    print(f"{'='*40}")
    
    emotion = detect_emotion(message)
    print(f"📊 Emotion detected: {emotion}")
    
    response = get_health_response(message, name, role)
    print(f"💬 A.M.I. Response: {response}")
    
    # Check if response is useful
    if len(response.strip()) < 10:
        print("⚠️ Warning: Response too short")
    elif 'cannot provide medical advice' in response.lower():
        print("❌ Issue: Gemini refusing medical advice")
    else:
        print("✅ Good response!")

print(f"\n{'='*50}")
print("✅ Medical response test complete!")
print("="*50)