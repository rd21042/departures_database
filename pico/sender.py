from pathlib import Path
from textwrap import wrap
import json
import serial
from math import ceil
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

# Returns departures for a stop given:
# a timetable, the stops distance from endpoint and the current time
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

# Given a stop, returns the text to write to OLED
def generate_text_to_write(stop: str) -> list:
    now = datetime.now()
    hour = now.hour
    minute = now.minute

    deps_text = wrap(f"{stop.capitalize()} {hour}:{minute:02}", width=16)
    lines = [1, 20, 21, 3, 4, 12]

    for line in lines:
        data = import_timetable(line)
        if not data:
            continue

        stop_names = data.get("stop_offsets", {})
        stop_offsets = stop_names.get(stop, [])

        for i in ["start", "end"]:
            if stop_offsets:
                try:
                    if i == "start":
                        distance_from_dest = int(stop_offsets[0])
                    elif i == "end":
                        distance_from_dest = int(stop_offsets[1])
                except ValueError:
                    continue
            else:
                continue

            destination = data.get(i, "N/A")
            timetable = data.get(f"timetable_{i}", {})

            if stop != destination:
                deps = get_departures(timetable, distance_from_dest, hour, minute)
                
                if deps:
                    text = f"{line} {destination} " + deps
                    deps = wrap(text, width=16)
                    deps_text.extend(deps[:2])

    rows_per_page = 8
    items_per_page = 7 # For several pages where "Sida x av x" takes up one row

    if deps_text:
        msg_length = len(deps_text)
        result = []

        if msg_length <= rows_per_page:
            deps_text = (deps_text + [""] * (rows_per_page - msg_length))
        else:
            total_pages = ceil(msg_length / items_per_page)

        for page in range(total_pages):
            start = page * items_per_page
            end = start + items_per_page

            page_items = deps_text[start:end]          
            page_items += [""] * (items_per_page - len(page_items))
            page_items.append(f"Sida {page + 1} av {total_pages}")
            result.extend(page_items)

        deps_text = result
    else:
        deps_text = wrap(f"No departures for {stop} within the next 100 minutes", width=16)
        deps_text = (deps_text + [""] * (rows_per_page - len(deps_text)))
    
    return deps_text

def main():
    # Setup
    stop = get_stop()
    page_number = 0
    lines_per_page = 8
    update_overwrite = False
    last_sent_minute = None

    # Loop
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            sleep(1)

            while True:
                current_minute = datetime.now().minute

                if current_minute != last_sent_minute or update_overwrite:
                    update_overwrite = False
                    text_to_write = generate_text_to_write(stop)
                    pages = ceil(len(text_to_write) / lines_per_page)

                    start_index = page_number * lines_per_page
                    end_index = start_index + lines_per_page

                    #for line in text_to_write[start_index:end_index]:
                        #ser.write((line + "\n").encode("utf-8"))
                        #sleep(0.05)

                    last_sent_minute = current_minute

                x_value = ser.readline().decode("utf-8").strip()

                # x_value is a 16-bit int, and therefore lies between 0 and 65 536
                # The center is excatly on the middle of the x-axis which means x_value is 32 768 at center
                try:
                    x_value = int(x_value)
                    print(x_value)

                    if x_value > 40_000 and page_number < pages - 1:
                        page_number += 1
                        update_overwrite = True

                    elif x_value < 25_000 and page_number > 1:
                        page_number -= 1
                        update_overwrite = True
                        
                except ValueError:
                    pass

                sleep(1)

    except KeyboardInterrupt:
        print("Successfully stopped updating")

    except Exception as e:
        print("Serial error: ", e)

main()
