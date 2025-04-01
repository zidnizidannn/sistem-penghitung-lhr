from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

def conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="detection"
    )

@app.route('/api/vehicle_count', methods=['GET'])
def get_vehicle_count():
    try:
        db = conn()
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT vehicle_type, COUNT(*) as count 
        FROM vehicle_detections GROUP BY vehicle_type
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vehicle_count/last_24h', methods=['GET'])
def get_vehicle_count_last_24h():
    try:
        db = conn()
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT vehicle_type, COUNT(*) as count FROM vehicle_detections 
        WHERE timestamp >= NOW() - INTERVAL 1 DAY GROUP BY vehicle_type
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/vehicle_count/today', methods=['GET'])
def get_vehicle_count_today():
    try:
        db = conn()
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT vehicle_type, COUNT(*) as count FROM vehicle_detections 
        WHERE DATE(timestamp) = CURDATE() GROUP BY vehicle_type
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vehicle_count/last_15min', methods=['GET'])
def get_vehicle_count_last_15min():
    try:
        db = conn()
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT vehicle_type, COUNT(*) as count FROM vehicle_detections 
        WHERE timestamp >= NOW() - INTERVAL 15 MINUTE GROUP BY vehicle_type
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/vehicle_count/last_15min_today', methods=['GET'])
def get_vehicle_count_last_15min_today():
    try:
        db = conn()
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT vehicle_type, COUNT(*) as count FROM vehicle_detections 
        WHERE timestamp >= NOW() - INTERVAL 15 MINUTE AND DATE(timestamp) = CURDATE() GROUP BY vehicle_type
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vehicle_count/history', methods=['GET'])
def get_historical_data():
    try:
        db = conn()
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT DATE(timestamp) as date, HOUR(timestamp) as hour, vehicle_type, COUNT(*) as count 
        FROM vehicle_detections 
        GROUP BY DATE(timestamp), HOUR(timestamp), vehicle_type
        ORDER BY date, hour
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/vehicle_count/yesterday', methods=['GET'])
def get_vehicle_count_yesterday():
    try:
        db = conn()
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT vehicle_type, COUNT(*) as count 
        FROM vehicle_detections 
        WHERE DATE(timestamp) = CURDATE() - INTERVAL 1 DAY 
        GROUP BY vehicle_type
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vehicle_count/details/<int:vehicle_id>', methods=['GET'])
def get_vehicle_details(vehicle_id):
    try:
        db = conn()
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT * 
        FROM vehicle_detections 
        WHERE id = %s
        """
        cursor.execute(query, (vehicle_id,))
        result = cursor.fetchone()
        cursor.close()
        db.close()
        if result:
            return jsonify(result)
        else:
            return jsonify({"error": "Vehicle not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)