from flask import Flask, Response
from prometheus_client import generate_latest, CollectorRegistry, Gauge
import os
import socket

app = Flask(__name__)

# Dosya sayısını ve boyutunu tutmak için iki Gauge metrik oluştur ve metrikler için bir CollectorRegistry tanımlama
registry = CollectorRegistry()

# Ekstra custom label'ları ekleyerek metrikler oluşturma
xml_file_count_metric = Gauge('xml_file_count', 'Number of .xml files in the specified directory', ['computer', 'ip'], registry=registry)
sxml_file_count_metric = Gauge('sxml_file_count', 'Number of .sxml files in the specified directory', ['computer', 'ip'], registry=registry)
total_file_size_metric = Gauge('total_file_size_gb', 'Total size of files in the specified directory (GB)', ['computer', 'ip'], registry=registry)

# Dosya sayısını ve boyutunu hesaplayan fonksiyon
def calculate_files_stats(directory_path):
    try:
        xml_file_count = len([name for name in os.listdir(directory_path) if name.endswith('.xml')])
        sxml_file_count = len([name for name in os.listdir(directory_path) if name.endswith('.sxml')])

        total_file_size_bytes = sum(os.path.getsize(os.path.join(directory_path, name)) for name in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, name)))

        total_file_size_gb = total_file_size_bytes / (1024 ** 3)  # bytes --> gigabytes

        return xml_file_count, sxml_file_count, total_file_size_gb
    except Exception as e:
        print("Error calculating files stats:", str(e))
        return None, None, None

@app.route('/metrics')
def metrics():
    # Bilgisayar adını ve IP adresini alma
    computer_name = socket.gethostname()
    ip_address = socket.gethostbyname(computer_name)

    # Dosya istatistiklerini alma
    xml_file_count, sxml_file_count, total_file_size_gb = calculate_files_stats(r'C:\Users\Emre\Desktop\plaka_gorselleri')
    
    # .xml dosya sayısını metrikte güncelle ve custom label değerlerini ayarlama
    if xml_file_count is not None:
        xml_file_count_metric.labels(computer=computer_name, ip=ip_address).set(xml_file_count)
    
    # .sxml dosya sayısını metrikte güncelle ve custom label değerlerini ayarlama
    if sxml_file_count is not None:
        sxml_file_count_metric.labels(computer=computer_name, ip=ip_address).set(sxml_file_count)

    # Toplam dosya boyutunu metrikte güncelle ve custom label değerlerini ayarlama
    if total_file_size_gb is not None:
        total_file_size_metric.labels(computer=computer_name, ip=ip_address).set(total_file_size_gb)

    # Metrikleri döndürme (registry'yi kullanarak)
    return Response(generate_latest(registry=registry), content_type='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
