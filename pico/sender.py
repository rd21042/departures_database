from pathlib import Path
from textwrap import wrap
import json
import serial
from time import sleep
from datetime import datetime

port = "COM3" # Can vary depending on device/OS
baudrate = 115200

def import_timetable(line):
    try:
        with open(Path(__file__).resolve().parent.parent / f"timetables/line{line}.json", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print("JSON error:", e)
        return {}

def get_stop():
    lines = [1, 2, 3, 4, 12]
    stop_lookup = {}

    # Collect all stops across all lines
    for line in lines:
        data = import_timetable(line)
        stop_offsets = data.get("stop_offsets", {})

        for name in stop_offsets.keys():
            stop_lookup[name.lower()] = name  # normalized → original

    # Ask user until valid input
    while True:
        stop = input("Choose a stop: ").strip().lower()

        if stop in stop_lookup:
            return stop_lookup[stop]
        else:
            print("Not a valid stop")

# Returns departures given a timetable, the stops offset and the current time
def get_departures(timetable, distance_from_endpoint, hour, minute):
    start_hour_shift = distance_from_endpoint // 60
    if distance_from_endpoint % 60 != 0:
        start_hour_shift += 1

    end_hour_shift = (distance_from_endpoint + 20) // 60
    deps = []

    for hour_offset in range(0 - start_hour_shift, 3 - end_hour_shift): # Current hour and next 2 hours
        h = (hour + hour_offset) % 24 # Ensures that h stays within 0 and 24
        departures = timetable.get(str(h), [])
        departures = [int(x) for x in departures]
        
        for dep_time in departures:
            tot_minutes = dep_time + distance_from_endpoint
            dep_minute = tot_minutes % 60
            hour_offset += tot_minutes // 60
            time_to_dep = (dep_minute - minute) + hour_offset * 60
            
            if 0 <= time_to_dep < 100: # Only consider departures within the next 99 minutes
                deps.append(time_to_dep)

    deps = sorted(deps)[:3] # Only show the next 3 departures

    if deps:
        return " ".join(str(d) for d in deps)
    else:
        return ""

def update_screen(stop):
    now = datetime.now()
    hour = now.hour
    minute = now.minute

    message = [f"{stop.capitalize()[:10]} {hour}:{minute:02}"]
    lines = [1, 2, 3, 4, 12]

    for line in lines:
        data = import_timetable(line)
        if not data:
            continue

        stop_names = data.get("stop_offsets", {})
        stop_offsets = stop_names.get(stop, [])

        if stop_offsets: # Check if current line reaches given stop
            distance_from_start = stop_offsets[0]
        else:
            continue

        destination = data.get('end', 'N/A')
        timetable = data.get("timetable_start", {})

        text = f"{line} {destination} " + get_departures(timetable, distance_from_start, hour, minute)
        deps = wrap(text, width=16)
        message.extend(deps[:2])

    # Ensure that we are sending exactly 8 lines, which fills the entirety of the OLED
    if message:
        message = (message + [""] * 8)[:8]
    else:
        message = (["No departures"] + [""] * 8)[:8]
    
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            sleep(2) # Wait for Pico reset
            for line in message:
                ser.write((line + "\n").encode("utf-8"))
                sleep(0.05) # 50 ms

    except Exception as e:
        print("Serial error:", e)

def main():
    # Setup
    stop = get_stop()
    update_screen(stop)

    # Loop
    try:
        while True:
            sleep(60 - datetime.now().second) # Wait until minute number increases
            update_screen(stop)

    except KeyboardInterrupt:
        print("Successfully stopped updating") # Smoother program termination

main()
