from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# Fungsi query helper
def query_db(query, args=(), one=False):
    try:
        with mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="detection"
        ) as db:
            with db.cursor(dictionary=True) as cursor:
                cursor.execute(query, args)
                result = cursor.fetchall()
                return (result[0] if result else None) if one else result
    except Exception as e:
        return {"error": str(e)}

# Fungsi bantu response JSON
def make_response(data):
    if isinstance(data, dict) and "error" in data:
        return jsonify(data), 500
    return jsonify(data)

# API summary: today, yesterday, all
@app.route('/api/vehicle_count/summary', methods=['GET'])
def vehicle_summary():
    scope = request.args.get('scope', 'today')

    if scope == 'today':
        query = """
            SELECT vehicle_type, COUNT(*) as count 
            FROM vehicle_detections 
            WHERE DATE(timestamp) = CURDATE() 
            GROUP BY vehicle_type
        """
    elif scope == 'yesterday':
        query = """
            SELECT vehicle_type, COUNT(*) as count 
            FROM vehicle_detections 
            WHERE DATE(timestamp) = CURDATE() - INTERVAL 1 DAY 
            GROUP BY vehicle_type
        """
    elif scope == 'all':
        query = """
            SELECT vehicle_type, COUNT(*) as count 
            FROM vehicle_detections 
            GROUP BY vehicle_type
        """
    else:
        return jsonify({"error": "Invalid scope"}), 400

    result = query_db(query)
    return make_response(result)

# API time series: hourly (today), last_15min, history
@app.route('/api/vehicle_count/time_series', methods=['GET'])
def vehicle_time_series():
    type_ = request.args.get('type', 'hourly')

    if type_ == 'hourly':
        query = """
            SELECT HOUR(timestamp) as hour, COUNT(*) as count 
            FROM vehicle_detections 
            WHERE DATE(timestamp) = CURDATE() 
            GROUP BY HOUR(timestamp)
            ORDER BY hour
        """
    elif type_ == 'last_15min':
        query = """
            SELECT vehicle_type, COUNT(*) as count 
            FROM vehicle_detections 
            WHERE timestamp >= NOW() - INTERVAL 15 MINUTE 
            GROUP BY vehicle_type
        """
    elif type_ == 'history':
        query = """
            SELECT DATE(timestamp) as date, 
                    HOUR(timestamp) as hour, 
                    FLOOR(MINUTE(timestamp) / 15) * 15 as minute_interval, 
                    vehicle_type, 
                    COUNT(*) as count 
            FROM vehicle_detections 
            GROUP BY DATE(timestamp), HOUR(timestamp), minute_interval, vehicle_type
            ORDER BY date, hour, minute_interval
        """
    else:
        return jsonify({"error": "Invalid type parameter"}), 400

    result = query_db(query)
    return make_response(result)

# API detail kendaraan berdasarkan ID
@app.route('/api/vehicle_count/details/<int:vehicle_id>', methods=['GET'])
def get_vehicle_details(vehicle_id):
    if vehicle_id <= 0:
        return jsonify({"error": "Invalid vehicle ID"}), 400

    result = query_db(
        "SELECT * FROM vehicle_detections WHERE id = %s",
        (vehicle_id,), one=True
    )

    if isinstance(result, dict) and "error" in result:
        return jsonify(result), 500
    elif result:
        return jsonify(result)
    else:
        return jsonify({"error": "Vehicle not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
