# helper/pdf_utils.py
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os # Untuk path logo

# Atur backend matplotlib agar tidak memerlukan GUI
import matplotlib
matplotlib.use('Agg')

# Fungsi bantuan untuk membuat paragraf dengan gaya tertentu
def create_paragraph(text, style_name, alignment=TA_LEFT, fontSize=10, leading=12, spaceAfter=6, spaceBefore=0, textColor=colors.black, bold=False):
    styles = getSampleStyleSheet()
    # Buat style dasar jika tidak ada
    if style_name not in styles:
        styles.add(ParagraphStyle(name=style_name, parent=styles['Normal']))

    # Jika bold=True, coba gunakan atau buat style bold
    actual_style_name = style_name
    if bold:
        bold_style_name = style_name + 'Bold'
        if bold_style_name not in styles:
            # Ambil fontName dari style dasar, tambahkan -Bold
            base_font_name = styles[style_name].fontName
            # Heuristik umum untuk nama font bold
            if 'Bold' not in base_font_name:
                 bold_font_name = base_font_name + '-Bold'
            else:
                 bold_font_name = base_font_name # Sudah bold
            
            # Cek jika font bold valid, jika tidak fallback ke base + weight (meskipun reportlab tidak langsung support weight di ParagraphStyle)
            # Untuk kesederhanaan, kita asumsikan fontName-Bold ada atau reportlab menanganinya.
            # Dalam kasus nyata, Anda mungkin perlu mendaftarkan font bold secara eksplisit.
            try:
                styles.add(ParagraphStyle(name=bold_style_name, parent=styles[style_name], fontName=bold_font_name))
            except: # Fallback jika nama font bold tidak dikenali
                 styles.add(ParagraphStyle(name=bold_style_name, parent=styles[style_name])) # Mungkin tidak jadi bold
        actual_style_name = bold_style_name


    style = ParagraphStyle(
        name='CustomStyle_' + actual_style_name, # Nama unik untuk menghindari konflik
        parent=styles[actual_style_name],
        alignment=alignment,
        fontSize=fontSize,
        leading=leading,
        spaceAfter=spaceAfter,
        spaceBefore=spaceBefore,
        textColor=textColor
    )
    return Paragraph(text, style)

# Fungsi bantuan untuk menghasilkan gambar grafik batang menggunakan matplotlib
def generate_bar_chart_image(x_labels, y_values, x_title, y_title, chart_title):
    if not x_labels or not y_values or all(v == 0 for v in y_values):
        # Buat gambar placeholder jika tidak ada data
        fig, ax = plt.subplots(figsize=(7, 3.5)) # Ukuran disesuaikan agar tidak terlalu besar
        ax.text(0.5, 0.5, "Data tidak tersedia untuk grafik", ha='center', va='center', fontsize=10, color='grey')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(chart_title, fontsize=12)
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='PNG', dpi=100)
        img_buffer.seek(0)
        plt.close(fig)
        return img_buffer

    img_buffer = BytesIO()
    # Sesuaikan ukuran gambar agar pas di PDF
    fig, ax = plt.subplots(figsize=(7, 3.5)) # lebar 7 inci, tinggi 3.5 inci
    
    bars = ax.bar(x_labels, y_values, color='skyblue', width=0.6) # Sesuaikan lebar bar
    ax.set_xlabel(x_title, fontsize=10)
    ax.set_ylabel(y_title, fontsize=10)
    ax.set_title(chart_title, fontsize=12, pad=15) # Tambah padding untuk judul
    
    # Atur tick labels
    ax.tick_params(axis='x', labelsize=8, rotation=30) # Rotate dan align
    ax.tick_params(axis='y', labelsize=8)

    # Tambahkan nilai di atas bar jika memungkinkan
    for bar in bars:
        yval = bar.get_height()
        if yval > 0: # Hanya tampilkan jika nilai > 0
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05 * max(y_values, default=1), # Penyesuaian posisi teks
                    f'{int(yval)}', ha='center', va='bottom', fontsize=7, color='dimgray')

    plt.grid(axis='y', linestyle='--', alpha=0.7) # Tambah grid y-axis
    plt.tight_layout(pad=1.5) # Penyesuaian layout agar tidak terpotong
    plt.savefig(img_buffer, format='PNG', dpi=100) # DPI bisa disesuaikan
    img_buffer.seek(0)
    plt.close(fig)
    return img_buffer

# Fungsi bantuan untuk menghasilkan gambar grafik lingkaran menggunakan matplotlib
def generate_pie_chart_image(labels, sizes, chart_title):
    # Filter out zero sizes and corresponding labels to avoid errors and clutter
    filtered_labels_sizes = [(label, size) for label, size in zip(labels, sizes) if size > 0]
    
    if not filtered_labels_sizes:
        fig, ax = plt.subplots(figsize=(4, 3)) # Ukuran disesuaikan
        ax.text(0.5, 0.5, "Data tidak tersedia", ha='center', va='center', fontsize=9, color='grey')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(chart_title, fontsize=10)
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='PNG', dpi=100)
        img_buffer.seek(0)
        plt.close(fig)
        return img_buffer

    # Unpack filtered labels and sizes
    final_labels, final_sizes = zip(*filtered_labels_sizes)

    img_buffer = BytesIO()
    # Sesuaikan ukuran gambar agar pas di PDF
    fig, ax = plt.subplots(figsize=(4, 3)) # lebar 4 inci, tinggi 3 inci
    
    pie_colors = ['#66b3ff','#99ff99','#ffcc99','#ff9999', '#c2c2f0','#ffb3e6', '#c4e17f']
    
    wedges, texts, autotexts = ax.pie(final_sizes, labels=None, autopct='%1.1f%%', 
                                      startangle=90, colors=pie_colors[:len(final_labels)],
                                      pctdistance=0.80) # Atur jarak persentase dari tengah

    ax.set_title(chart_title, fontsize=10, pad=10) # Tambah padding untuk judul
    
    # Atur properti teks persentase
    for autotext in autotexts:
        autotext.set_fontsize(7)
        autotext.set_color('black')

    if len(final_labels) > 0 :
         ax.legend(wedges, [f"{l} ({s:.1f}%)" for l, s in zip(final_labels, [(sz/sum(final_sizes))*100 for sz in final_sizes])],
                  title="Jenis Kendaraan",
                  loc="center left",
                  bbox_to_anchor=(0.95, 0, 0.5, 1), # Posisi legenda
                  fontsize=7)


    plt.tight_layout(rect=[0, 0, 0.8, 1]) # Sesuaikan layout agar legenda tidak terpotong
    plt.savefig(img_buffer, format='PNG', dpi=100)
    img_buffer.seek(0)
    plt.close(fig)
    return img_buffer

# Fungsi utama untuk menghasilkan PDF
def generate_report_pdf(report_type_display, summary_data, time_series_data, report_period_str, busiest_period_info, logo_path=None):
    buffer = BytesIO()
    # Ukuran kertas A4: 8.27 x 11.69 inci. Kita gunakan letter untuk contoh ini.
    doc = SimpleDocTemplate(buffer, pagesize=(8.27 * inch, 11.69 * inch), # A4
                            leftMargin=0.75*inch, rightMargin=0.75*inch,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    
    current_dir = os.path.dirname(__file__)
    dishub = Image(os.path.join(current_dir, '..', 'dishub.png'), width=1*inch, height=1*inch)
    pemkot = Image(os.path.join(current_dir, '..', 'pemkot.png'), width=1*inch, height=1*inch)

    center_style = ParagraphStyle(
        name='AddressStyle',
        parent=getSampleStyleSheet()['Normal'],
        alignment=TA_CENTER,
        leading=16,
        spaceAfter=0,
        spaceBefore=0
    )
    # === BAGIAN HEADER ===
    address_text_paragraph = Paragraph(
        "<para align='center'><b><font size=16>PEMERINTAH KOTA MADIUN</font></b><br/>" +
        "<b><font size=16>DINAS PERHUBUNGAN</font></b><br/>" +
        "<font size=10>Jl. Hayam Wuruk No. 15, Telp: 081212341234</font></para>",
        center_style
    )

    if dishub or pemkot:
        cell1_content = dishub if dishub else Spacer(0.8*inch, 0.8*inch)
        
        # Kolom 3: Logo Pemkot (atau spacer jika tidak ada)
        cell3_content = pemkot if pemkot else Spacer(0.8*inch, 0.8*inch)
        logo_column_width = 1.0 * inch
        text_column_width = (6.77 * inch) - (2 * logo_column_width) # 4.77 inci untuk teks

        header_table_data = [[cell1_content, address_text_paragraph, cell3_content]]
        
        header_table = Table(header_table_data, colWidths=[logo_column_width, text_column_width, logo_column_width])
        
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('ALIGN', (1,0), (1,0), 'CENTER'),
            ('ALIGN', (2,0), (2,0), 'RIGHT'),
        ]))
        story.append(header_table)
        line = Table(
            [['']],
            colWidths=[doc.width]
        )
        line.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 1, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(line)
    
    story.append(Spacer(0, 0.3*inch))
    story.append(create_paragraph(f"LAPORAN {report_type_display.upper()} LHR", 'h1', alignment=TA_CENTER, bold=True, fontSize=12, spaceAfter=10))
    story.append(create_paragraph(report_period_str, 'Normal', alignment=TA_CENTER, fontSize=10, spaceAfter=20))

    # === BAGIAN 1: RINGKASAN STATISTIK ===
    story.append(create_paragraph("<b>1. RINGKASAN STATISTIK</b>", 'h3', fontSize=12, spaceAfter=10, bold=True))
    
    total_kendaraan_summary = sum(item['count'] for item in summary_data)
    story.append(create_paragraph(f"Total kendaraan melintas {report_period_str.lower().replace('periode ','')} adalah <b>{total_kendaraan_summary:,}</b> kendaraan.", 'Normal', fontSize=10, spaceAfter=10))

    summary_table_data = [
        [Paragraph("<b>Jenis Kendaraan</b>", getSampleStyleSheet()['Normal']), 
         Paragraph("<b>Jumlah</b>", getSampleStyleSheet()['Normal']), 
         Paragraph("<b>Persentase</b>", getSampleStyleSheet()['Normal'])]
    ]
    for item in summary_data:
        percentage = (item['count'] / total_kendaraan_summary * 100) if total_kendaraan_summary > 0 else 0
        summary_table_data.append([
            item['vehicle_type'], 
            f"{item['count']:,}", 
            f"{percentage:.2f} %"
        ])
    summary_table_data.append([
        Paragraph("<b>Total</b>", getSampleStyleSheet()['Normal']), 
        Paragraph(f"<b>{total_kendaraan_summary:,}</b>", getSampleStyleSheet()['Normal']), 
        Paragraph("<b>100.00 %</b>", getSampleStyleSheet()['Normal'])
    ])

    summary_table = Table(summary_table_data, colWidths=[3*inch, 2*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (1,1), (1,-1), 'RIGHT'), # Jumlah rata kanan
        ('ALIGN', (2,1), (2,-1), 'RIGHT'), # Persentase rata kanan
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('BACKGROUND', (0,1), (-1,-2), colors.whitesmoke), # Warna baris data
        ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey), # Warna baris total
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.2*inch))

    # === BAGIAN 2: DISTRIBUSI KENDARAAN ===
    story.append(create_paragraph("<b>2. DISTRIBUSI KENDARAAN</b>", 'h3', fontSize=12, spaceAfter=10, bold=True))
    story.append(create_paragraph(busiest_period_info, 'Normal', fontSize=10, spaceAfter=10))

    if report_type_display.lower() == "harian":
        bar_chart_labels = [item['Waktu_Label'] for item in time_series_data]
        bar_chart_values = [item['Total'] for item in time_series_data]
        bar_x_label = "Jam"
        bar_title = "Distribusi Kendaraan Per Jam"
    elif report_type_display.lower() == "mingguan":
        bar_chart_labels = [item['Tanggal'] for item in time_series_data]
        bar_chart_values = [item['Total'] for item in time_series_data]
        bar_x_label = "Tanggal"
        bar_title = "Distribusi Kendaraan Harian (Mingguan)"
    elif report_type_display.lower() == "bulanan":
        bar_chart_labels = [item['Tanggal_Simple'] for item in time_series_data]
        bar_chart_values = [item['Total'] for item in time_series_data]
        bar_x_label = "Tanggal dalam Bulan"
        bar_title = "Distribusi Kendaraan Harian (Bulanan)"
    else: # Fallback
        bar_chart_labels = [str(i+1) for i in range(len(time_series_data))]
        bar_chart_values = [item.get('Total',0) for item in time_series_data]
        bar_x_label = "Periode"
        bar_title = "Distribusi Kendaraan"

    bar_chart_img_buffer = generate_bar_chart_image(bar_chart_labels, bar_chart_values, bar_x_label, "Jumlah Kendaraan", bar_title)
    if bar_chart_img_buffer:
        bar_chart_image = Image(bar_chart_img_buffer, width=6*inch, height=4*inch)
        bar_chart_image.hAlign = 'CENTER'
        story.append(create_paragraph("<b>GRAFIK DISTRIBUSI</b>", 'Normal', fontSize=10, bold=True, spaceBefore=10, spaceAfter=5))
        story.append(bar_chart_image)
        story.append(Spacer(1,0.1*inch))

    # Data untuk Grafik Persentase (Pie Chart)
    pie_chart_labels = [item['vehicle_type'] for item in summary_data]
    pie_chart_sizes = [item['count'] for item in summary_data]
    pie_chart_img_buffer = generate_pie_chart_image(pie_chart_labels, pie_chart_sizes, "")
    if pie_chart_img_buffer:
        pie_chart_image = Image(pie_chart_img_buffer, width=6*inch, height=5*inch)
        pie_chart_image.hAlign = 'CENTER'
        story.append(create_paragraph("<b>GRAFIK PERSENTASE</b>", 'Normal', fontSize=10, bold=True, spaceBefore=10, spaceAfter=5))
        story.append(pie_chart_image)
        story.append(Spacer(1, -0.5*inch))


    # === BAGIAN 3: DATA DETAIL ===
    story.append(create_paragraph("<b>3. DATA DETAIL</b>", 'h3', fontSize=12, spaceAfter=10, bold=True))
    
    detail_table_header_text = "Waktu" # Default
    if report_type_display.lower() == "harian": detail_table_header_text = "Jam"
    elif report_type_display.lower() == "mingguan": detail_table_header_text = "Tanggal"
    elif report_type_display.lower() == "bulanan": detail_table_header_text = "Tanggal"


    vehicle_columns = ["Motorcycle", "Car", "Bus", "Truck"]
    
    detail_table_data = [
        [Paragraph(f"<b>{detail_table_header_text}</b>", getSampleStyleSheet()['Normal'])] +
        [Paragraph(f"<b>{col}</b>", getSampleStyleSheet()['Normal']) for col in vehicle_columns] +
        [Paragraph("<b>Total</b>", getSampleStyleSheet()['Normal'])]
    ]

    for item in time_series_data:
        row_data = []
        if report_type_display.lower() == "harian":
            row_data.append(item.get('Waktu_Label', 'N/A')) # Misal "00:00"
        else:
            row_data.append(item.get('Tanggal', 'N/A')) # Misal "17 Apr 2025" atau "01/MM/YYYY"
        
        for v_col in vehicle_columns:
            row_data.append(f"{item.get(v_col, 0):,}")
        
        row_data.append(f"{item.get('Total', 0):,}")
        detail_table_data.append(row_data)

    col_widths_detail = [1.7*inch] + [1.0*inch] * len(vehicle_columns) + [1.0*inch] 
    
    detail_table = Table(detail_table_data, colWidths=col_widths_detail)
    detail_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'), # Default rata kiri
        ('ALIGN', (1,1), (-1,-1), 'RIGHT'), # Data angka rata kanan
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10), # Font lebih kecil untuk tabel detail
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(detail_table)

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
