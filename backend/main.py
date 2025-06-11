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

# Data base jumlah kendaraan per jam dengan pola realistis
base_traffic_pattern = {
    "00:00": 270, "01:00": 146, "02:00": 110, "03:00": 77, "04:00": 166, "05:00": 253,
    "06:00": 468, "07:00": 753, "08:00": 844, "09:00": 882, "10:00": 902, "11:00": 1025,
    "12:00": 915, "13:00": 958, "14:00": 1002, "15:00": 1133, "16:00": 1170, "17:00": 1235, 
    "18:00": 1040, "19:00": 710, "20:00": 495, "21:00": 375, "22:00": 300, "23:00": 247
}

# Distribusi jenis kendaraan dengan variasi random
def get_random_vehicle_distribution():
    """Membuat distribusi kendaraan yang berubah-ubah setiap jam"""
    base_motorcycle = random.uniform(0.60, 0.70)  # 60-70%
    base_car = random.uniform(0.20, 0.35)         # 20-35%
    base_bus = random.uniform(0.01, 0.05)         # 1-5%
    base_truck = 1 - (base_motorcycle + base_car + base_bus)  # Sisanya
    
    return {
        "motorcycle": base_motorcycle,
        "car": base_car,
        "bus": base_bus,
        "truck": max(0.01, base_truck)  # Minimal 1%
    }

def generate_random_timestamps(start_time, end_time, count):
    """Generate timestamp acak dalam rentang waktu tertentu"""
    timestamps = []
    start_timestamp = start_time.timestamp()
    end_timestamp = end_time.timestamp()
    
    for _ in range(count):
        random_timestamp = random.uniform(start_timestamp, end_timestamp)
        timestamps.append(datetime.fromtimestamp(random_timestamp))
    
    # Urutkan timestamp
    timestamps.sort()
    return timestamps

def get_daily_multiplier(date):
    """Dapatkan multiplier berdasarkan hari dalam seminggu"""
    weekday = date.weekday()  # 0=Senin, 6=Minggu
    
    if weekday == 5:  # Sabtu
        return random.uniform(1.2, 1.4)
    elif weekday == 6:  # Minggu
        return random.uniform(1.1, 1.3)
    elif weekday in [0, 1, 2, 3]:  # Senin-Kamis
        return random.uniform(0.9, 1.1)
    else:  # Jumat
        return random.uniform(1.0, 1.2)

def get_weather_multiplier():
    """Simulasi pengaruh cuaca terhadap lalu lintas"""
    weather_conditions = [
        ("sunny", 1.0, 0.7),      # Cerah - probabilitas tinggi
        ("cloudy", 0.95, 0.2),    # Berawan - sedikit menurun
        ("rainy", 0.7, 0.1),      # Hujan - menurun drastis
    ]
    
    condition, multiplier, probability = random.choices(
        weather_conditions, 
        weights=[w[2] for w in weather_conditions]
    )[0]
    
    # Tambahkan variasi random pada multiplier
    return multiplier * random.uniform(0.8, 1.2)

start_date = datetime(2025, 6, 3).date()
end_date = datetime.now().date()

# Generate dan masukkan data ke database untuk setiap hari
current_date = start_date
while current_date <= end_date:
    print(f"Memproses data untuk tanggal: {current_date}")
    
    # Dapatkan multiplier harian
    daily_multiplier = get_daily_multiplier(current_date)
    weather_multiplier = get_weather_multiplier()
    
    for jam_str, base_total in base_traffic_pattern.items():
        # Variasi random yang lebih besar (±20-30%)
        hourly_variation = random.uniform(0.7, 1.3)
        
        # Variasi khusus untuk jam tertentu
        hour = int(jam_str.split(':')[0])
        if hour in [6, 7, 8, 17, 18, 19]:  # Rush hour
            rush_variation = random.uniform(1.1, 1.4)
        elif hour in [0, 1, 2, 3, 4, 5]:  # Tengah malam
            rush_variation = random.uniform(0.5, 0.9)
        else:
            rush_variation = random.uniform(0.9, 1.1)
        
        # Hitung total kendaraan dengan semua variasi
        final_total = int(base_total * daily_multiplier * weather_multiplier * 
                         hourly_variation * rush_variation)
        
        # Pastikan minimal ada beberapa kendaraan
        final_total = max(final_total, random.randint(5, 20))
        
        # Buat rentang waktu
        start_time = datetime.combine(current_date, datetime.strptime(jam_str, "%H:%M").time())
        end_time = start_time + timedelta(hours=1) - timedelta(seconds=1)
        
        # Generate timestamp acak
        timestamps = generate_random_timestamps(start_time, end_time, final_total)
        
        # Generate distribusi kendaraan yang berubah setiap jam
        vehicle_dist = get_random_vehicle_distribution()
        
        # Insert data ke database
        for ts in timestamps:
            # Pilih jenis kendaraan secara random
            vehicle_type = random.choices(
                list(vehicle_dist.keys()),
                weights=list(vehicle_dist.values())
            )[0]
            
            # Tambahkan sedikit noise pada jenis kendaraan
            if random.random() < 0.05:  # 5% kemungkinan tipe berubah
                vehicle_type = random.choice(list(vehicle_dist.keys()))
            
            # Masukkan data ke database
            sql = "INSERT INTO vehicle_detections (timestamp, vehicle_type) VALUES (%s, %s)"
            cursor.execute(sql, (ts.strftime('%Y-%m-%d %H:%M:%S'), vehicle_type))
        
        # Commit setiap jam untuk efisiensi
        db.commit()
        
        print(f"  Jam {jam_str}: {final_total} kendaraan (Multiplier: {daily_multiplier:.2f} x {weather_multiplier:.2f})")
    
    # Pindah ke hari berikutnya
    current_date += timedelta(days=1)
    print(f"Selesai memproses {current_date - timedelta(days=1)}\n")

# Tutup koneksi database
cursor.close()
db.close()
print("Data berhasil diinput ke database dengan variasi random yang realistis!")