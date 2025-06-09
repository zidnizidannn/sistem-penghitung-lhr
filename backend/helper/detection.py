from ultralytics import YOLO
import cv2
import time
from datetime import datetime
from helper.conn import conn as db_query

model = YOLO("./yolov8/train4/weights/best.pt")
VIDEO_SOURCE = "http://61.211.241.239/nphMotionJpeg?Resolution=1920&Quality=Standard"

vehicle_classes = {
    0: "bus",
    1: "car",
    2: "motorcycle",
    3: "truck"
}

def detect(running_ref):
    cap = cv2.VideoCapture(VIDEO_SOURCE)

    if not cap.isOpened():
        print("[ERROR] Video source not found or cannot be opened.")
        return

    print("[INFO] Deteksi dan streaming dimulai...")

    object_tracks = {}  # Simpan posisi center_y sebelumnya
    counted_objects = set()
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    LINE_Y = int(frame_height * 0.8)
    
    print(f"[DEBUG] Frame height: {frame_height}, Counting line Y: {LINE_Y}")

    while running_ref['running']:
        ret, frame = cap.read()
        if not ret:
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
                x1, y1, x2, y2 = map(int, box)
                vehicle_type = vehicle_classes.get(cls, "unknown")
                
                # Hitung center point untuk line crossing detection
                center_y = (y1 + y2) // 2
                prev_center_y = object_tracks.get(id)
                object_tracks[id] = center_y  # Update posisi terbaru

                # Gambar bounding box dan ID
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f'ID:{id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 2)

                # Line crossing detection - dari atas ke bawah
                if prev_center_y is not None and prev_center_y < LINE_Y <= center_y:
                    # Pastikan tidak duplikasi counting untuk ID yang sama
                    if id not in counted_objects:
                        counted_objects.add(id)
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        print(f"[CROSS] ID {id} ({vehicle_type}) crossed the line at {timestamp}")
                        
                        # Insert ke database hanya saat crossing
                        sql = "INSERT INTO vehicle_detections (timestamp, vehicle_type) VALUES (%s, %s)"
                        db_query(sql, (timestamp, vehicle_type))
                        
                        try:
                            result = db_query(sql, (timestamp, vehicle_type))
                            print(f"[DATABASE] Insert result: {result}")
                            
                            # Verifikasi data masuk
                            verify_sql = "SELECT * FROM vehicle_detections WHERE timestamp = %s ORDER BY id DESC LIMIT 1"
                            verify_result = db_query(verify_sql, (timestamp,))
                            print(f"[VERIFY] Data verification: {verify_result}")
                            
                            count_sql = "SELECT COUNT(*) as total FROM vehicle_detections"
                            count_result = db_query(count_sql, (), one=True)
                            print(f"[INFO] Total records in database: {count_result['total']}")
                            
                        except Exception as e:
                            print(f"[ERROR] Database insert failed: {e}")

        # Gambar garis counting
        cv2.line(frame, (0, LINE_Y), (frame.shape[1], LINE_Y), (0, 0, 255), 3)
        cv2.putText(frame, f'Garis hitung', (10, LINE_Y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # Encode frame dan kirim ke frontend
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        time.sleep(0.1)

    cap.release()
    print("[INFO] Deteksi dihentikan.")