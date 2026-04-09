# backend/face_working.py
import numpy as np
import cv2
import json
import os

class WorkingFaceRecognizer:
    def __init__(self):
        self.faces_dir = "faces"
        os.makedirs(self.faces_dir, exist_ok=True)
        print("🤖 Face recognizer initialized")
    
    def register(self, img, member_id, member_name):
        """
        Register a face for a member
        Returns: (success, encoding)
        """
        try:
            print(f"📸 Registering face for {member_name} (ID: {member_id})")
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Simple face detection (you can replace with face_recognition library)
            # For now, we'll create a dummy encoding
            height, width = img.shape[:2]
            
            # Create a dummy face encoding (128-dimensional vector like face_recognition)
            # In production, use: face_recognition.face_encodings(img)
            encoding = np.random.randn(128).tolist()  # Dummy encoding
            
            # Save face image for reference
            face_path = os.path.join(self.faces_dir, f"{member_id}_{member_name}.jpg")
            cv2.imwrite(face_path, img)
            
            print(f"✅ Face registered and saved to {face_path}")
            return True, encoding
            
        except Exception as e:
            print(f"❌ Face registration error: {e}")
            return False, None
    
    def recognize(self, img):
        """
        Recognize a face from image
        Returns: None if not recognized, or dict with member info
        """
        try:
            print("🔍 Attempting face recognition...")
            
            # For now, we'll use a dummy implementation
            # In production, you should:
            # 1. Load all registered face encodings from database
            # 2. Compare with current face encoding
            # 3. Return the best match if confidence > threshold
            
            # Dummy: Always return "not recognized" for now
            # You can enable this for testing with dummy members:
            # return {"id": 1, "name": "Test User", "confidence": 0.95}
            
            print("⚠️  Face not recognized (dummy implementation)")
            return None
            
        except Exception as e:
            print(f"❌ Face recognition error: {e}")
            return None
    
    def get_all_faces(self):
        """Get list of all registered faces"""
        faces = []
        try:
            for filename in os.listdir(self.faces_dir):
                if filename.endswith('.jpg'):
                    parts = filename.split('_')
                    if len(parts) >= 2:
                        member_id = parts[0]
                        member_name = parts[1].replace('.jpg', '')
                        faces.append({
                            "id": member_id,
                            "name": member_name,
                            "path": os.path.join(self.faces_dir, filename)
                        })
        except Exception as e:
            print(f"Error getting faces: {e}")
        
        return faces

# Singleton instance
working_face_recognizer = WorkingFaceRecognizer()