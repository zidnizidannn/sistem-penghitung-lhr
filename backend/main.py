# import cv2
# import mysql.connector
# from datetime import datetime
# from ultralytics import YOLO

# # Load YOLO model
# model = YOLO("./yolov8/train4/weights/best.pt")

# # Database connection
# db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="",
#     database="detection"
# )
# cursor = db.cursor()

# # Open video
# cap = cv2.VideoCapture("./yolov8/cctv1.mp4")

# # Line for counting
# line_y = 700
# offset = 5

# # Counter
# counter = {
#     "bus": 0,
#     "car": 0,
#     "motorcycle": 0,
#     "truck": 0
# }

# vehicle_classes = {
#     0: "bus",
#     1: "car",
#     2: "motorcycle",
#     3: "truck"
# }

# # Set to track ID yang sudah crossing
# passed_ids = set()

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     if frame.shape[2] == 4:
#         frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

#     # Use tracking
#     results = model.track(frame, persist=True, conf=0.4)[0]

#     if results.boxes.id is not None:
#         ids = results.boxes.id.cpu().numpy().astype(int)
#         classes = results.boxes.cls.cpu().numpy().astype(int)
#         boxes = results.boxes.xyxy.cpu().numpy()

#         for id, cls, box in zip(ids, classes, boxes):
#             if cls in vehicle_classes:
#                 vehicle_type = vehicle_classes[cls]
#                 x1, y1, x2, y2 = box
#                 x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

#                 cx = int((x1 + x2) / 2)
#                 cy = int((y1 + y2) / 2)

#                 # Gambar bbox dan ID
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                 cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
#                 cv2.putText(frame, f'ID:{id}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,0), 2)

#                 # Cek crossing line
#                 if (line_y - offset) < cy < (line_y + offset):
#                     if id not in passed_ids:
#                         passed_ids.add(id)
#                         counter[vehicle_type] += 1
#                         timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#                         sql = "INSERT INTO vehicle_detections (timestamp, vehicle_type) VALUES (%s, %s)"
#                         cursor.execute(sql, (timestamp, vehicle_type))
#                         db.commit()

#     # Draw counting line
#     cv2.line(frame, (0, line_y), (frame.shape[1], line_y), (255, 0, 0), 2)

#     # Show counter text
#     y_pos = 50
#     for v_type, count in counter.items():
#         cv2.putText(frame, f"{v_type}: {count}", (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
#         y_pos += 30

#     # Show frame
#     cv2.imshow("YOLOv8 Tracking Detection", frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()
# cursor.close()
# db.close()

import random
import mysql.connector
from datetime import datetime, timedelta

# Koneksi ke database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="detection"
)
cursor = db.cursor()

# Data jumlah kendaraan per jam berdasarkan hasil pengurangan terakhir
data_kendaraan = {
    "00:00": 270, "01:00": 146, "02:00": 110, "03:00": 77, "04:00": 166, "05:00": 253,
    "06:00": 468, "07:00": 753, "08:00": 844, "09:00": 882, "10:00": 902, "11:00": 1025,
    "12:00": 915, "13:00": 958, "14:00": 1002, "15:00": 1133, "16:00": 1170, "17:00": 1235, 
    "18:00": 1040, "19:00": 710, "20:00": 495, "21:00": 375, "22:00": 300, "23:00": 247, "23:59": 215
}

# Distribusi jenis kendaraan
vehicle_distribution = {
    "motorcycle": 0.65,  # 60%
    "car": 0.28,         # 30%
    "bus": 0.02,        # 5%
    "truck": 0.05       # 5%
}

start_date = datetime(2025, 5, 25).date()
end_date = datetime.now().date()

# Generate dan masukkan data ke database untuk setiap hari
current_date = start_date
while current_date <= end_date:
    # Cek apakah hari Sabtu (5) atau Minggu (6)
    is_weekend = current_date.weekday() >= 5
    multiplier = 1.3 if is_weekend else 1.0  # 30% lebih banyak kendaraan di akhir pekan
    
    for jam, total_kendaraan in data_kendaraan.items():
        # Tambahkan variasi acak (±10%) pada jumlah kendaraan
        variation = random.uniform(0.9, 1.1)
        adjusted_total = int(total_kendaraan * multiplier * variation)
        
        start_time = datetime.strptime(f"{current_date} {jam}:00", "%Y-%m-%d %H:%M:%S")
        end_time = start_time + timedelta(hours=1) - timedelta(seconds=1)
        
        # Buat daftar timestamp kendaraan dengan interval acak
        time_interval = (end_time - start_time).total_seconds() / adjusted_total
        timestamps = [start_time + timedelta(seconds=i * time_interval) for i in range(adjusted_total)]
        
        for ts in timestamps:
            vehicle_type = random.choices(
                list(vehicle_distribution.keys()),
                weights=vehicle_distribution.values()
            )[0]
            
            # Masukkan data ke database
            sql = "INSERT INTO vehicle_detections (timestamp, vehicle_type) VALUES (%s, %s)"
            cursor.execute(sql, (ts.strftime('%Y-%m-%d %H:%M:%S'), vehicle_type))
            db.commit()
        
        print(f"Berhasil menambahkan {adjusted_total} kendaraan untuk {current_date} jam {jam}.")
    
    # Pindah ke hari berikutnya
    current_date += timedelta(days=1)

# Tutup koneksi database
cursor.close()
db.close()

print("Semua data kendaraan dari 29 April 2025 hingga hari ini telah dimasukkan ke dalam database.")