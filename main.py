import psutil
from datetime import datetime
import subprocess
import re
import os
import requests

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def get_memory_info():
    mem = psutil.virtual_memory()
    return {
        "Total": f"{mem.total / (1024 ** 3):.2f} GB",
        "Available": f"{mem.available / (1024 ** 3):.2f} GB",
        "Used": f"{mem.used / (1024 ** 3):.2f} GB",
        "Percent": f"{mem.percent} %"
    }

def get_disk_info():
    disk = psutil.disk_usage('/')
    return {
        "Total": f"{disk.total / (1024 ** 3):.2f} GB",
        "Used": f"{disk.used / (1024 ** 3):.2f} GB",
        "Free": f"{disk.free / (1024 ** 3):.2f} GB",
        "Percent": f"{disk.percent} %"
    }

def get_cpu_info():
    return {
        "CPU Usage": f"{psutil.cpu_percent(interval=1)} %"
    }

def get_uptime():
    try:
        uptime_pretty = subprocess.check_output(['uptime', '-p'], encoding='utf-8').strip()
        return uptime_pretty
    except Exception as e:
        return f"Uptime not available: {e}"


def get_k10temp_temp():
    try:
        output = subprocess.check_output(['sensors'], encoding='utf-8')
        pattern = r'k10temp-pci-00c3\n(?:.+\n)*?temp1:\s+\+([\d.]+)°C'
        match = re.search(pattern, output)
        if match:
            return f"{match.group(1)} °C"
    except Exception as e:
        return f"Temperature not available: {e}"

def prepare_output():
    output = []

    output.append("⛅ Time now")
    output.append(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("")

    output.append("🌸 Memory Info")
    for k, v in get_memory_info().items():
        output.append(f"   {k:10}: {v}")
    output.append("")

    output.append("🌷 Disk Info")
    for k, v in get_disk_info().items():
        output.append(f"   {k:10}: {v}")
    output.append("")

    output.append("☘️ CPU Usage")
    for k, v in get_cpu_info().items():
        output.append(f"   {k:10}: {v}")
    output.append("")

    output.append(f"⚙️ Uptime\n   Duration  : {get_uptime()}")
    output.append("")

    output.append(f"🪸 Temperature\n   K10temp   : {get_k10temp_temp()}")

    full_output = "\n".join(output)

    return full_output

def send_output(output):
    params = {
        "chat_id": CHAT_ID,
        "text": output
    }
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data=params).raise_for_status()

def main():
    send_output(prepare_output())

if __name__ == "__main__":
    main()

