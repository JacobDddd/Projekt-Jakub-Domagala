from database_conn import get_database_connection

conn = get_database_connection()

def get_user_all_reservations(user_id):
    cursor = conn.cursor()
    data = cursor.execute(
        """
        SELECT *
        FROM RESERVATIONS
        WHERE UserID = ?
        """,
        (user_id,),
    ).fetchall()
    reservations = []
    for row in data:
        reservation_id = row[0]
        reservation_date = row[1]

        stops = cursor.execute(
            """
            SELECT s1.City as StartCity, s2.City as EndCity
            FROM RESERVATIONS_STOPS rs
            JOIN STOPS s1 ON rs.StopID = s1.ID
            JOIN STOPS s2 ON rs.StopID = s2.ID
            WHERE rs.MainReservationID = ?
            ORDER BY rs.ReservationStopOrder
            """,
            (reservation_id,)
        ).fetchall()

        if stops:
            start_city = stops[0][0]
            end_city = stops[-1][1]
        else:
            start_city = None
            end_city = None

        reservations.append({
            'ReservationID': reservation_id,
            'ReservationDate': reservation_date,
            'StartCity': start_city,
            'EndCity': end_city
        })

    return reservations

def get_user_specific_reservation_data(user_id, reservation_id):
    cursor = conn.cursor()
    reservation_data = cursor.execute(
        """
        SELECT r.ID as ReservationID, r.ReservationDate, s1.City as StartCity, s2.City as EndCity
        FROM RESERVATIONS r
        JOIN RESERVATIONS_STOPS rs ON r.ID = rs.MainReservationID
        JOIN STOPS s1 ON rs.StopID = s1.ID
        JOIN STOPS s2 ON rs.StopID = s2.ID
        WHERE r.UserID = ? AND r.ID = ?
        ORDER BY rs.ReservationStopOrder
        """,
        (user_id, reservation_id)
    ).fetchone()

    if not reservation_data:
        return None

    connections = cursor.execute(
        """
        SELECT t.TrainName, w.ID as WagonID, s.SeatNumber, s.CompartmentNumber, s1.City as StartCity, s2.City as EndCity
        FROM RESERVATIONS_STOPS rs
        JOIN SEATS s ON rs.SeatID = s.ID
        JOIN WAGON w ON s.WagonID = w.ID
        JOIN TRAINS t ON w.TrainID = t.ID
        JOIN STOPS s1 ON rs.StopID = s1.ID
        JOIN STOPS s2 ON rs.StopID = s2.ID
        WHERE rs.MainReservationID = ?
        ORDER BY rs.ReservationStopOrder
        """,
        (reservation_id,)
    ).fetchall()

    connection_list = []
    for idx, connection in enumerate(connections, start=1):
        connection_list.append({
            'ConnectionNumber': idx,
            'TrainName': connection['TrainName'],
            'WagonID': connection['WagonID'],
            'SeatNumber': connection['SeatNumber'],
            'Route': [connection['StartCity'], connection['EndCity']]
        })

    return {
        'ReservationID': reservation_data['ReservationID'],
        'ReservationDate': reservation_data['ReservationDate'],
        'StartCity': reservation_data['StartCity'],
        'EndCity': reservation_data['EndCity'],
        'Connections': connection_list
    }

def add_reservation(user_id, stops, seats):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO RESERVATIONS (UserID, ReservationDate)
        VALUES (?, date('now'))
        """,
        (user_id,)
    )
    reservation_id = cursor.lastrowid

    for idx, (stop_id, seat_id) in enumerate(zip(stops, seats), start=1):
        cursor.execute(
            """
            INSERT INTO RESERVATIONS_STOPS (MainReservationID, StopID, SeatID, ReservationStopOrder)
            VALUES (?, ?, ?, ?)
            """,
            (reservation_id, stop_id, seat_id, idx)
        )

    conn.commit()
    return reservation_id

def remove_reservation(user_id, reservation_id):
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM RESERVATIONS
        WHERE UserID = ? AND ID = ?
        """,
        (user_id, reservation_id)
    )
    conn.commit()
    return cursor.rowcount

def get_all_reservations_for_buying_tickets():
    pass

def get_reservation_day_density(date, stops, linesIds):
    cursor = conn.cursor()
    density = {}

    for line in linesIds:
        total_seats = cursor.execute(
            """
            SELECT COUNT(*)
            FROM SEATS s
            JOIN WAGON w ON s.WagonID = w.ID
            JOIN TRAINS t ON w.TrainID = t.ID
            WHERE t.LineID = ?
            """,
            (line,)
        ).fetchone()[0]

        reserved_seats = cursor.execute(
            """
            SELECT COUNT(*)
            FROM RESERVATIONS_STOPS rs
            JOIN RESERVATIONS r ON rs.MainReservationID = r.ID
            JOIN SEATS s ON rs.SeatID = s.ID
            JOIN WAGON w ON s.WagonID = w.ID
            JOIN TRAINS t ON w.TrainID = t.ID
            WHERE t.LineID = ? AND r.ReservationDate = ? AND rs.StopID IN (SELECT ID FROM STOPS WHERE City IN ({}))
            """.format(','.join('?' * len(stops))),
            (line, date, *stops)
        ).fetchone()[0]

        if total_seats > 0:
            density[line] = int((reserved_seats / total_seats) * 100)
        else:
            density[line] = 0

    return density

def get_available_seats_for_day(date, line):
    cursor = conn.cursor()
    try:
        lineID = cursor.execute(
            """
            SELECT ID
            FROM LINES
            WHERE LineNumber = ?
            """,
            (line,)
        ).fetchone()[0]
    except TypeError:
        lineID = line

    wagons = cursor.execute(
        """
        SELECT w.ID as WagonID, w.TrainID, t.LineID
        FROM WAGON w
        JOIN TRAINS t ON w.TrainID = t.ID
        WHERE t.LineID = ?
        """,
        (lineID,)
    ).fetchall()

    available_seats_by_id = {}
    available_seats_by_number = {}
    for wagon in wagons:
        seats = cursor.execute(
            """
            SELECT s.ID as SeatID, s.SeatNumber, s.CompartmentNumber
            FROM SEATS s
            WHERE s.WagonID = ?
            """,
            (wagon[0],)
        ).fetchall()

        reserved_seats = cursor.execute(
            """
            SELECT s.ID as SeatID
            FROM RESERVATIONS_STOPS rs
            JOIN RESERVATIONS r ON rs.MainReservationID = r.ID
            JOIN SEATS s ON rs.SeatID = s.ID
            WHERE r.ReservationDate = ? AND rs.StopID IN (SELECT ID FROM STOPS WHERE City IN (SELECT City FROM STOPS WHERE ID IN (SELECT StopID FROM LINE_STOPS WHERE LineID = ?)))
            """,
            (date, lineID)
        ).fetchall()

        reserved_seat_ids = set(seat[0] for seat in reserved_seats)

        wagon_info_by_id = {
            'class': 'compartment' if any(seat[2] != 0 for seat in seats) else 'non-compartment',
            'seats': {}
        }
        wagon_info_by_number = {
            'class': 'compartment' if any(seat[2] != 0 for seat in seats) else 'non-compartment',
            'seats': {}
        }

        for seat in seats:
            if seat[0] not in reserved_seat_ids:
                if wagon_info_by_id['class'] == 'compartment':
                    if seat[2] not in wagon_info_by_id['seats']:
                        wagon_info_by_id['seats'][seat[2]] = []
                        wagon_info_by_number['seats'][seat[2]] = []
                    wagon_info_by_id['seats'][seat[2]].append(seat[0])
                    wagon_info_by_number['seats'][seat[2]].append(seat[1])
                else:
                    if 0 not in wagon_info_by_id['seats']:
                        wagon_info_by_id['seats'][0] = []
                        wagon_info_by_number['seats'][0] = []
                    wagon_info_by_id['seats'][0].append(seat[0])
                    wagon_info_by_number['seats'][0].append(seat[1])

        available_seats_by_id[wagon[0]] = wagon_info_by_id
        available_seats_by_number[wagon[0]] = wagon_info_by_number

    return available_seats_by_id, available_seats_by_number


def make_reservations(user_data, path, date, lines_with_reservations):
    cursor = conn.cursor()

    # Insert new reservation
    cursor.execute(
        """
        INSERT INTO RESERVATIONS (UserID, ReservationDate)
        VALUES (?, ?)
        """,
        (user_data['ID'], date)
    )
    reservation_id = cursor.lastrowid

    # Insert stops and seats into RESERVATIONS_STOPS
    line_ids = {}
    line_names = list(lines_with_reservations.keys())
    lines_for_query_count = ", ".join('?' * len(line_names))
    line_ids_query = cursor.execute(
        """
        SELECT LineNumber, ID
        FROM LINES
        WHERE LineNumber IN ({0})
        """.format(lines_for_query_count),
        line_names
    ).fetchall()

    line_ids = {line[0]: line[1] for line in line_ids_query}

    # Replace key values of lines_with_reservations with new line ids
    lines_with_reservations = {line_ids[line]: seat for line, seat in lines_with_reservations.items()}
    iteration = 1
    for line_id, stops in path.items():
        for stop_id in set(stops):  # Remove duplicate stops
            seat_id = lines_with_reservations.get(line_id)
            if seat_id:
                cursor.execute(
                    """
                    INSERT INTO RESERVATIONS_STOPS (MainReservationID, StopID, SeatID, ReservationStopOrder)
                    VALUES (?, ?, ?, ?)
                    """,
                    (reservation_id, stop_id, seat_id, iteration)
                )
                iteration += 1

    conn.commit()
    return reservation_id
