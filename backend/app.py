# backend/app.py - FIXED VERSION WITH RELIABLE DATABASE CONNECTION
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import traceback
import mysql.connector
from mysql.connector import Error, pooling
import cv2
import pickle
import os
import numpy as np
import json
import requests
from datetime import datetime
import base64
from PIL import Image
import io
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from collections import defaultdict
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

load_dotenv()

# -------------------- NEWS MEMORY --------------------
last_fetched_news = []

from gemini_simple import get_health_response, detect_emotion

print("🚀 Starting Family Healthcare Assistant Backend")
print("=" * 50)

app = FastAPI(title="Family Healthcare Assistant API")

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- DUPLICATE MESSAGE PREVENTION --------------------
recent_messages = defaultdict(list)

# -------------------- DATABASE CONNECTION WITH RETRY --------------------
class DatabaseManager:
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', '9850337042'),
            'database': os.getenv('DB_NAME', 'healthcare'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'autocommit': False,
            'use_pure': True,
            'connection_timeout': 30,
            'pool_name': 'mypool',
            'pool_size': 5,
            'pool_reset_session': True
        }
        self.pool = None
        self.init_pool()
    
    def init_pool(self):
        """Initialize connection pool"""
        try:
            # First test connection without pool
            conn = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                port=self.config['port'],
                connection_timeout=10
            )
            conn.close()
            logger.info("✅ Database connection test successful")
            
            # Create pool
            self.pool = mysql.connector.pooling.MySQLConnectionPool(**self.config)
            logger.info(f"✅ Connection pool created with size {self.config['pool_size']}")
            return True
            
        except Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            logger.error("Please check:")
            logger.error("  1. MySQL is running (see Step 1 instructions)")
            logger.error("  2. Username/password is correct")
            logger.error("  3. Database 'healthcare' exists")
            return False
    
    def get_connection(self):
        """Get connection from pool with retry"""
        if not self.pool:
            if not self.init_pool():
                return None
        
        try:
            conn = self.pool.get_connection()
            # Test connection
            conn.ping(reconnect=True, attempts=3, delay=1)
            return conn
        except Error as e:
            logger.error(f"Failed to get connection: {e}")
            # Try to reinitialize pool
            self.pool = None
            time.sleep(1)
            return None
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False, commit=False):
        """Execute query with automatic connection handling"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            if not conn:
                raise Exception("No database connection available")
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            result = None
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            
            if commit:
                conn.commit()
                result = cursor.lastrowid
            
            return result
            
        except Exception as e:
            logger.error(f"Query error: {e}")
            if conn and commit:
                try:
                    conn.rollback()
                except:
                    pass
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

# Initialize database manager
db = DatabaseManager()

# -------------------- FACE RECOGNITION (OpenCV - NO DLIB) --------------------
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Create faces directory
os.makedirs("faces", exist_ok=True)

def extract_face_features(image_bytes):
    """Extract face features using OpenCV"""
    try:
        # Convert bytes to image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("Failed to decode image")
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(100, 100)  # Larger minimum size for better quality
        )
        
        if len(faces) == 0:
            logger.warning("No faces detected")
            return None
        
        # Get the largest face
        (x, y, w, h) = max(faces, key=lambda rect: rect[2] * rect[3])
        
        # Extract and process face ROI
        face_roi = gray[y:y+h, x:x+w]
        face_roi = cv2.resize(face_roi, (128, 128))  # Larger size for better features
        face_roi = cv2.equalizeHist(face_roi)  # Improve contrast
        
        # Extract features (histogram of oriented gradients style)
        features = []
        
        # Divide into regions and get histograms
        regions = [(0, 0, 64, 64), (64, 0, 64, 64), (0, 64, 64, 64), (64, 64, 64, 64)]
        for (rx, ry, rw, rh) in regions:
            region = face_roi[ry:ry+rh, rx:rx+rw]
            hist = cv2.calcHist([region], [0], None, [32], [0, 256])
            hist = cv2.normalize(hist, hist).flatten()
            features.extend(hist)
        
        # Add LBP-like features
        lbp = np.zeros_like(face_roi)
        for i in range(1, face_roi.shape[0]-1):
            for j in range(1, face_roi.shape[1]-1):
                center = face_roi[i, j]
                code = 0
                code |= (face_roi[i-1, j-1] > center) << 7
                code |= (face_roi[i-1, j] > center) << 6
                code |= (face_roi[i-1, j+1] > center) << 5
                code |= (face_roi[i, j+1] > center) << 4
                code |= (face_roi[i+1, j+1] > center) << 3
                code |= (face_roi[i+1, j] > center) << 2
                code |= (face_roi[i+1, j-1] > center) << 1
                code |= (face_roi[i, j-1] > center) << 0
                lbp[i, j] = code
        lbp_hist = cv2.calcHist([lbp], [0], None, [64], [0, 256])
        lbp_hist = cv2.normalize(lbp_hist, lbp_hist).flatten()
        features.extend(lbp_hist)
        
        return np.array(features, dtype=np.float32)
        
    except Exception as e:
        logger.error(f"Error extracting face features: {e}")
        traceback.print_exc()
        return None

def load_face_features():
    """Load all face features from database"""
    try:
        result = db.execute_query(
            """
            SELECT m.id, m.name, m.face_encoding, f.family_name 
            FROM members m 
            JOIN families f ON m.family_id = f.id 
            WHERE m.face_encoding IS NOT NULL
            """,
            fetch_all=True
        )
        
        if not result:
            return {}
        
        face_features = {}
        for member in result:
            if member['face_encoding']:
                try:
                    features = pickle.loads(member['face_encoding'])
                    face_features[member['id']] = {
                        'name': member['name'],
                        'family_name': member['family_name'],
                        'features': features
                    }
                except Exception as e:
                    logger.error(f"Error loading features for {member['name']}: {e}")
                    continue
        
        logger.info(f"✅ Loaded {len(face_features)} face encodings from database")
        return face_features
        
    except Exception as e:
        logger.error(f"Error loading face features: {e}")
        return {}

def recognize_face_from_image(image_bytes):
    """Recognize face using OpenCV features"""
    try:
        # Extract features from input image
        input_features = extract_face_features(image_bytes)
        
        if input_features is None:
            logger.warning("No face features extracted")
            return None
        
        # Load stored features
        stored_features = load_face_features()
        
        if not stored_features:
            logger.warning("No stored face features found")
            return None
        
        best_match = None
        best_distance = float('inf')
        
        for member_id, data in stored_features.items():
            stored_feature = data['features']
            
            # Ensure same length
            min_len = min(len(input_features), len(stored_feature))
            input_trunc = input_features[:min_len]
            stored_trunc = stored_feature[:min_len]
            
            # Calculate Euclidean distance
            distance = np.linalg.norm(input_trunc - stored_trunc)
            
            # Convert to confidence (0-1)
            max_distance = np.sqrt(min_len) * 255  # Theoretical maximum
            confidence = max(0, 1 - (distance / (max_distance * 0.15)))  # Adjusted threshold
            
            logger.debug(f"Comparing with {data['name']}: distance={distance:.2f}, confidence={confidence:.2%}")
            
            # Update best match
            if confidence > 0.65 and distance < best_distance:
                best_distance = distance
                best_match = {
                    'member_id': member_id,
                    'name': data['name'],
                    'family_name': data['family_name'],
                    'confidence': confidence,
                    'distance': distance
                }
        
        if best_match:
            logger.info(f"✅ Face recognized: {best_match['name']} (confidence: {best_match['confidence']:.2%})")
            
            # Update last seen
            db.execute_query(
                "UPDATE members SET last_seen = NOW() WHERE id = %s",
                (best_match['member_id'],),
                commit=True
            )
            
            return best_match
        
        logger.info("❌ No matching face found")
        return None
        
    except Exception as e:
        logger.error(f"Error in face recognition: {e}")
        traceback.print_exc()
        return None

# -------------------- WEATHER API --------------------
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
weather_cache = {}

def get_weather_info(city="Delhi"):
    """Get weather information with caching"""
    if not WEATHER_API_KEY:
        logger.warning("WEATHER_API_KEY not set")
        return None

    # Check cache (5 minute TTL)
    cache_key = city.lower()
    if cache_key in weather_cache:
        cached_time, cached_data = weather_cache[cache_key]
        if time.time() - cached_time < 300:  # 5 minutes
            return cached_data

    try:
        logger.info(f"Fetching weather for {city}...")

        response = requests.get(
            "http://api.weatherapi.com/v1/current.json",
            params={
                "key": WEATHER_API_KEY,
                "q": city,
                "aqi": "no"
            },
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        weather_info = {
            "temperature": data["current"]["temp_c"],
            "description": data["current"]["condition"]["text"],
            "city": data["location"]["name"],
            "humidity": data["current"]["humidity"],
            "wind_speed": data["current"]["wind_kph"],
            "feels_like": data["current"]["feelslike_c"]
        }

        # Update cache
        weather_cache[cache_key] = (time.time(), weather_info)

        logger.info(f"Weather fetched: {weather_info['temperature']}°C")
        return weather_info

    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return None

# -------------------- NEWS API --------------------
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
news_cache = {}

def get_news(category="general", country="in"):
    """Get news with caching"""
    if not NEWS_API_KEY:
        logger.warning("NEWS_API_KEY not set")
        return None

    cache_key = f"{category}_{country}"
    if cache_key in news_cache:
        cached_time, cached_data = news_cache[cache_key]
        if time.time() - cached_time < 300:  # 5 minutes
            return cached_data

    try:
        logger.info(f"Fetching news ({category})...")

        response = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={
                "country": country,
                "category": category,
                "apiKey": NEWS_API_KEY,
                "pageSize": 5
            },
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        if data.get("articles"):
            articles = []
            for article in data["articles"][:3]:
                articles.append({
                    "title": article.get("title", "No title"),
                    "description": article.get("description", "No description"),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "url": article.get("url", "#")
                })

            # Update cache
            news_cache[cache_key] = (time.time(), articles)

            logger.info(f"News fetched: {len(articles)} articles")
            return articles

        return None

    except Exception as e:
        logger.error(f"News API error: {e}")
        return None

# -------------------- ENHANCED MEMORY SYSTEM --------------------
class ConversationMemory:
    def __init__(self):
        self.memory_file = "conversation_memory.json"
        self.memory = {}
        self.load_memory()
    
    def load_memory(self):
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    self.memory = json.load(f)
            else:
                self.memory = {}
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
            self.memory = {}
    
    def save_memory(self):
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def add_conversation(self, member_id: int, user_message: str, assistant_response: str):
        member_id_str = str(member_id)
        if member_id_str not in self.memory:
            self.memory[member_id_str] = []
        
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "assistant": assistant_response
        }
        
        self.memory[member_id_str].append(conversation)
        
        if len(self.memory[member_id_str]) > 100:
            self.memory[member_id_str] = self.memory[member_id_str][-100:]
        
        self.save_memory()
    
    def get_conversation_history(self, member_id: int, limit: int = 10) -> str:
        member_id_str = str(member_id)
        if member_id_str not in self.memory:
            return ""
        
        conversations = self.memory[member_id_str][-limit:]
        history = []
        
        for conv in conversations:
            history.append(f"User: {conv['user']}")
            history.append(f"Assistant: {conv['assistant']}")
        
        return "\n".join(history)
    
    def get_member_preferences(self, member_id: int) -> Dict[str, Any]:
        member_id_str = str(member_id)
        if member_id_str not in self.memory:
            return {}
        
        preferences = {
            "frequent_topics": [],
            "conversation_count": len(self.memory[member_id_str]),
            "last_interaction": None
        }
        
        conversations = self.memory[member_id_str][-20:]
        
        if conversations:
            preferences["last_interaction"] = conversations[-1]["timestamp"]
            
            topic_count = {}
            for conv in conversations:
                msg = conv["user"].lower()
                
                if any(word in msg for word in ['weather', 'temperature', 'rain', 'sunny']):
                    topic_count['weather'] = topic_count.get('weather', 0) + 1
                if any(word in msg for word in ['news', 'headline', 'update']):
                    topic_count['news'] = topic_count.get('news', 0) + 1
                if any(word in msg for word in ['health', 'doctor', 'medicine', 'pain', 'fever']):
                    topic_count['health'] = topic_count.get('health', 0) + 1
                if any(word in msg for word in ['family', 'home', 'house']):
                    topic_count['family'] = topic_count.get('family', 0) + 1
            
            sorted_topics = sorted(topic_count.items(), key=lambda x: x[1], reverse=True)[:3]
            preferences["frequent_topics"] = [topic for topic, count in sorted_topics]
        
        return preferences

memory_system = ConversationMemory()

# -------------------- ROUTES --------------------
@app.get("/")
def root():
    return {
        "status": "running", 
        "message": "Family Healthcare Assistant API",
        "database": "connected" if db.pool else "disconnected"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    # Test database connection
    db_status = "disconnected"
    if db.pool:
        conn = db.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                db_status = "connected"
            except:
                pass
            finally:
                conn.close()
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat(),
        "memory_entries": sum(len(v) for v in memory_system.memory.values()),
        "apis": {
            "weather": "active" if WEATHER_API_KEY else "inactive",
            "news": "active" if NEWS_API_KEY else "inactive"
        }
    }

@app.post("/recognize")
async def recognize_face_endpoint(image: UploadFile = File(...)):
    """Face recognition endpoint"""
    try:
        logger.info("Processing face recognition...")
        
        image_bytes = await image.read()
        
        if len(image_bytes) < 1000:
            return JSONResponse({
                "success": False,
                "message": "Image too small. Please take a clearer photo."
            })
        
        recognition_result = recognize_face_from_image(image_bytes)
        
        if recognition_result:
            return JSONResponse({
                "success": True,
                "recognized": True,
                "member": {
                    "id": recognition_result['member_id'],
                    "name": recognition_result['name'],
                    "family_name": recognition_result['family_name']
                },
                "confidence": float(recognition_result['confidence']),
                "message": f"Welcome back, {recognition_result['name']}! 😊"
            })
        else:
            return JSONResponse({
                "success": True,
                "recognized": False,
                "message": "Face not recognized. Would you like to register?"
            })
            
    except Exception as e:
        logger.error(f"Face recognition error: {e}")
        traceback.print_exc()
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.post("/register")
async def register_member(
    image: UploadFile = File(...),
    family_name: str = Form(...),
    member_name: str = Form(...),
    role: str = Form(...),
    age: str = Form(None),
    medical_history: str = Form(None),
    emergency_contact: str = Form(None)
):
    """Member registration endpoint"""
    try:
        logger.info(f"Registering {member_name}...")
        
        image_bytes = await image.read()
        
        # Extract face features
        face_features = extract_face_features(image_bytes)
        
        if face_features is None:
            return JSONResponse({
                "success": False,
                "message": "No face detected. Please ensure good lighting and face is clearly visible."
            })
        
        # Check if family exists
        family = db.execute_query(
            "SELECT id FROM families WHERE family_name = %s",
            (family_name,),
            fetch_one=True
        )
        
        if family:
            family_id = family['id']
        else:
            family_id = db.execute_query(
                "INSERT INTO families (family_name) VALUES (%s)",
                (family_name,),
                commit=True
            )
        
        # Save face encoding
        encoding_bytes = pickle.dumps(face_features)
        
        # Save image to disk
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f"faces/{family_id}_{member_name}_{timestamp}.jpg"
        with open(image_path, "wb") as f:
            f.write(image_bytes)
        
        # Insert member
        member_id = db.execute_query(
            """
            INSERT INTO members 
            (family_id, name, role, age, face_encoding, medical_history, emergency_contact, last_seen) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """,
            (
                family_id,
                member_name,
                role,
                int(age) if age and age.isdigit() else None,
                encoding_bytes,
                medical_history,
                emergency_contact
            ),
            commit=True
        )
        
        logger.info(f"✅ Registered {member_name} (ID: {member_id})")
        
        return JSONResponse({
            "success": True,
            "member_id": member_id,
            "family_id": family_id,
            "message": f"Successfully registered {member_name}! 🎉"
        })
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        traceback.print_exc()
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.post("/chat")
async def chat(
    member_id: int = Form(...),
    message: str = Form(...),
    use_voice: str = Form("false"),
):
    """Chat endpoint"""
    try:
        # Check for duplicate messages
        current_time = time.time()
        recent = recent_messages[member_id]
        
        recent = [msg for msg in recent if current_time - msg['time'] < 3]
        recent_messages[member_id] = recent
        
        for msg in recent:
            if msg['text'] == message:
                logger.info(f"Ignoring duplicate message")
                return JSONResponse({
                    "success": True,
                    "response": None,
                    "emotion": "neutral",
                    "duplicate": True
                })
        
        recent.append({'text': message, 'time': current_time})
        
        logger.info(f"Chat from member {member_id}: {message[:50]}...")
        
        # Get member info
        member_info = db.execute_query(
            """
            SELECT m.name, f.family_name 
            FROM members m 
            JOIN families f ON m.family_id = f.id 
            WHERE m.id = %s
            """,
            (member_id,),
            fetch_one=True
        )
        
        member_name = member_info['name'] if member_info else "Guest"
        family_name = member_info['family_name'] if member_info else "Family"
        
        # Get context
        memory_history = memory_system.get_conversation_history(member_id)
        preferences = memory_system.get_member_preferences(member_id)
        
        current_hour = datetime.now().hour
        current_time_str = datetime.now().strftime("%I:%M %p")
        is_morning = current_hour < 12
        
        # Get weather if relevant
        weather_info = None
        if any(word in message.lower() for word in ['weather', 'temperature', 'hot', 'cold', 'rain']):
            weather_info = get_weather_info()
        
        # Get news if requested
        news_articles = None
        if any(word in message.lower() for word in ['news', 'headlines', 'update']):
            news_articles = get_news()
        
        # Generate response
        response = get_health_response(
            message=message,
            member_name=member_name,
            history=memory_history,
            weather_info=weather_info,
            news_articles=news_articles,
            preferences=preferences,
            current_time=current_time_str,
            is_morning=is_morning
        )
        
        emotion = detect_emotion(message)
        
        # Save conversation
        memory_system.add_conversation(member_id, message, response)
        
        # Save to database
        db.execute_query(
            """
            INSERT INTO conversations 
            (member_id, message, response, emotion) 
            VALUES (%s, %s, %s, %s)
            """,
            (member_id, message, response, emotion),
            commit=True
        )
        
        return JSONResponse({
            "success": True,
            "response": response,
            "emotion": emotion,
            "member_name": member_name,
            "family_name": family_name,
            "timestamp": datetime.now().isoformat(),
            "weather": weather_info,
            "has_news": news_articles is not None,
            "duplicate": False
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        traceback.print_exc()
        return JSONResponse({
            "success": False,
            "response": "I'm having trouble connecting right now. Please try again.",
            "emotion": "concerned"
        }, status_code=500)

@app.get("/weather")
async def get_weather_endpoint(city: str = None):
    """Weather endpoint"""
    try:
        weather = get_weather_info(city or "Delhi")
        
        if weather:
            return JSONResponse({"success": True, "weather": weather})
        else:
            return JSONResponse({"success": False, "message": "Weather fetch failed"})
            
    except Exception as e:
        logger.error(f"Weather error: {e}")
        return JSONResponse({"success": False, "error": str(e)})

@app.get("/news")
async def get_news_endpoint():
    """News endpoint"""
    global last_fetched_news
    
    try:
        articles = get_news()
        
        if articles:
            last_fetched_news = articles
            return JSONResponse({"success": True, "articles": articles})
        
        return JSONResponse({"success": False, "message": "No articles found"})
        
    except Exception as e:
        logger.error(f"News error: {e}")
        return JSONResponse({"success": False, "message": str(e)})

@app.get("/news-detail/{index}")
async def get_news_detail(index: int):
    """News detail endpoint"""
    global last_fetched_news
    
    try:
        if not last_fetched_news:
            return JSONResponse({"success": False, "message": "No news loaded"})
        
        if index < 0 or index >= len(last_fetched_news):
            return JSONResponse({"success": False, "message": "Invalid article number"})
        
        article = last_fetched_news[index]
        
        return JSONResponse({
            "success": True,
            "title": article["title"],
            "description": article.get("description"),
            "url": article.get("url")
        })
        
    except Exception as e:
        logger.error(f"News detail error: {e}")
        return JSONResponse({"success": False, "message": str(e)})

@app.get("/member/{member_id}")
async def get_member_info(member_id: int):
    """Get member info"""
    try:
        member = db.execute_query(
            """
            SELECT m.id, m.name, m.role, m.age, m.medical_history, 
                   m.emergency_contact, m.last_seen, f.family_name 
            FROM members m 
            JOIN families f ON m.family_id = f.id 
            WHERE m.id = %s
            """,
            (member_id,),
            fetch_one=True
        )
        
        if member:
            return JSONResponse({"success": True, "member": member})
        else:
            return JSONResponse({"success": False, "message": "Member not found"})
            
    except Exception as e:
        logger.error(f"Member info error: {e}")
        return JSONResponse({"success": False, "error": str(e)})

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("🚀 Family Healthcare Assistant Backend")
    print("=" * 50)
    print(f"✅ Database Pool: {'Ready' if db.pool else 'Not Connected'}")
    print("✅ Face Recognition: OpenCV Ready")
    print(f"✅ Weather API: {'Ready' if WEATHER_API_KEY else 'Not Configured'}")
    print(f"✅ News API: {'Ready' if NEWS_API_KEY else 'Not Configured'}")
    print("✅ Conversation Memory: Ready")
    print("=" * 50)
    print("🌐 Server starting on http://localhost:8000")
    print("📝 API Docs: http://localhost:8000/docs")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)