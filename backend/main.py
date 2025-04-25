# import cv2
# import mysql.connector
# from datetime import datetime
# from ultralytics import YOLO

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

# Tanggal hari ini
today = datetime.now().date()

# Generate dan masukkan data ke database
for jam, total_kendaraan in data_kendaraan.items():
    start_time = datetime.strptime(f"{today} {jam}:00", "%Y-%m-%d %H:%M:%S")
    end_time = start_time + timedelta(hours=1) - timedelta(seconds=1)
    
    # Buat daftar timestamp kendaraan dengan interval acak
    time_interval = (end_time - start_time).total_seconds() / total_kendaraan
    timestamps = [start_time + timedelta(seconds=i * time_interval) for i in range(total_kendaraan)]
    
    for ts in timestamps:
        vehicle_type = random.choices(
            list(vehicle_distribution.keys()), 
            weights=vehicle_distribution.values()
        )[0]
        
        # Masukkan data ke database
        sql = "INSERT INTO vehicle_detections (timestamp, vehicle_type) VALUES (%s, %s)"
        cursor.execute(sql, (ts.strftime('%Y-%m-%d %H:%M:%S'), vehicle_type))
        db.commit()
    
    print(f"Berhasil menambahkan {total_kendaraan} kendaraan untuk jam {jam}.")

# Tutup koneksi database
cursor.close()
db.close()

print("Semua data kendaraan telah dimasukkan ke dalam database.")
