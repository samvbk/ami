# backend/face_utils.py
import cv2
import numpy as np
import os
from deepface import DeepFace
import mediapipe as mp
import json
from typing import Optional, Dict, List
import time

class FaceRecognition:
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 1 for close range, 0 for far range
            min_detection_confidence=0.5
        )
        self.faces_db = {}
        self.load_faces_db()
    
    def load_faces_db(self):
        """Load face encodings from database"""
        try:
            from db import get_db
            conn = get_db()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT id, name, face_encoding FROM members")
                members = cursor.fetchall()
                
                for member in members:
                    if member['face_encoding']:
                        try:
                            encoding = json.loads(member['face_encoding'])
                            self.faces_db[member['id']] = {
                                'name': member['name'],
                                'encoding': np.array(encoding)
                            }
                        except:
                            continue
                
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Error loading faces DB: {e}")
    
    def detect_faces_mediapipe(self, image):
        """Detect faces using MediaPipe (works better on macOS)"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_image)
        
        faces = []
        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                h, w, _ = image.shape
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                faces.append((x, y, width, height))
        
        return faces
    
    def extract_face_encoding(self, face_image):
        """Extract face encoding using DeepFace"""
        try:
            # Use DeepFace for face recognition
            result = DeepFace.represent(
                face_image,
                model_name="Facenet512",
                enforce_detection=False,
                detector_backend="mediapipe"  # Uses mediapipe for detection
            )
            
            if result:
                return np.array(result[0]['embedding'])
        except Exception as e:
            print(f"Error extracting face encoding: {e}")
        
        return None
    
    def recognize_face(self, image) -> Optional[Dict]:
        """Recognize face in image"""
        # Detect faces
        faces = self.detect_faces_mediapipe(image)
        
        if not faces:
            return None
        
        # Take the largest face
        (x, y, w, h) = max(faces, key=lambda rect: rect[2] * rect[3])
        face_roi = image[y:y+h, x:x+w]
        
        # Extract encoding
        face_encoding = self.extract_face_encoding(face_roi)
        
        if face_encoding is None:
            return None
        
        # Compare with known faces
        best_match = None
        best_similarity = 0.6  # Threshold
        
        for member_id, member_data in self.faces_db.items():
            saved_encoding = member_data['encoding']
            
            # Calculate cosine similarity
            similarity = np.dot(face_encoding, saved_encoding) / (
                np.linalg.norm(face_encoding) * np.linalg.norm(saved_encoding)
            )
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = {
                    'id': member_id,
                    'name': member_data['name'],
                    'similarity': float(similarity)
                }
        
        return best_match
    
    def register_face(self, image, member_id, member_name):
        """Register a new face"""
        faces = self.detect_faces_mediapipe(image)
        
        if not faces:
            return False, "No face detected"
        
        # Take the largest face
        (x, y, w, h) = max(faces, key=lambda rect: rect[2] * rect[3])
        face_roi = image[y:y+h, x:x+w]
        
        # Extract encoding
        face_encoding = self.extract_face_encoding(face_roi)
        
        if face_encoding is None:
            return False, "Could not extract face features"
        
        # Save to in-memory DB
        self.faces_db[member_id] = {
            'name': member_name,
            'encoding': face_encoding
        }
        
        # Save face image locally
        faces_dir = "faces"
        os.makedirs(faces_dir, exist_ok=True)
        face_path = os.path.join(faces_dir, f"{member_name}_{member_id}.jpg")
        cv2.imwrite(face_path, face_roi)
        
        return True, face_encoding.tolist()

# Global instance
face_recognizer = FaceRecognition()