from json_serializer import import_line_data, export_line_data
from timetable_modifier import timetabler, stoplist_parser

def yes_no_query(prompt):
    while True:
        answer = input(prompt + " j/n: ").lower()
        if answer not in ["j", "n"]:
            print("Du skrev inte j (ja) eller n (nej)\n")
        else:
            return answer

def end_selector(start, end):
    while True:
        choice = input(
            "Vill du ändra starthållplatsens eller sluthållplatsens tidtabell?\n"
            f"Start: {start}\n"
            f"Slut: {end}\n"
            "Vänligen skriv start eller slut här: "
        ).lower()

        if choice == "start":
            return "start"
        elif choice == "slut":
            return "end"
        else:
            print("Du skrev inte start eller slut. Vänligen försök igen\n")

def main():
    if yes_no_query("Har du klistrat in rätt hållplatslista i stoplist.txt?") == "n":
        return
    print()

    while True:
        valid_lines = ["1", "20", "21", "3", "4", "12", "13"]
        line_answer = input(
            "Vilken linje vill du ändra/lägga till?\n"
            f"Välj mellan {', '.join(valid_lines)}: "
        )

        if line_answer in valid_lines:
            line = int(line_answer)
            break
        else:
            print("Ogilitigt svar. Försök igen\n")

    print()

    data = import_line_data(line)
    start, end, stops = stoplist_parser()

    if yes_no_query("Vill du ändra tidtabellen?") == "j":
        print()

        end_choice = end_selector(start, end)
        print()
        data[f"timetable_{end_choice}"] = timetabler(data[f"timetable_{end_choice}"])

        print()
        if yes_no_query("Vill du ändra tidtabellen för den andra änden?") == "j":
            other_end = "end" if end_choice == "start" else "start"
            data[f"timetable_{other_end}"] = timetabler(data[f"timetable_{other_end}"])

    data["start"] = start
    data["end"] = end
    data["stop_offsets"] = stops
    export_line_data(data, line)

main()
