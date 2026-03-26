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

line_number = 4

try:
    with open(Path(__file__).parent.parent / f"timetables/line{line_number}.json", encoding="utf-8") as file:
        data = json.load(file)
except Exception as e:
    print("JSON error:", e)
    exit()

endpoint = "start"
destination = data.get(endpoint, "N/A")
message = f"{line_number} {destination}"
deps = []

for hour_offset, h in enumerate([hour, (hour + 1) % 24]): # Current hour and next hour
    departures = data.get(f"timetable_{endpoint}", {}).get(str(h))

    if not departures:
        continue  # No departures for this hour
    
    departures = [int(x) for x in departures]
    
    for dep_time in departures:
        time_to_dep = (dep_time - minute) + hour_offset * 60
        
        if time_to_dep >= 0:
            deps.append(time_to_dep)

deps = sorted(deps)[:2]
if deps:
    for time_to_dep in deps:
        message += f" {time_to_dep}"
else:
    message = "No departures"

message = "\n".join(wrap(message, width=16))

try:
    with serial.Serial(port, baudrate, timeout=1) as ser:
        sleep(2)  # wait for Pico reset
        ser.write((message + "\n").encode())
except Exception as e:
    print("Serial error:", e)
