import sqlite3

"""Ta część kody robi populację bazy danych związaną z danymi dotyczącymi linii kolejowych
   i przystanków. Wczytuje dane z pliku rozpiska_linii.txt, a następnie wypełnia bazę danych"""

DB_PATH = "../backend/database.db"

# Read the input file
with open("rozpiska_linii.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

# Extract unique city names
city_set = set()
lines_data = []  # To hold line number and stops for each line
for line in lines:
    # Split line into number and stops
    line_parts = line.split(";", 1)
    if len(line_parts) == 2:
        line_number = line_parts[0].strip()
        stops_part = line_parts[1]
        stops = [part.strip().title() for part in stops_part.split("-") if part.strip()]
        reversed_stops = stops[::-1]
        if stops:
            lines_data.append((line_number, stops))
            lines_data.append((line_number+"x", reversed_stops))
        for stop in stops:
            if stop and not stop[0].isdigit():
                city_set.add(stop)

# Sort the city names alphabetically
sorted_cities = sorted(city_set)

# Write the unique city names to linie.txt
with open("linie.txt", "w", encoding="utf-8") as file:
    file.write("\n".join(sorted_cities))

# Create a SQLite3 database
connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()


# Insert city names into the PRZYSTANKI table
cursor.executemany("INSERT OR IGNORE INTO STOPS (City) VALUES (?)", [(city,) for city in sorted_cities])


# Insert data into LINES and LINE_STOPS tables
for line_number, stops in lines_data:
    # Insert the line into LINES table
    cursor.execute("INSERT OR IGNORE INTO LINES (LineNumber) VALUES (?)", (line_number,))
    line_id = cursor.lastrowid

    # Insert each stop into LINE_STOPS with the correct order
    for order, stop in enumerate(stops, start=1):
        # Get the StopId for the stop name
        cursor.execute("SELECT ID FROM STOPS WHERE City = ?", (stop,))
        stop_id = cursor.fetchone()[0]

        # Insert into LINE_STOPS with StopId
        cursor.execute(
            "INSERT INTO LINE_STOPS (LineID, StopOrder, StopID) VALUES (?, ?, ?)",
            (line_id, order, stop_id)
        )

# Commit and close the database connection
connection.commit()
connection.close()

print("Process completed successfully!")
