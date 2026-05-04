from pathlib import Path
from textwrap import wrap
import json
import serial
from time import sleep
from datetime import datetime

port = "COM3" # Can vary depending on device/OS
baudrate = 115200

# Retrieves the given line's timetable
def import_timetable(line: int) -> dict:
    try:
        path = Path(__file__).resolve().parent.parent / f"timetables/line{line}.json"
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print("JSON error:", e)
        return {}

# Asks user to name a stop and returns it
def get_stop() -> str:
    lines = [1, 20, 21, 3, 4, 12]
    stop_lookup = {}

    # Collect all stops across all lines
    for line in lines:
        data = import_timetable(line)
        stop_offsets = data.get("stop_offsets", {})

        for name in stop_offsets.keys():
            stop_lookup[name.lower()] = name # normalized → original

    # Ask user until valid input
    while True:
        stop = input("Choose a stop: ").strip().lower()

        if stop in stop_lookup:
            return stop_lookup[stop]
        else:
            print("Not a valid stop")

# Returns departures given a timetable, the stops distance from endpoint and the current time
def get_departures(
        timetable: dict,
        distance_from_endpoint: int, 
        hour: int,
        minute: int
    ) -> str:

    start_hour_shift = distance_from_endpoint // 60
    if distance_from_endpoint % 60 != 0:
        start_hour_shift += 1

    end_hour_shift = (distance_from_endpoint + 20) // 60
    deps = []

    # Check for departures within the current hour and next 2 hours
    for hour_offset in range(0 - start_hour_shift, 3 - end_hour_shift):
        h = (hour + hour_offset) % 24
        departures = timetable.get(str(h), [])
        departures = [int(x) for x in departures]
        
        for dep_time in departures:
            tot_minutes = dep_time + distance_from_endpoint
            dep_minute = tot_minutes % 60
            correct_hour_offset = hour_offset + (tot_minutes // 60)
            time_to_dep = (dep_minute - minute) + correct_hour_offset * 60
            
            if 0 <= time_to_dep < 100:
                deps.append(time_to_dep)

    deps = sorted(deps)[:3]

    if deps:
        return " ".join(str(d) for d in deps)
    else:
        return ""

# Given a stop, sends up-to-date departures to Pico to refresh OLED screen
def update_screen(stop: str):
    now = datetime.now()
    hour = now.hour
    minute = now.minute

    message = wrap(f"{stop.capitalize()} {hour}:{minute:02}", width=16)
    lines = [1, 20, 21, 3, 4, 12]

    # Check for departures across all lines
    for line in lines:
        data = import_timetable(line)
        if not data:
            continue

        stop_names = data.get("stop_offsets", {})
        stop_offsets = stop_names.get(stop, [])

        if stop_offsets:
            try:
                distance_from_start = int(stop_offsets[0])
            except ValueError:
                continue
        else:
            continue

        destination = data.get('end', 'N/A')
        timetable = data.get("timetable_start", {})

        if stop != destination:
            deps = get_departures(timetable, distance_from_start, hour, minute)
            
            if deps:
                text = f"{line} {destination} " + deps
                deps = wrap(text, width=16)
                message.extend(deps[:2])
            else:
                message = ["No departures"]

    msg_length = len(message)

    if msg_length <= 8:
        message = (message + [""] * 8)[:8]
    else:
        for i, index in enumerate(range(8, msg_length, 8)):
            message.insert(index - 1, f"Sida {i + 1} av {(msg_length // 8) + 1}")
    
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            sleep(1)

            for line in message[:8]:
                ser.write((line + "\n").encode("utf-8"))
                sleep(0.05)
        
            data = ser.readline().decode("utf-8").strip()
        
        print(data)

    except Exception as e:
        print("Serial error: ", e)

def main():
    # Setup
    stop = get_stop()
    update_screen(stop)

    # Loop
    try:
        while True:
            sleep(60 - datetime.now().second)
            update_screen(stop)

    except KeyboardInterrupt:
        print("Successfully stopped updating")

main()
