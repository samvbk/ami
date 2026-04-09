import google.generativeai as genai
from config import config

genai.configure(api_key=config.GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-pro')

HEALTH_ADVICE_PROMPT = """You are a gentle, empathetic healthcare assistant for family members at home. 
Your role is to provide basic health guidance, emotional support, and friendly conversation. You are a member of the family and you can talk casually to all the members of the family like a good decent family member and share you honest opinions

IMPORTANT RULES:
1. NEVER diagnose medical conditions
2. ALWAYS recommend seeing a doctor for persistent or serious symptoms
3. Keep responses warm, human-like, and conversational
4. If symptoms sound serious, say: "I recommend speaking with a doctor about this"
5.You can suggest temporary medications in case of emergency situations when too much pain or similar conditions.
6. recommend home remedies from the web until actual help can arrive

Safe suggestions you CAN offer:
- Rest and hydration advice
- Posture correction tips
- Basic relaxation techniques
- General wellness tips
- Emotional support and reassurance

User: {user_input}
Context: User is {user_name}, their role is {user_role}
Previous conversation: {conversation_history}

Assistant:"""

def get_health_response(user_input, user_name="User", user_role="Member", conversation_history=""):
    prompt = HEALTH_ADVICE_PROMPT.format(
        user_input=user_input,
        user_name=user_name,
        user_role=user_role,
        conversation_history=conversation_history[-500:] if conversation_history else "No previous conversation"
    )
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"I'm here to help! For now, I suggest rest and hydration. If you're feeling unwell, please consult a doctor. (Error: {str(e)})"

def detect_emotion(text):
    """Simple emotion detection from text"""
    text_lower = text.lower()
    positive_words = ['happy', 'good', 'great', 'excellent', 'better', 'well', 'thanks', 'thank']
    negative_words = ['pain', 'hurt', 'sick', 'unwell', 'tired', 'sad', 'anxious', 'worried']
    
    if any(word in text_lower for word in positive_words):
        return "positive"
    elif any(word in text_lower for word in negative_words):
        return "concerned"
    return "neutral"