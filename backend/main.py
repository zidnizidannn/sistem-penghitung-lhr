import cv2
import mysql.connector
from datetime import datetime
from ultralytics import YOLO

# model = YOLO("D:/Zidni Zidan/Documents/KAMPUS/Tugas Akhir/sistem/backend/yolov8/train4/weights/best.pt")  # Gunakan model yang sesuai

# db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="",
#     database="detection"
# )
# cursor = db.cursor()

# cap = cv2.VideoCapture("D:/Zidni Zidan/Documents/KAMPUS/Tugas Akhir/sistem/backend/yolov8/det3.jpg")

# while cap.isOpened():
#     ret, frame = cap.read()
#     if ret:
#         if frame.shape[2] == 4:
#             frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
        
#         results = model(frame, conf=0.4)
#     for r in results:
#         for box in r.boxes:
#             cls = int(box.cls[0])
#             print(f"Detected class index: {cls}")

#             vehicle_classes = {
#                 0: "bus",
#                 1: "car",
#                 2: "motorcycle",
#                 3: "truck"
#             }

#             if cls in vehicle_classes:
#                 vehicle_type = vehicle_classes[cls]
#                 timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#                 sql = "INSERT INTO vehicle_detections (timestamp, vehicle_type) VALUES (%s, %s)"
#                 cursor.execute(sql, (timestamp, vehicle_type))
#                 db.commit()

#     cv2.imshow("YOLOv8 Detection", frame)

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

# ==============================
# ATUR PARAMETER DI SINI
jam_mulai = "22:00"  # Format HH:MM
jam_selesai = "23:59"  # Format HH:MM
total_kendaraan = 198  # Jumlah kendaraan yang ingin di-generate
# ==============================

# Konversi waktu ke format datetime
today = datetime.now().date()
start_time = datetime.strptime(f"{today} {jam_mulai}:00", "%Y-%m-%d %H:%M:%S")
end_time = datetime.strptime(f"{today} {jam_selesai}:00", "%Y-%m-%d %H:%M:%S")

# Pastikan jam mulai lebih kecil dari jam selesai
if start_time >= end_time:
    print("Error: Jam mulai harus lebih kecil dari jam selesai.")
    exit()

# Distribusi jenis kendaraan
vehicle_distribution = {
    "motorcycle": 0.6,  # 60%
    "car": 0.3,         # 30%
    "bus": 0.05,        # 5%
    "truck": 0.05       # 5%
}

# Buat daftar timestamp kendaraan dengan interval acak
time_interval = (end_time - start_time).total_seconds() / total_kendaraan
timestamps = [start_time + timedelta(seconds=i * time_interval) for i in range(total_kendaraan)]

# Generate data kendaraan berdasarkan distribusi
for ts in timestamps:
    vehicle_type = random.choices(
        list(vehicle_distribution.keys()), 
        weights=vehicle_distribution.values()
    )[0]

    # Masukkan data ke database
    sql = "INSERT INTO vehicle_detections (timestamp, vehicle_type) VALUES (%s, %s)"
    cursor.execute(sql, (ts.strftime('%Y-%m-%d %H:%M:%S'), vehicle_type))
    db.commit()

print(f"Berhasil menambahkan {total_kendaraan} kendaraan dari {jam_mulai} sampai {jam_selesai}.")

# Tutup koneksi database
cursor.close()
db.close()
