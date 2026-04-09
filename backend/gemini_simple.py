


# backend/gemini_simple.py
# WITH MEMORY + REAL WEATHER + REAL NEWS + FREE TIER MODELS

import os
from typing import Optional, Dict, Any, List
import google.generativeai as genai

print("🤖 Initializing Gemini free-tier models...")

# --------------------------------------------------
# API KEY
# --------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "❌ GEMINI_API_KEY not found. "
        "Run: export GEMINI_API_KEY='YOUR_API_KEY'"
    )

genai.configure(api_key=GEMINI_API_KEY)

# --------------------------------------------------
# FREE TIER MODEL OPTIONS (2.5 FLASH FIRST)
# --------------------------------------------------
FREE_TIER_MODELS = [
    "models/gemini-2.5-flash",           # BEST - Try this first
    "models/gemini-2.5-flash-lite",       # 2nd - Lite version of 2.5
    "models/gemini-2.0-flash-exp",        # 3rd - 2.0 experimental
    "models/gemini-2.0-flash",            # 4th - 2.0 stable
    "models/gemini-2.0-flash-lite-001",   # 5th - 2.0 lite version 1
    "models/gemini-2.0-flash-lite",       # 6th - 2.0 lite
    "models/gemini-1.5-flash",            # 7th - 1.5 flash
    "models/gemini-1.5-flash-lite",       # 8th - 1.5 lite
    "models/gemini-pro",                  # 9th - Legacy pro
    "models/gemini-1.0-pro"               # 10th - Legacy 1.0
]

model = None
selected_model_name = None

for MODEL_NAME in FREE_TIER_MODELS:
    try:
        print(f"🔄 Trying model: {MODEL_NAME}...")
        
        temp_model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config={
                "temperature": 0.8,
                "top_p": 0.95,
                "max_output_tokens": 512,
            },
        )

        test = temp_model.generate_content("Reply with: Gemini connected")
        if test and test.text:
            model = temp_model
            selected_model_name = MODEL_NAME
            print(f"✅ Gemini connected successfully using model: {MODEL_NAME}")
            break
        else:
            print(f"⚠️ Model {MODEL_NAME} returned empty response")

    except Exception as e:
        print(f"⚠️ Model {MODEL_NAME} failed: {e}")
        continue

if not model:
    raise RuntimeError("❌ All free-tier Gemini models failed. Check API key or quota.")

print(f"🎯 Active model: {selected_model_name}")

# --------------------------------------------------
# MAIN RESPONSE FUNCTION
# --------------------------------------------------
def get_health_response(
    message: str,
    member_name: str,
    history: Optional[str] = None,
    weather_info: Optional[Dict[str, Any]] = None,
    news_articles: Optional[List[Dict[str, Any]]] = None,
    preferences: Optional[Dict[str, Any]] = None,
    current_time: str = "",
    is_morning: bool = False
) -> str:
    """
    Generates response using free-tier Gemini models
    with memory, weather, and news context.
    """

    weather_context = ""
    if weather_info:
        weather_context = f"""
REAL WEATHER DATA:
- Location: {weather_info.get('city')}
- Temperature: {weather_info.get('temperature')}°C
- Conditions: {weather_info.get('description')}
- Humidity: {weather_info.get('humidity')}%
"""

    news_context = ""
    if news_articles:
        news_context = "REAL NEWS HEADLINES:\n"
        for i, article in enumerate(news_articles[:3], 1):
            news_context += f"{i}. {article.get('title')}\n"

    time_context = f"Current time: {current_time}" if current_time else ""

    preferences_context = ""
    if preferences:
        if preferences.get("frequent_topics"):
            preferences_context += f"{member_name} often asks about: {', '.join(preferences['frequent_topics'])}\n"

    prompt = f"""
You are Amy — an emergency medical assistant AND a friendly young Indian family member (age 22).

PERSONALITY:
- Warm, casual, natural like family
- Slightly fun, not robotic
- Keep replies short (1-3 sentences)
- Use light emojis occasionally 😊

RULES:
- If it's morning and user greets, mention the REAL weather.
- If user asks for news, share REAL headlines.
- For health issues: suggest home remedies + common Indian medicines from the HEALTH_REMEDIES dictionary below.
- Remember past conversations.
- Address the user by name: {member_name}

HEALTH_REMEDIES = {{
    "fever": "Paracetamol (Crocin, Dolo 650), rest, cold salt water wash, and tulsi ginger kadha",
    "body ache": "Ibuprofen (Brufen, Combiflam), massage with mustard oil + garlic, or Chandrika balm",
    "common cold": "Sinarest, Wikoryl, or Solvin Cold, and steam with menthol or eucalyptus oil",
    "nasal congestion": "Otrivin or Nasivion drops, and steam with crushed ajwain or peppermint oil",
    "sore throat": "Strepsils, Cofsils, Betadine gargle, and warm salt water + haldi gargle",
    "dry cough": "Ascoril D or Zedex, and ginger honey tea or black pepper + honey",
    "wet cough": "Benadryl or Grilinctus, and tulsi ginger decoction with a pinch of salt",
    "acidity": "Digene, Gelusil, or Eno, and cold milk with saunf or clove after meals",
    "stomach ache": "Meftal-Spas or Cyclopam, and hing or ajwain in warm water",
    "diarrhea": "ORS (Electral) and Loperamide, and rice kanji or curd with roasted cumin",
    "vomiting": "Domstal or Vomistop, and crushed ginger juice with honey or lemon mint sorbet",
    "knee pain": "Volini or Moov gel, and warm mustard oil + ajwain or Maha Narayan oil massage",
    "joint pain": "Volini or Moov gel, and warm mustard oil + ajwain or Maha Narayan oil massage",
    "muscle sprain": "Fastum Gel or Omni Gel, ice pack, then warm sesame oil massage",
    "minor cuts": "Dettol, Savlon, or Betadine ointment, and clean with haldi + neem water paste",
    "skin burns": "Burnol or Silverex, and apply aloe vera or grated raw potato",
    "skin allergies": "Cetirizine (Okacet) or Avil, and coconut oil + camphor or neem paste",
    "mouth ulcers": "Oraflora or Zytee, and gargle with coconut water or honey + haldi",
    "eye irritation": "Itone or Refresh Tears, and rose water or chilled triphala water eye compress",
    "constipation": "Dulcolax, Cremaffin, or Isabgol, and warm milk with ghee or soaked raisins",
    "tonsils": "Betadine gargle, Strepsils, or warm saline rinses, and licorice root gargle or tulsi tea",
    "weakness": "Revital H, Zincovit, or Electral, and moong dal soup or kheer",
    "sunstroke": "Electral, Glucon-D, or cold compresses, and aam panna or salted buttermilk",
    "heatstroke": "Electral, Glucon-D, or cold compresses, and aam panna or salted buttermilk",
    "dizziness": "Vertin, Stemetil, or Electral, and coriander seed water or date milkshake",
    "headache": "Saridon, Crocin Pain Relief, or Amrutanjan Balm, and sandalwood paste or ginger lemon tea",
    "indigestion": "Pudin Hara, Digene, or Panzynorm, and buttermilk with rock salt + roasted cumin",
    "bloating": "Pudin Hara, Digene, or Panzynorm, and buttermilk with rock salt + roasted cumin",
    "foot fungal": "Itch-Guard, Ring-Guard, or Candid powder, and Dettol foot soak or neem coconut oil",
    "back pain": "Moov, Volini spray, or Dynapar Gel, and rest on hard mattress + warm mustard oil with garlic",
    "toothache": "Sensodyne, clove oil, or Ketorol DT, and clove powder or salt pepper water gargle",
    "menstrual cramps": "Meftal-Spas or Cyclopam, and hot water bottle + ajwain saunf water",
    "period pain": "Meftal-Spas or Cyclopam, and hot water bottle + ajwain saunf water",
    "insect bites": "Caladryl lotion or Aloe Vera gel, and crushed basil or onion juice",
    "eye redness": "Itone or Rose water, and cool cucumber slices or chamomile tea bags",
    "earache": "Otogesic or Waxsolve, and warm sesame oil + garlic instillation",
    "blisters": "Neosporin or Soframycin, and fresh aloe pulp or coconut oil",
    "open wounds": "Clean with saline, apply Soframycin or Neosporin, cover with gauze, and apply haldi powder",
    "thermal burns": "Cool water rinse, Burnol or Silverex, and aloe vera or raw potato slice",
    "sunburn": "Caladryl lotion, Aloe Vera gel, or lacto-calamine, and thick yogurt + sandalwood pack",
    "sprain": "RICE method, Thrombophob gel or crepe bandage, and warm mustard oil massage after 24 hours",
    "swelling": "RICE method, Thrombophob gel or crepe bandage, and warm mustard oil massage after 24 hours",
    "bruises": "Ice pack, Heparin (Thrombophob) ointment, and warm haldi + milk paste",
    "splinters": "Remove with sterile tweezers, clean with Savlon, apply Cipladine, and warm bread poultice",
    "bee sting": "Baking soda paste or Caladryl lotion, Avil or Cetirizine, and crushed garlic or raw onion",
    "cracked heels": "Krack cream or Vaseline before bed, and warm salt water soak + pumice scrub"
}}

{time_context}
{weather_context}
{news_context}
{preferences_context}

CONVERSATION HISTORY:
{history if history else "No previous messages"}

USER ({member_name}): {message}

Reply naturally (1-3 sentences, use emojis occasionally):
"""

    try:
        response = model.generate_content(prompt)

        if not response or not response.text:
            return f"Hi {member_name}! 😊 How can I help you today?"

        cleaned = response.text.strip()
        cleaned = cleaned.replace("**", "").replace("*", "")

        return cleaned

    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return f"Hi {member_name}! 😊 How can I assist you today?"

# --------------------------------------------------
# EMOTION DETECTION
# --------------------------------------------------
def detect_emotion(text: str) -> str:
    t = text.lower()

    if any(word in t for word in ["emergency", "help", "pain", "hurt", "urgent", "bleeding"]):
        return "concerned"

    if any(word in t for word in ["sad", "lonely", "depressed", "crying"]):
        return "sad"

    if any(word in t for word in ["happy", "great", "excited", "awesome", "😊", "😄"]):
        return "happy"

    if any(word in t for word in ["lol", "haha", "funny", "😂"]):
        return "playful"

    if any(word in t for word in ["angry", "mad", "upset", "frustrated"]):
        return "angry"

    if any(word in t for word in ["fever", "headache", "cough", "cold", "medicine", "doctor", "hospital"]):
        return "concerned"

    if any(word in t for word in ["how", "what", "why", "when", "where", "who", "?"]):
        return "thinking"

    return "neutral"

# --------------------------------------------------
# TEST MODE
# --------------------------------------------------
if __name__ == "__main__":
    print(f"🧪 Testing with active model: {selected_model_name}")
    test = get_health_response(
        message="Good morning! What's the weather like?",
        member_name="Test User",
        is_morning=True
    )
    print("🧪 Test:", test)