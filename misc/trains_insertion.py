import sqlite3
import random
import string

global wagon_id
wagon_id = 1

def generate_train_name(line_number):
    base_name = "IC"
    seed = ''.join([c for c in line_number if c != 'x'])
    random.seed(seed)
    name = base_name + ''.join(random.choices(string.ascii_uppercase, k=5)) + ('x' if 'x' in line_number else '')
    return name

def create_seats(cursor, wagon_id, is_compartmental, wagon_class, size):
    if is_compartmental:
        compartment_size = {1: 4, 2: 6, 3: 8}[wagon_class]
        num_compartments = 12 if size == "large" else 10
        for compartment in range(1, num_compartments + 1):
            seat_number = 1
            for _ in range(compartment_size):
                seat_id = (10 * compartment) + seat_number
                cursor.execute(
                    "INSERT INTO SEATS (WagonID, SeatNumber, CompartmentNumber) VALUES (?, ?, ?)",
                    (wagon_id, seat_id, compartment),
                )
                seat_number += 1
            seat_number = 1
    else:
        seat_number = 1
        total_seats = 120 if size == "large" else 80
        for _ in range(1, total_seats + 1):
            cursor.execute(
                "INSERT INTO SEATS (WagonID, SeatNumber, CompartmentNumber) VALUES (?, ?, ?)",
                (wagon_id, seat_number, 0),
            )
            seat_number += 1

def create_wagons(cursor, train_id, line_number):
    global wagon_id
    num_wagons = random.randint(2, 8)
    mandatory_classes = [1, 2]
    classes = [1, 2, 3]

    wagons = []

    # Ensure at least one wagon of each mandatory class
    for wagon_class in mandatory_classes:
        size = "large" if len(wagons) < 2 else random.choice(["large", "small"])
        is_compartmental = random.choice([True, False])
        wagons.append((train_id, is_compartmental, wagon_class, size))

    # Generate remaining wagons randomly
    for _ in range(num_wagons - len(wagons)):
        wagon_class = random.choice(classes)
        size = "large" if len(wagons) < 2 else random.choice(["large", "small"])
        is_compartmental = wagon_class in [1, 2, 3]
        wagons.append((train_id, is_compartmental, wagon_class, size))

    # Insert wagons and their seats
    for (train_id, is_compartmental, wagon_class, size) in wagons:
        cursor.execute(
            "INSERT INTO WAGON (TrainID, ID) VALUES (?, ?)",
            (train_id, wagon_id),
        )
        wagon_id += 1
        create_seats(cursor, wagon_id, is_compartmental, wagon_class, size)


def populate_database():
    conn = sqlite3.connect("./backend/database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT ID, LineNumber FROM LINES")
    lines = cursor.fetchall()

    for line_id, line_number in lines:
        train_name = generate_train_name(line_number)

        # Insert train
        cursor.execute(
            "INSERT INTO TRAINS (TrainName, LineID) VALUES (?, ?)",
            (train_name, line_id),
        )
        train_id = cursor.lastrowid

        # Create wagons and seats for the train
        create_wagons(cursor, train_id, line_number)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    populate_database()
