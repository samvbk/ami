# backend/config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Database connection
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql://root:9850337042@localhost:3306/healthcare")
    
    # Gemini API Key
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBceGQklxwC6L3-siM8AWr7O-2tziOXEao")
    
    # Validate API key
    @property
    def is_valid_gemini_key(self):
        if not self.GEMINI_API_KEY:
            return False
        if not self.GEMINI_API_KEY.startswith("AIza"):
            return False
        return True
    
    # App settings
    SECRET_KEY = os.getenv("SECRET_KEY", "ami_secret_key_change_in_production")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Directories
    FACES_DIR = "faces"
    AUDIO_DIR = "audio"
    
    # Create directories
    os.makedirs(FACES_DIR, exist_ok=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)
    
config = Config()

# Print configuration (mask sensitive data)
def print_config():
    print(f"🔧 A.M.I. Configuration:")
    print(f"   Database: {config.DATABASE_URL}")
    if config.GEMINI_API_KEY:
        print(f"   Gemini API: ✅ Set ({config.GEMINI_API_KEY[:12]}...)")
    else:
        print(f"   Gemini API: ❌ Not set")
    print(f"   Faces directory: {config.FACES_DIR}")
    print(f"   Audio directory: {config.AUDIO_DIR}")

if __name__ == "__main__":
    print_config()