from io import BytesIO
from fpdf import FPDF
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib
import os
import numpy as np

matplotlib.use('Agg')

class TransportationReportPDF(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.set_auto_page_break(auto=True, margin=25)
        self.set_margins(left=15, top=20, right=15)
        
    def header(self):
        # Department heading
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'PEMERINTAH KOTA MADIUN', ln=1, align='C')
        self.cell(0, 10, 'DINAS PERHUBUNGAN', ln=1, align='C')
        self.set_font('Arial', '', 10)
        self.cell(0, 6, 'Jl. Jalan Raya No. 123, Telepon: (0123) 456789', ln=1, align='C')
        self.cell(0, 6, 'Email: dishub@example.go.id - Website: www.dishub.example.go.id', ln=1, align='C')
        
        # Line break
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)
    
    def footer(self):
        # Go to 1.5 cm from bottom
        self.set_y(-15)
        self.set_font('Arial', '', 8)
        # Page number
        self.cell(0, 10, f'Halaman {self.page_no()}', 0, 0, 'C')
        # Timestamp
        self.set_x(10)
        self.cell(0, 10, f'Dicetak pada: {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}', 0, 0, 'L')
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, ln=1)
        self.ln(1)
        
    def chapter_subtitle(self, subtitle):
        self.set_font('Arial', 'B', 11)
        self.cell(0, 8, subtitle, ln=1)
        self.ln(1)
        
    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, body)
        self.ln()
    
    def add_table(self, headers, data, col_widths=None):
        # Default column widths if not specified
        if col_widths is None:
            col_widths = [self.w / len(headers) - 10] * len(headers)
            
        line_height = 8
        
        # Table headers
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(200, 200, 200)  # Light gray background
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], line_height, header, border=1, fill=True)
        self.ln()
        
        # Table data
        self.set_font('Arial', '', 10)
        self.set_fill_color(255, 255, 255)  # White background
        
        for row in data:
            for i, cell in enumerate(row):
                self.cell(col_widths[i], line_height, str(cell), border=1)
            self.ln()
        
        self.ln(5)
    
    def add_chart(self, chart_path, title, width=120):
        self.chapter_subtitle(title)
        
        # Get aspect ratio from image
        img_width, img_height = plt.gcf().get_size_inches()
        aspect = img_height / img_width
        
        # Calculate height based on aspect ratio
        height = width * aspect
        
        # Center the image
        x = (self.w - width) / 2
        
        self.image(chart_path, x=x, y=self.get_y(), w=width)
        self.ln(height + 10)  # Add space after chart
    
    def add_signature_box(self, location, name, position, nip=None):
        self.set_font('Arial', '', 10)
        self.cell(0, 6, f"{location}, {datetime.now().strftime('%d %B %Y')}", ln=1, align='R')
        self.cell(0, 6, position, ln=1, align='R')
        self.ln(15)  # Space for signature
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, name, ln=1, align='R')
        if nip:
            self.set_font('Arial', '', 10)
            self.cell(0, 6, f"NIP. {nip}", ln=1, align='R')


def generateReport(report_type, db_config):
    pdf = TransportationReportPDF()
    pdf.add_page()
    
    # Report Title
    if report_type == 'daily':
        title = f"LAPORAN HARIAN VOLUME LALU LINTAS"
        subtitle = f"Tanggal: {datetime.now().strftime('%d %B %Y')}"
        period = "Hari Ini"
    elif report_type == 'weekly':
        end_date = datetime.now()
        start_date = end_date - timedelta(days=6)
        title = f"LAPORAN MINGGUAN VOLUME LALU LINTAS"
        subtitle = f"Periode: {start_date.strftime('%d %B %Y')} s/d {end_date.strftime('%d %B %Y')}"
        period = "Minggu Ini"
    elif report_type == 'monthly':
        title = f"LAPORAN BULANAN VOLUME LALU LINTAS"
        subtitle = f"Bulan: {datetime.now().strftime('%B %Y')}"
        period = "Bulan Ini"
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, title, ln=1, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, subtitle, ln=1, align='C')
    pdf.ln(5)
    
    # Fetch data from database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    if report_type == 'daily':
        query = """
            SELECT vehicle_type, COUNT(*) as count 
            FROM vehicle_detections 
            WHERE DATE(timestamp) = CURDATE() 
            GROUP BY vehicle_type
        """
        total_query = """
            SELECT COUNT(*) as total
            FROM vehicle_detections 
            WHERE DATE(timestamp) = CURDATE()
        """
        time_query = """
            SELECT HOUR(timestamp) as hour, COUNT(*) as count 
            FROM vehicle_detections 
            WHERE DATE(timestamp) = CURDATE() 
            GROUP BY HOUR(timestamp)
            ORDER BY hour
        """
        peak_query = """
            SELECT HOUR(timestamp) as hour, COUNT(*) as count 
            FROM vehicle_detections 
            WHERE DATE(timestamp) = CURDATE() 
            GROUP BY HOUR(timestamp)
            ORDER BY count DESC
            LIMIT 1
        """
    elif report_type == 'weekly':
        query = """
            SELECT vehicle_type, COUNT(*) as count 
            FROM vehicle_detections 
            WHERE timestamp >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
            GROUP BY vehicle_type
        """
        total_query = """
            SELECT COUNT(*) as total
            FROM vehicle_detections 
            WHERE timestamp >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
        """
        time_query = """
            SELECT DATE(timestamp) as date, COUNT(*) as count 
            FROM vehicle_detections 
            WHERE timestamp >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
            GROUP BY DATE(timestamp)
            ORDER BY date
        """
        peak_query = """
            SELECT DATE(timestamp) as date, COUNT(*) as count 
            FROM vehicle_detections 
            WHERE timestamp >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
            GROUP BY DATE(timestamp)
            ORDER BY count DESC
            LIMIT 1
        """
    elif report_type == 'monthly':
        query = """
            SELECT vehicle_type, COUNT(*) as count 
            FROM vehicle_detections 
            WHERE YEAR(timestamp) = YEAR(CURDATE()) AND MONTH(timestamp) = MONTH(CURDATE())
            GROUP BY vehicle_type
        """
        total_query = """
            SELECT COUNT(*) as total
            FROM vehicle_detections 
            WHERE YEAR(timestamp) = YEAR(CURDATE()) AND MONTH(timestamp) = MONTH(CURDATE())
        """
        time_query = """
            SELECT DAY(timestamp) as day, COUNT(*) as count 
            FROM vehicle_detections 
            WHERE YEAR(timestamp) = YEAR(CURDATE()) AND MONTH(timestamp) = MONTH(CURDATE())
            GROUP BY DAY(timestamp)
            ORDER BY day
        """
        peak_query = """
            SELECT DAY(timestamp) as day, COUNT(*) as count 
            FROM vehicle_detections 
            WHERE YEAR(timestamp) = YEAR(CURDATE()) AND MONTH(timestamp) = MONTH(CURDATE())
            GROUP BY DAY(timestamp)
            ORDER BY count DESC
            LIMIT 1
        """
    
    # Execute queries
    pdf.chapter_title("1. RINGKASAN STATISTIK")
    cursor.execute(query)
    vehicle_counts = cursor.fetchall()
    
    cursor.execute(total_query)
    total_count = cursor.fetchone()['total']
    
    cursor.execute(time_query)
    time_data = cursor.fetchall()
    
    cursor.execute(peak_query)
    peak_data = cursor.fetchone()
    
    # Summary text
    pdf.chapter_body(f"Total kendaraan yang terdeteksi pada {period}: {total_count:,} kendaraan.")
    
    # Create summary table
    headers = ["Jenis Kendaraan", "Jumlah", "Persentase"]
    data = []
    
    for item in vehicle_counts:
        percentage = (item['count'] / total_count) * 100 if total_count > 0 else 0
        data.append([
            item['vehicle_type'].capitalize(),
            f"{item['count']:,}",
            f"{percentage:.2f}%"
        ])
    
    # Add row for total
    data.append(["TOTAL", f"{total_count:,}", "100.00%"])
    
    pdf.add_table(headers, data, col_widths=[60, 60, 60])
    
    # 2. Time Distribution
    pdf.chapter_title("2. DISTRIBUSI WAKTU")
    
    # Create time distribution chart for file output
    plt.figure(figsize=(6, 3))
    
    if report_type == 'daily':
        # Fill in missing hours with zero
        hours = [item['hour'] for item in time_data]
        all_hours = list(range(24))
        missing_hours = set(all_hours) - set(hours)
        
        for hour in missing_hours:
            time_data.append({'hour': hour, 'count': 0})
        
        # Sort by hour
        time_data.sort(key=lambda x: x['hour'])
        
        x = [f"{item['hour']:02d}:00" for item in time_data]
        y = [item['count'] for item in time_data]
        
        plt.bar(x, y, color='skyblue')
        plt.xticks(rotation=90)
        plt.title('Distribusi Kendaraan Per Jam')
        
        # Show busiest hour
        if peak_data:
            busiest_hour = f"{peak_data['hour']:02d}:00 - {(peak_data['hour'] + 1) % 24:02d}:00"
            pdf.chapter_body(f"Jam sibuk: {busiest_hour} dengan {peak_data['count']:,} kendaraan.")
    
    elif report_type == 'weekly':
        x = [item['date'].strftime('%d/%m') for item in time_data]
        y = [item['count'] for item in time_data]
        
        plt.bar(x, y, color='skyblue')
        plt.title('Distribusi Kendaraan Harian')
        
        # Show busiest day
        if peak_data:
            busiest_day = peak_data['date'].strftime('%d %B %Y')
            pdf.chapter_body(f"Hari tersibuk: {busiest_day} dengan {peak_data['count']:,} kendaraan.")
    
    elif report_type == 'monthly':
        x = [f"{item['day']:02d}" for item in time_data]
        y = [item['count'] for item in time_data]
        
        plt.bar(x, y, color='skyblue')
        plt.title('Distribusi Kendaraan Per Hari dalam Bulan')
        
        # Show busiest day
        if peak_data:
            current_month = datetime.now().strftime('%B %Y')
            busiest_day = f"{peak_data['day']:02d} {current_month}"
            pdf.chapter_body(f"Hari tersibuk: {busiest_day} dengan {peak_data['count']:,} kendaraan.")
    
    plt.xlabel('Waktu')
    plt.ylabel('Jumlah Kendaraan')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Save chart to temporary file
    chart_path = f"temp_chart_{report_type}.png"
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()
    
    # Add chart to PDF
    pdf.add_chart(chart_path, "Grafik Distribusi Kendaraan")
    
    # 3. Vehicle Type Distribution
    pdf.chapter_title("3. DISTRIBUSI JENIS KENDARAAN")
    
    # Create pie chart for vehicle types
    if vehicle_counts:
        plt.figure(figsize=(6, 6))
        labels = [item['vehicle_type'].capitalize() for item in vehicle_counts]
        sizes = [item['count'] for item in vehicle_counts]
        
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, shadow=True)
        plt.axis('equal')
        plt.title('Distribusi Jenis Kendaraan')
        
        # Save pie chart
        pie_chart_path = f"temp_pie_{report_type}.png"
        plt.savefig(pie_chart_path, bbox_inches='tight')
        plt.close()
        
        # Add pie chart to PDF
        pdf.add_chart(pie_chart_path, "Grafik Distribusi Jenis Kendaraan")
    
    # 4. Detailed Data
    pdf.chapter_title("4. DATA DETAIL")
    
    if report_type == 'daily':
        # Get hourly breakdown with vehicle types
        detail_query = """
            SELECT HOUR(timestamp) as hour, 
                   vehicle_type,
                   COUNT(*) as count
            FROM vehicle_detections 
            WHERE DATE(timestamp) = CURDATE() 
            GROUP BY HOUR(timestamp), vehicle_type
            ORDER BY hour, vehicle_type
        """
        cursor.execute(detail_query)
        detail_data = cursor.fetchall()
        
        # Process data for table
        hours_dict = {}
        vehicle_types = set()
        
        for item in detail_data:
            hour = item['hour']
            v_type = item['vehicle_type']
            count = item['count']
            
            if hour not in hours_dict:
                hours_dict[hour] = {}
            
            hours_dict[hour][v_type] = count
            vehicle_types.add(v_type)
        
        # Sort vehicle types for consistent column order
        vehicle_types = sorted(list(vehicle_types))
        
        # Create table headers
        headers = ["Jam"] + [v_type.capitalize() for v_type in vehicle_types] + ["Total"]
        
        # Create table data
        data = []
        for hour in sorted(hours_dict.keys()):
            row = [f"{hour:02d}:00 - {(hour + 1) % 24:02d}:00"]
            
            hour_total = 0
            for v_type in vehicle_types:
                count = hours_dict[hour].get(v_type, 0)
                row.append(f"{count:,}")
                hour_total += count
            
            row.append(f"{hour_total:,}")
            data.append(row)
        
        # Add row for total
        total_row = ["TOTAL"]
        type_totals = {v_type: 0 for v_type in vehicle_types}
        
        for hour in hours_dict:
            for v_type in vehicle_types:
                type_totals[v_type] += hours_dict[hour].get(v_type, 0)
        
        for v_type in vehicle_types:
            total_row.append(f"{type_totals[v_type]:,}")
        
        total_row.append(f"{total_count:,}")
        data.append(total_row)
        
        pdf.add_table(headers, data)
    
    elif report_type == 'weekly':
        # Get daily breakdown with vehicle types
        detail_query = """
            SELECT DATE(timestamp) as date, 
                   vehicle_type,
                   COUNT(*) as count
            FROM vehicle_detections 
            WHERE timestamp >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
            GROUP BY DATE(timestamp), vehicle_type
            ORDER BY date, vehicle_type
        """
        cursor.execute(detail_query)
        detail_data = cursor.fetchall()
        
        # Process data for table
        dates_dict = {}
        vehicle_types = set()
        
        for item in detail_data:
            date = item['date']
            v_type = item['vehicle_type']
            count = item['count']
            
            if date not in dates_dict:
                dates_dict[date] = {}
            
            dates_dict[date][v_type] = count
            vehicle_types.add(v_type)
        
        # Sort vehicle types for consistent column order
        vehicle_types = sorted(list(vehicle_types))
        
        # Create table headers
        headers = ["Tanggal"] + [v_type.capitalize() for v_type in vehicle_types] + ["Total"]
        
        # Create table data
        data = []
        for date in sorted(dates_dict.keys()):
            row = [date.strftime('%d/%m/%Y')]
            
            date_total = 0
            for v_type in vehicle_types:
                count = dates_dict[date].get(v_type, 0)
                row.append(f"{count:,}")
                date_total += count
            
            row.append(f"{date_total:,}")
            data.append(row)
        
        # Add row for total
        total_row = ["TOTAL"]
        type_totals = {v_type: 0 for v_type in vehicle_types}
        
        for date in dates_dict:
            for v_type in vehicle_types:
                type_totals[v_type] += dates_dict[date].get(v_type, 0)
        
        for v_type in vehicle_types:
            total_row.append(f"{type_totals[v_type]:,}")
        
        total_row.append(f"{total_count:,}")
        data.append(total_row)
        
        pdf.add_table(headers, data)
    
    elif report_type == 'monthly':
        # Get daily breakdown with vehicle types
        detail_query = """
            SELECT DAY(timestamp) as day, 
                   vehicle_type,
                   COUNT(*) as count
            FROM vehicle_detections 
            WHERE YEAR(timestamp) = YEAR(CURDATE()) AND MONTH(timestamp) = MONTH(CURDATE())
            GROUP BY DAY(timestamp), vehicle_type
            ORDER BY day, vehicle_type
        """
        cursor.execute(detail_query)
        detail_data = cursor.fetchall()
        
        # Process data for table
        days_dict = {}
        vehicle_types = set()
        
        for item in detail_data:
            day = item['day']
            v_type = item['vehicle_type']
            count = item['count']
            
            if day not in days_dict:
                days_dict[day] = {}
            
            days_dict[day][v_type] = count
            vehicle_types.add(v_type)
        
        # Sort vehicle types for consistent column order
        vehicle_types = sorted(list(vehicle_types))
        
        # Create table headers
        headers = ["Tanggal"] + [v_type.capitalize() for v_type in vehicle_types] + ["Total"]
        
        # Create table data
        data = []
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        for day in sorted(days_dict.keys()):
            date_str = f"{day:02d}/{current_month:02d}/{current_year}"
            row = [date_str]
            
            day_total = 0
            for v_type in vehicle_types:
                count = days_dict[day].get(v_type, 0)
                row.append(f"{count:,}")
                day_total += count
            
            row.append(f"{day_total:,}")
            data.append(row)
        
        # Add row for total
        total_row = ["TOTAL"]
        type_totals = {v_type: 0 for v_type in vehicle_types}
        
        for day in days_dict:
            for v_type in vehicle_types:
                type_totals[v_type] += days_dict[day].get(v_type, 0)
        
        for v_type in vehicle_types:
            total_row.append(f"{type_totals[v_type]:,}")
        
        total_row.append(f"{total_count:,}")
        data.append(total_row)
        
        pdf.add_table(headers, data)
    
    # 5. Conclusion
    pdf.chapter_title("5. KESIMPULAN DAN REKOMENDASI")
    
    # Generate some basic conclusions
    conclusions = []
    
    # Find busiest vehicle type
    busiest_type = max(vehicle_counts, key=lambda x: x['count']) if vehicle_counts else None
    
    if busiest_type:
        busiest_percentage = (busiest_type['count'] / total_count) * 100 if total_count > 0 else 0
        conclusions.append(
            f"Jenis kendaraan yang paling banyak melintas adalah {busiest_type['vehicle_type'].capitalize()} "
            f"({busiest_type['count']:,} kendaraan atau {busiest_percentage:.2f}% dari total)."
        )
    
    if peak_data:
        if report_type == 'daily':
            busiest_hour = f"{peak_data['hour']:02d}:00 - {(peak_data['hour'] + 1) % 24:02d}:00"
            peak_percentage = (peak_data['count'] / total_count) * 100 if total_count > 0 else 0
            conclusions.append(
                f"Jam sibuk terjadi pada {busiest_hour} dengan jumlah {peak_data['count']:,} kendaraan "
                f"({peak_percentage:.2f}% dari total harian)."
            )
            
            # Generate recommendation based on peak hour
            if 7 <= peak_data['hour'] <= 9 or 16 <= peak_data['hour'] <= 18:
                conclusions.append(
                    "Jam sibuk berada pada jam berangkat/pulang kerja. Disarankan untuk menambah personil "
                    "pengaturan lalu lintas pada jam tersebut."
                )
            else:
                conclusions.append(
                    "Jam sibuk berada di luar jam berangkat/pulang kerja standar. Perlu dilakukan analisis "
                    "lebih lanjut untuk menentukan faktor penyebabnya."
                )
        
        elif report_type == 'weekly':
            busiest_day = peak_data['date'].strftime('%A, %d %B %Y')
            peak_percentage = (peak_data['count'] / total_count) * 100 if total_count > 0 else 0
            conclusions.append(
                f"Hari tersibuk terjadi pada {busiest_day} dengan jumlah {peak_data['count']:,} kendaraan "
                f"({peak_percentage:.2f}% dari total mingguan)."
            )
            
            # Day of week specific recommendation
            day_of_week = peak_data['date'].weekday()
            if day_of_week < 5:  # Weekday (0=Monday, 4=Friday)
                conclusions.append(
                    "Hari sibuk terjadi pada hari kerja. Disarankan untuk mengoptimalkan pengaturan lalu lintas "
                    "pada hari tersebut."
                )
            else:  # Weekend
                conclusions.append(
                    "Hari sibuk terjadi pada akhir pekan. Disarankan untuk meningkatkan pengaturan lalu lintas "
                    "untuk mengakomodasi kegiatan akhir pekan."
                )
        
        elif report_type == 'monthly':
            current_month = datetime.now().strftime('%B %Y')
            busiest_day = f"{peak_data['day']} {current_month}"
            peak_percentage = (peak_data['count'] / total_count) * 100 if total_count > 0 else 0
            conclusions.append(
                f"Hari tersibuk dalam bulan ini terjadi pada tanggal {busiest_day} dengan jumlah "
                f"{peak_data['count']:,} kendaraan ({peak_percentage:.2f}% dari total bulanan)."
            )
    
    # Join conclusions with line breaks
    conclusion_text = "\n\n".join(conclusions)
    pdf.chapter_body(conclusion_text)
    
    # 6. Signature
    pdf.ln(10)
    pdf.add_signature_box(
        "Kota", 
        "Nama Kepala Dinas", 
        "Kepala Dinas Perhubungan",
        "198001012010011001"
    )
    
    # Close database connection
    cursor.close()
    conn.close()
    
    # Get the PDF as bytes
    pdf_bytes = BytesIO(pdf.output(dest='S').encode('latin1'))
    
    # Clean up temporary files
    if os.path.exists(chart_path):
        os.remove(chart_path)
    if os.path.exists(pie_chart_path):
        os.remove(pie_chart_path)
    
    return pdf_bytes
