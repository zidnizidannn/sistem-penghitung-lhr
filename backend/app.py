from flask import Flask, jsonify, request, Response, abort
from flask_cors import CORS
import mysql.connector
from flask import Flask, send_file, jsonify, request
from io import BytesIO
from datetime import datetime, timedelta, date
import pandas as pd
from helper.conn import conn as query_db
from helper.detection import detect
from threading import Thread
from collections import defaultdict

app = Flask(__name__)
CORS(app)

# Fungsi bantu response JSON
def make_response(data):
    if isinstance(data, dict) and "error" in data:
        return jsonify(data), 500
    return jsonify(data)

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
    elif scope == 'weekly':
        query = """
            SELECT vehicle_type, COUNT(*) as count 
            FROM vehicle_detections 
            WHERE timestamp >= CURDATE() - INTERVAL 7 DAY
            GROUP BY vehicle_type
        """
    elif scope == 'monthly':
        try:
            year = int(request.args.get('year', datetime.now().year))
            month = int(request.args.get('month', datetime.now().month))
            
            query = f"""
                SELECT vehicle_type, COUNT(*) as count 
                FROM vehicle_detections 
                WHERE YEAR(timestamp) = {year} AND MONTH(timestamp) = {month}
                GROUP BY vehicle_type
            """
            
        except Exception as e:
            return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    elif scope == 'custom':
        date_str = request.args.get('date')
        if date_str:
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except:
                return jsonify({"error": "Invalid date format"}), 400

            query = f"""
                SELECT vehicle_type, COUNT(*) as count 
                FROM vehicle_detections 
                WHERE DATE(timestamp) = '{date_str}' 
                GROUP BY vehicle_type
            """
        elif all(param in request.args for param in ['year', 'month', 'week']):
            try:
                year = int(request.args.get('year'))
                month = int(request.args.get('month'))
                week = int(request.args.get('week'))

                start_day = (week - 1) * 7 + 1
                start_date = datetime(year, month, start_day)

                try:
                    end_date = datetime(year, month, start_day + 6)
                except ValueError:
                    if month == 12:
                        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                    else:
                        end_date = datetime(year, month + 1, 1) - timedelta(days=1)

                query = f"""
                    SELECT vehicle_type, COUNT(*) as count 
                    FROM vehicle_detections 
                    WHERE DATE(timestamp) BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
                    GROUP BY vehicle_type
                """
            except Exception as e:
                return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    else:
        return jsonify({"error": "Invalid scope"}), 400

    result = query_db(query)
    for item in result:
        vtype = item['vehicle_type']
        count = item['count']
        if vtype == 'motorcycle':
            item['smp'] = count * 0.5
        elif vtype == 'car':
            item['smp'] = count * 1
        elif vtype == 'bus':
            item['smp'] = count * 1.3
        elif vtype == 'truck':
            item['smp'] = count * 1.3
        else:
            item['smp'] = count
    return make_response(result)

@app.route('/api/vehicle_count/time_series', methods=['GET'])
def vehicle_time_series():
    type_ = request.args.get('type', 'hourly')

    if type_ == 'hourly':
        date_str = request.args.get('date')
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')

        query = f"""
            SELECT HOUR(timestamp) as hour, vehicle_type, COUNT(*) as count 
            FROM vehicle_detections 
            WHERE DATE(timestamp) = '{date_str}' 
            GROUP BY HOUR(timestamp)
            ORDER BY hour
        """
        rows = query_db(query)
    
        if isinstance(rows, dict) and "error" in rows:
            return make_response(rows)
        
        result = defaultdict(lambda: {"motor": 0, "mobil": 0, "bus": 0, "truk": 0, "total": 0, "smp": 0})
        
        for row in rows:
            hour = row["hour"]
            vtype = row["vehicle_type"]
            count = row["count"]
            
            if vtype == "motorcycle":
                result[hour]["motor"] += count
                result[hour]["smp"] += count * 0.5
            elif vtype == "car":
                result[hour]["mobil"] += count
                result[hour]["smp"] += count * 1
            elif vtype == "bus":
                result[hour]["bus"] += count
                result[hour]["smp"] += count * 1.3
            elif vtype == "truck":
                result[hour]["truk"] += count
                result[hour]["smp"] += count * 1.3
                
            result[hour]["total"] += count
        
        data = []
        for hour in range(24):
            data.append({
                "hour": hour,
                "motor": result[hour]["motor"],
                "mobil": result[hour]["mobil"], 
                "bus": result[hour]["bus"],
                "truk": result[hour]["truk"],
                "total": result[hour]["total"],
                "smp": round(result[hour]["smp"], 1)
            })
        
        return make_response(data)
    
    # elif type_ == 'last_15min':
    #     query = """
    #         SELECT vehicle_type, COUNT(*) as count 
    #         FROM vehicle_detections 
    #         WHERE timestamp >= NOW() - INTERVAL 15 MINUTE 
    #         GROUP BY vehicle_type
    #     """
    elif type_ == 'quarter':
        try:
            date_str = request.args.get('date')
            if not date_str:
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            query = f"""
                SELECT
                    TIME_FORMAT(
                        SEC_TO_TIME(
                            FLOOR(TIME_TO_SEC(TIME(timestamp)) / 900) * 900
                        ), 
                        '%H:%i'
                    ) as time_interval,
                    vehicle_type,
                    COUNT(*) as count
                FROM vehicle_detections
                WHERE DATE(timestamp) = '{date_str}'
                GROUP BY time_interval, vehicle_type
                ORDER BY time_interval
            """
            rows = query_db(query)

            result = defaultdict(lambda: {"motor": 0, "mobil": 0, "bus": 0, "truk": 0, "total": 0, "smp": 0.0})

            for row in rows:
                interval = row["time_interval"]
                vtype = row["vehicle_type"]
                count = row["count"]

                if vtype == "motorcycle":
                    result[interval]["motor"] += count
                    result[interval]["smp"] += count * 0.5
                elif vtype == "car":
                    result[interval]["mobil"] += count
                    result[interval]["smp"] += count * 1
                elif vtype == "bus":
                    result[interval]["bus"] += count
                    result[interval]["smp"] += count * 1.3
                elif vtype == "truck":
                    result[interval]["truk"] += count
                    result[interval]["smp"] += count * 1.3

                result[interval]["total"] += count

            data = [{"time_interval": k, **v, "smp": round(v["smp"], 1)} for k, v in result.items()]
            return make_response(data)

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    elif type_ == 'weekly':
        try:
            year = int(request.args.get('year'))
            month = int(request.args.get('month'))
            week = int(request.args.get('week'))

            start_day = (week - 1) * 7 + 1
            start_date = datetime(year, month, start_day)
            try:
                end_date = datetime(year, month, start_day + 6)
            except ValueError:
                if month == 12:
                    end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = datetime(year, month + 1, 1) - timedelta(days=1)

            query = f"""
                SELECT DATE(timestamp) as date,vehicle_type,COUNT(*) as count
                FROM vehicle_detections
                WHERE DATE(timestamp) BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
                GROUP BY DATE(timestamp), vehicle_type
                ORDER BY date
            """
            rows = query_db(query)

            result = defaultdict(lambda: {"motor": 0, "mobil": 0, "bus": 0, "truk": 0, "total": 0, "smp": 0.0})

            for row in rows:
                date = row["date"]
                vtype = row["vehicle_type"]
                count = row["count"]

                if vtype == "motorcycle":
                    result[date]["motor"] += count
                    result[date]["smp"] += count * 0.5
                elif vtype == "car":
                    result[date]["mobil"] += count
                    result[date]["smp"] += count * 1
                elif vtype in ["bus"]:
                    result[date]["bus"] += count
                    result[date]["smp"] += count * 1.3
                elif vtype in ["truck"]:
                    result[date]["truk"] += count
                    result[date]["smp"] += count * 1.3

                result[date]["total"] += count

            data = [{"date": k, **v, "smp": round(v["smp"], 1)} for k, v in result.items()]
            return make_response(data)

        except Exception as e:
            return jsonify({"error": str(e)}), 400
        
    elif type_ == 'monthly':
        try:
            year = int(request.args.get('year', datetime.now().year))
            month = int(request.args.get('month', datetime.now().month))
            
            from calendar import monthrange
            _, last_day = monthrange(year, month)
            
            start_date = f"{year}-{month:02d}-01"
            end_date = f"{year}-{month:02d}-{last_day:02d}"
            
            query = f"""
                SELECT 
                    DATE(timestamp) as date,
                    vehicle_type, 
                    COUNT(*) as count
                FROM vehicle_detections 
                WHERE DATE(timestamp) BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY DATE(timestamp), vehicle_type
                ORDER BY date
            """
            
            rows = query_db(query)
            
            if isinstance(rows, dict) and "error" in rows:
                return make_response(rows)
            
            result = defaultdict(lambda: {"motor": 0, "mobil": 0, "bus": 0, "truk": 0, "total": 0, "smp": 0.0})
            
            for row in rows:
                date = row["date"]
                vtype = row["vehicle_type"]
                count = row["count"]
                
                if vtype == "motorcycle":
                    result[date]["motor"] += count
                    result[date]["smp"] += count * 0.5
                elif vtype == "car":
                    result[date]["mobil"] += count
                    result[date]["smp"] += count *1
                elif vtype in ["bus"]:
                    result[date]["bus"] += count
                    result[date]["smp"] += count * 1.3
                elif vtype in ["truck"]:
                    result[date]["truk"] += count
                    result[date]["smp"] += count * 1.3
                    
                result[date]["total"] += count
            
            data = []
            current_date = datetime(year, month, 1)
            
            for day in range(1, last_day + 1):
                date_key = current_date.replace(day=day).date()
                data.append({
                    "date": date_key.strftime('%Y-%m-%d'),
                    "day": day,
                    "motor": result[date_key]["motor"],
                    "mobil": result[date_key]["mobil"], 
                    "bus": result[date_key]["bus"],
                    "truk": result[date_key]["truk"],
                    "total": result[date_key]["total"],
                    "smp": round(result[date_key]["smp"], 1)
                })
            return make_response(data)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 400

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

    return make_response(result)

@app.route('/api/video_feed')
def video_feed():
    if not running['running']:
        abort(403, "Detection is not running.")
    return Response(detect(running),mimetype='multipart/x-mixed-replace; boundary=frame')

running = {'running': False}

@app.route('/api/start_detection', methods=['POST'])
def start_detection():
    if running['running']:
        return jsonify({"message": "Detection already running"}), 400

    running['running'] = True
    return jsonify({"message": "Detection started"}), 200

@app.route('/api/stop_detection', methods=['POST'])
def stop_detection():
    if not running['running']:
        return jsonify({"message": "Detection not running"}), 400

    running['running'] = False
    return jsonify({"message": "Detection stopped"}), 200

from helper.reportGenerator import generate_report_pdf
import os

@app.route('/api/download_report/pdf', methods=['GET'])
def download_report_pdf():
    scope = request.args.get('scope', 'weekly') # default 'weekly', bisa 'daily', 'monthly'
    
    vehicle_type_map_display = {
        "motorcycle": "Motorcycle",
        "car": "Car",
        "bus": "Bus",
        "truck": "Truck"
    }

    summary_data_for_pdf = []
    time_series_data_for_pdf = []
    report_period_str = "Periode Tidak Diketahui"
    report_type_display = scope.capitalize() # "Daily", "Weekly", "Monthly"
    busiest_period_info = "Informasi periode tersibuk belum diimplementasikan."
    
    filename_suffix = scope
    start_date_for_filename = datetime.now()


    try:
        if scope == 'daily':
            date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
            selected_date = datetime.strptime(date_str, '%Y-%m-%d')
            start_date_for_filename = selected_date
            report_period_str = f"Tanggal: {selected_date.strftime('%d %b %Y')}"
            report_type_display = "HARIAN"

            # 1. Fetch Summary Data for Daily
            summary_query = f"""
                SELECT vehicle_type, COUNT(*) as count 
                FROM vehicle_detections 
                WHERE DATE(timestamp) = '{date_str}' 
                GROUP BY vehicle_type
            """
            summary_raw = query_db(summary_query)
            if isinstance(summary_raw, dict) and "error" in summary_raw: return jsonify(summary_raw), 500
            summary_data_for_pdf = [{"vehicle_type": vehicle_type_map_display.get(item['vehicle_type'], item['vehicle_type']), "count": item['count']} for item in summary_raw]

            # 2. Fetch Time Series Data for Daily (per jam)
            ts_query = f"""
                SELECT HOUR(timestamp) as hour, vehicle_type, COUNT(*) as count 
                FROM vehicle_detections 
                WHERE DATE(timestamp) = '{date_str}' 
                GROUP BY HOUR(timestamp), vehicle_type ORDER BY hour
            """
            ts_raw = query_db(ts_query)
            if isinstance(ts_raw, dict) and "error" in ts_raw: return jsonify(ts_raw), 500
            
            hourly_data_aggregated = defaultdict(lambda: {v_type: 0 for v_type in vehicle_type_map_display.values()})
            for row in ts_raw:
                hour = row['hour']
                v_type_db = row['vehicle_type']
                v_type_display = vehicle_type_map_display.get(v_type_db, v_type_db)
                hourly_data_aggregated[hour][v_type_display] += row['count']
            
            max_total_kendaraan_jam = -1
            jam_tersibuk = -1

            for hour in range(24):
                data_per_jam = {"Waktu_Label": f"{hour:02d}:00"}
                total_kendaraan_per_jam = 0
                for v_type_display in vehicle_type_map_display.values():
                    count = hourly_data_aggregated[hour].get(v_type_display, 0)
                    data_per_jam[v_type_display] = count
                    total_kendaraan_per_jam += count
                data_per_jam["Total"] = total_kendaraan_per_jam
                time_series_data_for_pdf.append(data_per_jam)

                if total_kendaraan_per_jam > max_total_kendaraan_jam:
                    max_total_kendaraan_jam = total_kendaraan_per_jam
                    jam_tersibuk = hour
            
            if jam_tersibuk != -1:
                busiest_period_info = f"Jam tersibuk: {jam_tersibuk:02d}:00 - {(jam_tersibuk+1):02d}:00 dengan {max_total_kendaraan_jam:,} kendaraan."
            else:
                busiest_period_info = "Tidak ada data kendaraan pada hari ini."


        elif scope == 'weekly':
            year = int(request.args.get('year', datetime.now().year))
            month = int(request.args.get('month', datetime.now().month))
            week = int(request.args.get('week')) # Wajib ada untuk mingguan

            start_day_of_month = (week - 1) * 7 + 1
            try:
                current_month_start = datetime(year, month, 1)
                start_date = datetime(year, month, start_day_of_month)
            except ValueError: # Jika start_day_of_month tidak valid
                first_day_of_target_month = datetime(year, month, 1)
                start_date = datetime(year, month, start_day_of_month)

            try:
                end_date = datetime(year, month, start_day_of_month + 6)
            except ValueError:
                if month == 12:
                    end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            
            start_date_for_filename = start_date
            report_period_str = f"Periode: {start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}"
            report_type_display = "MINGGUAN"

            # 1. Fetch Summary Data for Weekly
            summary_query = f"""
                SELECT vehicle_type, COUNT(*) as count 
                FROM vehicle_detections 
                WHERE DATE(timestamp) BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}' 
                GROUP BY vehicle_type
            """
            summary_raw = query_db(summary_query)
            if isinstance(summary_raw, dict) and "error" in summary_raw: return jsonify(summary_raw), 500
            summary_data_for_pdf = [{"vehicle_type": vehicle_type_map_display.get(item['vehicle_type'], item['vehicle_type']), "count": item['count']} for item in summary_raw]

            # 2. Fetch Time Series Data for Weekly (per hari)
            ts_query = f"""
                SELECT DATE(timestamp) as date, vehicle_type, COUNT(*) as count 
                FROM vehicle_detections 
                WHERE DATE(timestamp) BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}' 
                GROUP BY DATE(timestamp), vehicle_type ORDER BY date
            """
            ts_raw = query_db(ts_query)
            if isinstance(ts_raw, dict) and "error" in ts_raw: return jsonify(ts_raw), 500

            daily_data_aggregated = defaultdict(lambda: {v_type: 0 for v_type in vehicle_type_map_display.values()})
            
            # Inisialisasi semua hari dalam rentang minggu
            current_d = start_date
            while current_d <= end_date:
                _ = daily_data_aggregated[current_d.strftime('%Y-%m-%d')] # pastikan ada key
                current_d += timedelta(days=1)

            for row in ts_raw:
                date_val_str = row['date'].strftime('%Y-%m-%d') if isinstance(row['date'], (datetime, date)) else str(row['date'])
                v_type_db = row['vehicle_type']
                v_type_display = vehicle_type_map_display.get(v_type_db, v_type_db)
                daily_data_aggregated[date_val_str][v_type_display] += row['count']
            
            max_total_kendaraan_hari = -1
            hari_tersibuk_str = ""

            sorted_dates = sorted(daily_data_aggregated.keys())

            for date_str_key in sorted_dates:
                date_obj = datetime.strptime(date_str_key, '%Y-%m-%d')
                data_per_hari = {"Tanggal": date_obj.strftime('%d %b %Y')}
                total_kendaraan_per_hari = 0
                for v_type_display in vehicle_type_map_display.values():
                    count = daily_data_aggregated[date_str_key].get(v_type_display, 0)
                    data_per_hari[v_type_display] = count
                    total_kendaraan_per_hari += count
                data_per_hari["Total"] = total_kendaraan_per_hari
                time_series_data_for_pdf.append(data_per_hari)

                if total_kendaraan_per_hari > max_total_kendaraan_hari:
                    max_total_kendaraan_hari = total_kendaraan_per_hari
                    hari_tersibuk_str = date_obj.strftime('%d %b %Y')
            
            if hari_tersibuk_str:
                busiest_period_info = f"Hari tersibuk: {hari_tersibuk_str} dengan {max_total_kendaraan_hari:,} kendaraan."
            else:
                busiest_period_info = "Tidak ada data kendaraan pada minggu ini."


        elif scope == 'monthly':
            year = int(request.args.get('year', datetime.now().year))
            month = int(request.args.get('month', datetime.now().month))
            
            from calendar import monthrange
            _, last_day_of_month = monthrange(year, month)
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month, last_day_of_month)
            start_date_for_filename = start_date

            report_period_str = f"Bulan: {start_date.strftime('%B %Y')}"
            report_type_display = "BULANAN"

            # 1. Fetch Summary Data for Monthly
            summary_query = f"""
                SELECT vehicle_type, COUNT(*) as count 
                FROM vehicle_detections 
                WHERE YEAR(timestamp) = {year} AND MONTH(timestamp) = {month}
                GROUP BY vehicle_type
            """
            summary_raw = query_db(summary_query)
            if isinstance(summary_raw, dict) and "error" in summary_raw: return jsonify(summary_raw), 500
            summary_data_for_pdf = [{"vehicle_type": vehicle_type_map_display.get(item['vehicle_type'], item['vehicle_type']), "count": item['count']} for item in summary_raw]

            # 2. Fetch Time Series Data for Monthly (per hari)
            ts_query = f"""
                SELECT DATE(timestamp) as date, vehicle_type, COUNT(*) as count 
                FROM vehicle_detections 
                WHERE YEAR(timestamp) = {year} AND MONTH(timestamp) = {month}
                GROUP BY DATE(timestamp), vehicle_type ORDER BY date
            """
            ts_raw = query_db(ts_query)
            if isinstance(ts_raw, dict) and "error" in ts_raw: return jsonify(ts_raw), 500
            
            daily_data_aggregated = defaultdict(lambda: {v_type: 0 for v_type in vehicle_type_map_display.values()})
            
            current_d = start_date
            while current_d <= end_date:
                _ = daily_data_aggregated[current_d.strftime('%Y-%m-%d')]
                current_d += timedelta(days=1)

            for row in ts_raw:
                date_val_str = row['date'].strftime('%Y-%m-%d') if isinstance(row['date'], datetime) or isinstance(row['date'], date) else str(row['date'])
                v_type_db = row['vehicle_type']
                v_type_display = vehicle_type_map_display.get(v_type_db, v_type_db)
                daily_data_aggregated[date_val_str][v_type_display] += row['count']

            max_total_kendaraan_hari = -1
            hari_tersibuk_str = ""
            
            sorted_dates = sorted(daily_data_aggregated.keys())

            for date_str_key in sorted_dates:
                date_obj = datetime.strptime(date_str_key, '%Y-%m-%d')
                data_per_hari = {
                    "Tanggal": date_obj.strftime('%d %b %Y'),
                    "Tanggal_Simple": date_obj.strftime('%d')
                }
                total_kendaraan_per_hari = 0
                for v_type_display in vehicle_type_map_display.values():
                    count = daily_data_aggregated[date_str_key].get(v_type_display, 0)
                    data_per_hari[v_type_display] = count
                    total_kendaraan_per_hari += count
                data_per_hari["Total"] = total_kendaraan_per_hari
                time_series_data_for_pdf.append(data_per_hari)

                if total_kendaraan_per_hari > max_total_kendaraan_hari:
                    max_total_kendaraan_hari = total_kendaraan_per_hari
                    hari_tersibuk_str = date_obj.strftime('%d %b %Y')
            
            if hari_tersibuk_str:
                busiest_period_info = f"Hari tersibuk: {hari_tersibuk_str} dengan {max_total_kendaraan_hari:,} kendaraan."
            else:
                busiest_period_info = "Tidak ada data kendaraan pada bulan ini."

        else:
            return jsonify({"error": "Invalid scope parameter. Use 'daily', 'weekly', or 'monthly'."}), 400

        pdf_bytes = generate_report_pdf(
            report_type_display=report_type_display,
            summary_data=summary_data_for_pdf,
            time_series_data=time_series_data_for_pdf,
            report_period_str=report_period_str,
            busiest_period_info=busiest_period_info,
        )
        
        if scope == 'monthly':
            tahun = start_date_for_filename.strftime('%Y')
            bulan = start_date_for_filename.strftime('%B')
            file_download_name = f"LAPORAN LHR BULAN {bulan} TAHUN {tahun}.pdf"

        elif scope == 'weekly':
            bulan = start_date_for_filename.strftime('%B')
            minggu = int(request.args.get('week'))
            file_download_name = f"LAPORAN LHR MINGGU KE-{minggu} BULAN {bulan}.pdf"

        elif scope == 'daily':
            tanggal = start_date_for_filename.strftime('%d-%m-%Y')
            file_download_name = f"LAPORAN LHR TANGGAL {tanggal}.pdf"

        else:
            file_download_name = f"laporan_lhr_{report_type_display.lower()}.pdf"

        # Buat nama file yang dinamis
        # file_download_name = f"Laporan_LHR_{report_type_display}_{start_date_for_filename.strftime('%Y%m%d')}.pdf"

        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=file_download_name
        )

    except ValueError as ve:
        app.logger.error(f"ValueError during PDF report generation: {str(ve)}")
        return jsonify({"error": f"Input tidak valid: {str(ve)}"}), 400
    except Exception as e:
        app.logger.error(f"Error generating PDF report: {str(e)}", exc_info=True)
        return jsonify({"error": f"Gagal membuat laporan PDF: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
