# backend/face_simple.py
import cv2
import numpy as np
import os
import json
from typing import Optional, Dict, Tuple

class SimpleFaceRec:
    def __init__(self):
        # Load OpenCV face detector
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        print(f"🔍 Loading face cascade from: {cascade_path}")
        
        if not os.path.exists(cascade_path):
            print("❌ Face cascade file not found!")
            # Try alternative path
            cascade_path = 'haarcascade_frontalface_default.xml'
        
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if self.face_cascade.empty():
            print("❌ Failed to load face cascade!")
        else:
            print("✅ Face cascade loaded successfully")
        
        self.known_faces = {}
        self.load_faces()
    
    def load_faces(self):
        """Load faces from database"""
        try:
            from db import get_all_members
            members = get_all_members()
            print(f"📊 Found {len(members)} members in database")
            
            loaded_count = 0
            for member in members:
                if member.get('face_encoding'):
                    try:
                        encoding = json.loads(member['face_encoding'])
                        self.known_faces[member['id']] = {
                            'name': member['name'],
                            'encoding': np.array(encoding, dtype=np.float32)
                        }
                        loaded_count += 1
                        print(f"   Loaded face for: {member['name']} (ID: {member['id']})")
                    except Exception as e:
                        print(f"   Failed to load encoding for {member['name']}: {e}")
                        continue
            
            print(f"✅ Loaded {loaded_count} known faces from database")
            
        except Exception as e:
            print(f"❌ Error loading faces: {e}")
            self.known_faces = {}
    
    def detect_faces(self, image) -> list:
        """Detect faces in image with detailed logging"""
        if image is None:
            print("❌ No image provided for face detection")
            return []
        
        print(f"🔍 Detecting faces in image (shape: {image.shape})")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        print(f"📊 Found {len(faces)} face(s)")
        
        if len(faces) > 0:
            for i, (x, y, w, h) in enumerate(faces):
                print(f"   Face {i+1}: x={x}, y={y}, w={w}, h={h}")
        
        return faces
    
    def extract_features(self, face_image) -> np.ndarray:
        """Extract simple features from face"""
        if face_image is None or face_image.size == 0:
            print("❌ Invalid face image for feature extraction")
            return None
        
        try:
            # Resize to consistent size
            resized = cv2.resize(face_image, (100, 100))
            
            # Convert to grayscale
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            
            # Flatten and normalize
            features = gray.flatten().astype(np.float32) / 255.0
            
            print(f"📐 Extracted {len(features)} features from face")
            return features
            
        except Exception as e:
            print(f"❌ Error extracting features: {e}")
            return None
    
    def recognize(self, image) -> Optional[Dict]:
        """Recognize face in image"""
        print("🤖 Starting face recognition...")
        
        faces = self.detect_faces(image)
        
        if len(faces) == 0:
            print("❌ No faces detected for recognition")
            return None
        
        # Take the largest face
        (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
        face_roi = image[y:y+h, x:x+w]
        
        print(f"📏 Using largest face: {w}x{h} pixels")
        
        # Extract features
        features = self.extract_features(face_roi)
        
        if features is None:
            print("❌ Failed to extract features")
            return None
        
        # Compare with known faces
        best_match = None
        best_similarity = 0.7  # Threshold
        
        print(f"🔍 Comparing with {len(self.known_faces)} known faces...")
        
        for member_id, data in self.known_faces.items():
            # Simple Euclidean distance
            distance = np.linalg.norm(features - data['encoding'])
            similarity = 1.0 / (1.0 + distance)  # Convert distance to similarity
            
            print(f"   vs {data['name']}: similarity={similarity:.3f}")
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = {
                    'id': member_id,
                    'name': data['name'],
                    'confidence': float(similarity)
                }
        
        if best_match:
            print(f"✅ Recognized: {best_match['name']} (confidence: {best_match['confidence']:.3f})")
        else:
            print("❌ No match found above threshold")
        
        return best_match
    
    def register(self, image, member_id: int, member_name: str) -> Tuple[bool, str]:
        """Register a new face"""
        print(f"📝 Registering face for {member_name} (ID: {member_id})...")
        
        faces = self.detect_faces(image)
        
        if len(faces) == 0:
            print("❌ No faces detected for registration")
            return False, "No face detected in the image"
        
        # Take the largest face
        (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
        face_roi = image[y:y+h, x:x+w]
        
        print(f"📏 Using largest face: {w}x{h} pixels")
        
        # Extract features
        features = self.extract_features(face_roi)
        
        if features is None:
            print("❌ Failed to extract features for registration")
            return False, "Could not extract face features"
        
        # Save to memory
        self.known_faces[member_id] = {
            'name': member_name,
            'encoding': features
        }
        
        # Save face image
        os.makedirs("faces", exist_ok=True)
        face_path = f"faces/{member_name}_{member_id}.jpg"
        cv2.imwrite(face_path, face_roi)
        
        print(f"💾 Saved face image to: {face_path}")
        print(f"📊 Features saved for {member_name}")
        
        return True, features.tolist()

# Global instance
face_recognizer = SimpleFaceRec()