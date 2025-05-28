from ultralytics import YOLO
import cv2
import time
from datetime import datetime
from helper.conn import conn as db_query

model = YOLO("./yolov8/train4/weights/best.pt")
VIDEO_SOURCE = "./yolov8/cctv1.mp4"

vehicle_classes = {
    0: "bus",
    1: "car",
    2: "motorcycle",
    3: "truck"
}

def run_detection(running_ref):
    print("[INFO] Seteksi dimulai")
    cap = cv2.VideoCapture(VIDEO_SOURCE)

    if not cap.isOpened():
        print("[ERROR] Video source not found or cannot be opened.")
        return

    while running_ref['running']:
        ret, frame = cap.read()
        if not ret:
            break

        if frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

        results = model(frame, conf=0.4)

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                if cls in vehicle_classes:
                    vehicle_type = vehicle_classes[cls]
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    sql = "INSERT INTO vehicle_detections (timestamp, vehicle_type) VALUES (%s, %s)"
                    db_query(sql, (timestamp,))
        time.sleep(0.1)
    cap.release()
    print("[INFO] Detection stopped")

def generate_frames():
    cap = cv2.VideoCapture(VIDEO_SOURCE)

    if not cap.isOpened():
        print("[ERROR] Video source not found or cannot be opened.")
        return

    while True:
        success, frame = cap.read()
        if not success:
            break

        if frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

        results = model.track(frame, persist=True, conf=0.4)

        if results and results[0].boxes.id is not None:
            res = results[0]
            boxes = res.boxes.xyxy.cpu().numpy()
            ids = res.boxes.id.cpu().numpy().astype(int)
            classes = res.boxes.cls.cpu().numpy().astype(int)

            for id, cls, box in zip(ids, classes, boxes):
                x1, y1, x2, y2 = box
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f'ID:{id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
