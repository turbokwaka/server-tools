import psutil
from datetime import datetime
from zoneinfo import ZoneInfo
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
        with open("/host_proc/uptime", "r") as f:
            uptime_data = f.readline().split()
            uptime_seconds = float(uptime_data[0])
            mins = int(uptime_seconds // 60)
            hours = mins // 60
            days = hours // 24
            return f"{days}d {hours % 24}h {mins % 60}m"
    except Exception as e:
        return f"Uptime not available: {e}"

def get_k10temp_temp():
    try:
        output = subprocess.check_output(['sensors'], encoding='utf-8', errors='ignore')
        pattern = r'k10temp.*?\n(?:.+\n)*?temp1:\s+\+([\d.]+)°C'
        match = re.search(pattern, output, re.MULTILINE)
        if match:
            return f"{match.group(1)} °C"
        else:
            return "No k10temp data"
    except Exception as e:
        return f"Temperature not available: {e}"

def get_current_time_kiev():
    return datetime.now(ZoneInfo("Europe/Kiev")).strftime('%Y-%m-%d %H:%M:%S')

def prepare_output():
    output = []

    output.append("⛅ Time now")
    output.append(f"   {get_current_time_kiev()}")
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

    return "\n".join(output)

def send_output(output):
    params = {
        "chat_id": CHAT_ID,
        "text": output
    }
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data=params).raise_for_status()

def main():
    result = prepare_output()
    send_output(result)

if __name__ == "__main__":
    main()
