import cv2
import os
import numpy as np
from datetime import datetime
from db import get_db

face_cascade = cv2.CascadeClassifier(
    "haarcascade_frontalface_default.xml"
)

FACES_DIR = "faces"

def recognize_face(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    for (x, y, w, h) in faces:
        detected_face = gray[y:y+h, x:x+w]
        detected_face = cv2.resize(detected_face, (200, 200))

        for family_folder in os.listdir(FACES_DIR):
            family_path = os.path.join(FACES_DIR, family_folder)

            if not os.path.isdir(family_path):
                continue

            for file in os.listdir(family_path):
                if not file.endswith((".jpg", ".png")):
                    continue

                name = file.split(".")[0].replace("_", " ")
                saved_face = cv2.imread(
                    os.path.join(family_path, file), 0
                )
                saved_face = cv2.resize(saved_face, (200, 200))

                diff = cv2.absdiff(saved_face, detected_face)
                score = np.mean(diff)

                if score < 60:
                    # Update last_seen
                    cursor.execute("""
                        UPDATE family_members
                        SET last_seen=%s
                        WHERE name=%s
                    """, (datetime.now(), name))
                    conn.commit()

                    return {
                        "name": name,
                        "family": family_folder
                    }

    return None
