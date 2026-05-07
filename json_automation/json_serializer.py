from pathlib import Path
import json

def import_line_data(line):
    structure = {
        "start": "",
        "end": "",
        "timetable_start": {},
        "timetable_end": {},    
        "stop_offsets": {}
    }

    file_path = Path(__file__).resolve().parent.parent / "timetables" / f"line{line}.json"

    if not file_path.exists():
        return structure
    
    with open(file_path, encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return structure
        
        data.setdefault("timetable_start", {})
        data.setdefault("timetable_end", {})
        data.setdefault("stop_offsets", {})
        return data
    
def export_line_data(data, line):
    file_path = Path(__file__).resolve().parent.parent / "timetables" / f"line{line}.json"
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        