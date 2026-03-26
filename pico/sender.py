from pathlib import Path
from textwrap import wrap
import json
import serial
from time import sleep
from datetime import datetime

port = "COM3"
baudrate = 115200

# Get time
now = datetime.now()
hour = now.hour
minute = now.minute

def get_stop():
    valid_endpoints = ["tuve torg", "skogome", "selma lagerlofs torg"]
    
    while True:
        endpoint = input("Choose an endpoint: ").lower()
        if endpoint in valid_endpoints:
            return endpoint
        else:
            print("Not a valid endpoint")

def get_departures(timetable):
    next_deps = ""
    deps = []

    for hour_offset in range(3): # Current hour and next 2 hours
        h = (hour + hour_offset) % 24
        departures = timetable.get(str(h))

        if not departures:
            continue  # No departures for this hour
        
        departures = [int(x) for x in departures]
        
        for dep_time in departures:
            time_to_dep = (dep_time - minute) + hour_offset * 60
            
            if 0 <= time_to_dep < 100:
                deps.append(time_to_dep)

    deps = sorted(deps)[:2]

    if not deps:
        return ""
    
    return " ".join(str(d) for d in deps)

def send_serial(message):
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            sleep(2)  # Wait for Pico reset
            ser.write((message + "\n").encode())
    except Exception as e:
        print("Serial error:", e)
        return

def main():
    endpoint = get_stop()
    send_serial(f"{endpoint.capitalize()[:10]} {hour}:{minute}\n")
    lines = [1, 2, 3, 4, 12]

    for line in lines:
        try:
            with open(Path(__file__).parent.parent / f"timetables/line{line}.json", encoding="utf-8") as file:
                data = json.load(file)
        except Exception as e:
            print("JSON error:", e)
            return
        
        if endpoint in data.get("start", "").lower():
            timetable = data.get("timetable_start", {})
            message = wrap(f"{line} {data.get('end', 'N/A')} " + get_departures(timetable), width=16)
            send_serial("\n".join(message[:2]))

        elif endpoint in data.get("end", "").lower():
            timetable = data.get("timetable_end", {})
            message = wrap(f"{line} {data.get('start', 'N/A')} " + get_departures(timetable), width=16)
            send_serial("\n".join(message[:2]))

main()
