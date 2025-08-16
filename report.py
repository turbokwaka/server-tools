# report.py
import psutil
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess
import re
import os
import requests
import socket

from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

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
            uptime_seconds = float(f.readline().split()[0])
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

def get_current_time_kyiv():
    # Сучасна назва зони — Europe/Kyiv; залишаємо фолбек на стару
    for tz in ("Europe/Kyiv", "Europe/Kiev"):
        try:
            return datetime.now(ZoneInfo(tz)).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            continue
    # Останній фолбек — UTC
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')

def get_ip_info():
    try:
        # зовнішня IP
        external_ip = requests.get("https://api.ipify.org", timeout=5).text
    except Exception as e:
        external_ip = f"Error: {e}"

    return {
        "External IP": external_ip
    }

def prepare_output():
    output = []

    output.append("⛅ Time now")
    output.append(f"   {get_current_time_kyiv()}")
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
    output.append("")

    output.append("🌐 Network Info")
    for k, v in get_ip_info().items():
        output.append(f"   {k:10}: {v}")

    return "\n".join(output)

def send_output(output):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        # Якщо немає токена/чат-айді — просто виводимо в лог, щоб не мовчати
        print("TELEGRAM_TOKEN or CHAT_ID is not set")
        print(output)
        return
    params = {
        "chat_id": CHAT_ID,
        "text": output
    }
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data=params,
        timeout=10
    ).raise_for_status()

def main():
    result = prepare_output()
    send_output(result)

if __name__ == "__main__":
    main()
