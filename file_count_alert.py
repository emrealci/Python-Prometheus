import requests
import time
import os

threshold = 50

xml_warning = {}
sxml_warning = {}

def get_metric_value(url, metric_name):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            metrics = response.text.splitlines()
            for metric in metrics:
                if metric.startswith(metric_name):
                    metric_value = float(metric.split(" ")[1])
                    return metric_value
    except:
        return None

def read_metrics_config_file(file_path):
    devices_ip = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                url, metric = line.split(' ')
                devices_ip[url] = metric
    return devices_ip

def check_threshold(device, ip, xml_metric_value, sxml_metric_value):
    if xml_metric_value is not None and xml_metric_value >= threshold:
        xml_warning[device] = ip

    if sxml_metric_value is not None and sxml_metric_value >= threshold:
        sxml_warning[device] = ip

def format_dict_items(data):
    formatted_items = []
    for key, value in data.items():
        url_without_http = value.split("://", 1)[-1]
        url_without_port_metrics = url_without_http.split(":")[0]
        formatted_items.append(f"{key} : {url_without_port_metrics}")
    return ", ".join(formatted_items)

def show_popup_notification(alert_title, alert_text, display_time=10):
    os.system(f"notify-send '{alert_title}' '{alert_text}' & sleep {display_time} && pkill notify-osd")

def display_alerts():
    xml_text = format_dict_items(xml_warning)
    sxml_text = format_dict_items(sxml_warning)
    alert_text = f"Dosya Aşımı XML = {xml_text}\nDosya Aşımı SXML = {sxml_text}"

    os.system("paplay /usr/share/sounds/freedesktop/stereo/phone-outgoing-busy.oga")

    alert_title = "Uyarı"
    show_popup_notification(alert_title, alert_text, display_time=10)

    time.sleep(10)

def main():
    config_file_path = "/home/emre/Desktop/metrics_config.txt"
    devices = read_metrics_config_file(config_file_path)

    print("Eklenti metriklerin durumunu kontrol ediyor...")

    while True:
        xml_warning.clear()
        sxml_warning.clear()
        for url in devices:
            device = devices[url]
            ip = url
            xml_file_count = get_metric_value(url, "xml_file_count")
            sxml_file_count = get_metric_value(url, "sxml_file_count")
            check_threshold(device, ip, xml_file_count, sxml_file_count)

        display_alerts()


if __name__ == "__main__":
    main()
