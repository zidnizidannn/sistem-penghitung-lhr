import cv2
import numpy as np
import tensorflow.lite as tflite  # atau gunakan tensorflow.lite jika di PC
# import tensorflow.lite as tflite  # alternatif jika tidak pakai tflite_runtime

# Path model TFLite kamu
MODEL_PATH = "yolov8/train4/weights/best_int8.tflite"

# Inisialisasi model
interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

# Dapatkan info input/output
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

input_index = input_details[0]['index']
output_index = output_details[0]['index']
input_shape = input_details[0]['shape']  # biasanya [1, 640, 640, 3]

print(f"Input shape: {input_shape}")

# Baca satu frame dari webcam (atau bisa ganti jadi dari file)
cap = cv2.VideoCapture("backend\yolov8\cctv1.mp4")
ret, frame = cap.read()
cap.release()

if not ret:
    raise RuntimeError("Gagal membaca frame dari webcam")

# Preprocessing: resize, RGB, expand dims, convert to uint8
img = cv2.resize(frame, (input_shape[2], input_shape[1]))
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
input_data = np.expand_dims(img_rgb, axis=0).astype(np.uint8)  # int8 model pakai uint8 input

# Inference
interpreter.set_tensor(input_index, input_data)
interpreter.invoke()
output_data = interpreter.get_tensor(output_index)

# Postprocessing (asumsikan output shape [1, N, 6] = [x1, y1, x2, y2, conf, class])
detections = output_data[0]
print("Deteksi:")
for det in detections:
    x1, y1, x2, y2, conf, cls = det
    if conf > 0.4:
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        cls = int(cls)
        print(f"Class {cls} | Conf: {conf:.2f} | Box: ({x1}, {y1}, {x2}, {y2})")

        # Tampilkan ke gambar
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, f"{cls}: {conf:.2f}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

# Tampilkan hasil
cv2.imshow("TFLite YOLOv8 INT8 Detection", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
