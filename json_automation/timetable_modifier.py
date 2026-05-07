from pathlib import Path

def timetabler(timetable):
    print(
        "Om du vill hoppa över ett klockslag tryck enter\n"
        "Skriv tidtabellen med mellanslag med avgångarna\n"
    )

    day_hours = 24

    for i in range(day_hours):
        hour = str(i)

        if hour in timetable:
            while True:
                overwrite = input(
                    f"Tidtabell för klockan {i} finns redan\n"
                    "Vill du skriva över den? j/n: "
                ).lower()

                if overwrite in ["j", "n"]:
                    break
                else:
                    print("Du skrev inte j (ja) eller n (nej)")
        
            if overwrite == "n":
                continue
        
        departures = input(f"Tidtabell klockan {i}: ").split()
        if departures:
            timetable[hour] = departures
    
    return timetable

def stoplist_parser():
    stops = {}
    file_path = Path(__file__).resolve().parent / "stoplist.txt"

    with open(file_path, encoding="utf-8") as file:
        for line_content in file:
            parsed_line = line_content.split()

            if len(parsed_line) < 3:
                raise ValueError("Hållplatslistan är skriven fel")

            try:
                time_to_start, time_to_end = map(int, parsed_line[:2])
            except ValueError as error:
                raise ValueError("Hållplatslistan är skriven fel") from error
            
            stops[" ".join(parsed_line[2:])] = [time_to_start, time_to_end]

    stop_list = list(stops.keys())    
    return stop_list[0], stop_list[-1], stops
