from pathlib import Path
from textwrap import wrap
import json
import serial
import time

port = "COM3"
baudrate = 115200

with open(Path(__file__).parent.parent / "timetables/line1.json", encoding="utf-8") as file:
    data = json.load(file)
    time_now = 18
    deps = data["timetable_start"]["14"]
    next_dep = int(deps[1]) - time_now
    then = int(deps[2]) - time_now
    then_then = int(deps[3]) - time_now
    message = f"1 {data['end']} {next_dep} {then} {then_then}"
    message = "\n".join(wrap(message, width=16))

ser = serial.Serial(port, baudrate, timeout=1)
time.sleep(2)
ser.write((message + "\n").encode())
print("Message sent:", message)
ser.close()
