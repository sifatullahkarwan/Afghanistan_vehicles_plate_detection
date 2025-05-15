# detection.py
import cv2
import numpy as np
import sqlite3
from datetime import datetime
from ultralytics import YOLO
from sort.sort import Sort
import cvzone

DB_PATH = "./Database/screeb.db"

def run_detection():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return "camera is not activae"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    model = YOLO('runs/detect/train6/weights/best.pt')
    tracker = Sort(max_age=10, min_hits=2, iou_threshold=0.3)
    tracked_plates = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        detections = []
        for info in results:
            for box in info.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0]) * 100
                if confidence > 80:
                    detections.append([x1, y1, x2, y2, confidence])

        detections = np.array(detections) if detections else np.empty((0, 5))
        tracked_objects = tracker.update(detections)
        current_ids = set()

        for obj in tracked_objects:
            x1, y1, x2, y2, track_id = map(int, obj)
            current_ids.add(track_id)
            cvzone.cornerRect(frame, (x1, y1, x2 - x1, y2 - y1), l=20, rt=2, colorR=(0, 255, 0))
            cvzone.putTextRect(frame, f"ID {track_id}", (x1, y1 - 10), thickness=2, scale=1.5)

            if track_id not in tracked_plates:
                entry_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                plate_img = frame[y1:y2, x1:x2]
                if plate_img.size > 0:
                    _, buffer = cv2.imencode(".jpg", plate_img)
                    plate_blob = buffer.tobytes()
                    cursor.execute("INSERT INTO number_plates (plate, entry_time) VALUES (?, ?)", (plate_blob, entry_time))
                    conn.commit()
                    tracked_plates[track_id] = {"entry_time": entry_time}

        lost_ids = set(tracked_plates.keys()) - current_ids
        for lost_id in lost_ids:
            if "exit_time" not in tracked_plates[lost_id]:
                exit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute("UPDATE number_plates SET exit_time = ? WHERE entry_time = ?",
                               (exit_time, tracked_plates[lost_id]["entry_time"]))
                conn.commit()
                tracked_plates[lost_id]["exit_time"] = exit_time

        cv2.imshow('detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    conn.close()
    return "detection Ended"
