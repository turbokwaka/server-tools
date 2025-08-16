# scheduler.py
import time

import schedule
from report import prepare_output, send_output

def prepare_report():
    try:
        report = prepare_output()
    except Exception:
        report = "Броу всьо зламалось. Лошара."
    finally:
        send_output(report)

def main():
    schedule.every(1).minute.do(prepare_report)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()