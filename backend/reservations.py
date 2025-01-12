import sqlite3
from datetime import datetime
from user_verification import get_user
from database_conn import get_database_connection

# Function to check if a user is logged in (in this example, it returns a placeholder)
def is_logged_in(username):
    """Simulates checking if a user is logged in."""
    return username is not None  # This is a placeholder; replace with actual login check.

# Function to get all reservations for a user
def get_reservations_for_user(conn, user_id):
    """Fetch all reservations made by a user."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.ID, s.SeatNumber, w.TrainID, t.TrainName, st.City, r.ReservationDate
        FROM RESERVATIONS r
        JOIN SEATS s ON r.SeatID = s.ID
        JOIN WAGON w ON s.WagonID = w.ID
        JOIN TRAINS t ON w.TrainID = t.ID
        JOIN STOPS st ON s.SeatNumber = st.ID
        WHERE r.UserID = ?
    """, (user_id,))
    return cursor.fetchall()

# Function to get all reservations for a specific train
def get_reservations_for_train(conn, train_id):
    """Fetch all reservations made for a specific train."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.ID, s.SeatNumber, u.Username, r.ReservationDate
        FROM RESERVATIONS r
        JOIN SEATS s ON r.SeatID = s.ID
        JOIN USERS u ON r.UserID = u.ID
        WHERE s.WagonID IN (SELECT ID FROM WAGON WHERE TrainID = ?)
    """, (train_id,))
    return cursor.fetchall()

# Function to get all reservations for a specific wagon
def get_reservations_for_wagon(conn, wagon_id):
    """Fetch all reservations made for a specific wagon."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.ID, s.SeatNumber, u.Username, r.ReservationDate
        FROM RESERVATIONS r
        JOIN SEATS s ON r.SeatID = s.ID
        JOIN USERS u ON r.UserID = u.ID
        WHERE s.WagonID = ?
    """, (wagon_id,))
    return cursor.fetchall()

# Function to create reservations (with multiple seats at once)
def create_reservation(conn, seat_ids, user_id, reservation_date):
    """Creates multiple reservations for a user."""
    cursor = conn.cursor()

    # Check if any of the seats are already reserved
    for seat_id in seat_ids:
        cursor.execute("SELECT ID FROM RESERVATIONS WHERE SeatID = ?", (seat_id,))
        if cursor.fetchone():
            print(f"Seat {seat_id} is already reserved.")
            return None

    # Create reservations for all seats
    for seat_id in seat_ids:
        cursor.execute("""
            INSERT INTO RESERVATIONS (SeatID, UserID, ReservationDate)
            VALUES (?, ?, ?)
        """, (seat_id, user_id, reservation_date))

    conn.commit()
    print(f"Reservations created for seats {', '.join(map(str, seat_ids))} on {reservation_date}.")
    return True

# Function to remove multiple reservations
def remove_reservations(conn, reservation_ids, user_id):
    """Removes multiple reservations for a user."""
    cursor = conn.cursor()

    # Verify that the reservations belong to the user
    cursor.execute("SELECT ID, UserID FROM RESERVATIONS WHERE ID IN ({})".format(','.join('?'*len(reservation_ids))), tuple(reservation_ids))
    reservations = cursor.fetchall()

    for reservation in reservations:
        if reservation[1] == user_id:
            cursor.execute("DELETE FROM RESERVATIONS WHERE ID = ?", (reservation[0],))
        else:
            print(f"Reservation {reservation[0]} does not belong to the user.")

    conn.commit()
    print(f"Reservations {', '.join(map(str, reservation_ids))} removed.")

# Function to handle reservation actions (for logged-in and non-logged-in users)
def handle_reservation_action(conn, username, action, seat_ids=None, reservation_ids=None, train_id=None, wagon_id=None):
    """Handles reservation creation, deletion, or listing."""
    if not is_logged_in(username):
        print("Please log in to manage reservations.")
        return

    user = get_user(conn, username)  # Fetch user details
    if not user:
        print("User not found.")
        return

    user_id = user["ID"]

    if action == "view":
        if train_id:
            reservations = get_reservations_for_train(conn, train_id)
            print("Reservations for Train:")
            for res in reservations:
                print(f"User: {res[2]}, Seat: {res[1]}, Date: {res[3]}")
        elif wagon_id:
            reservations = get_reservations_for_wagon(conn, wagon_id)
            print("Reservations for Wagon:")
            for res in reservations:
                print(f"User: {res[2]}, Seat: {res[1]}, Date: {res[3]}")
        else:
            reservations = get_reservations_for_user(conn, user_id)
            print("Your reservations:")
            for res in reservations:
                print(f"Train: {res[3]}, Seat: {res[1]}, Stop: {res[4]}, Date: {res[5]}")

    elif action == "create":
        if seat_ids:
            reservation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current timestamp for reservation
            create_reservation(conn, seat_ids, user_id, reservation_date)
        else:
            print("Please provide valid seat(s) to reserve.")

    elif action == "delete":
        if reservation_ids:
            remove_reservations(conn, reservation_ids, user_id)
        else:
            print("Please provide valid reservation IDs to delete.")

# Assuming the necessary user interaction and inputs are provided, here's an example:

if __name__ == "__main__":
    conn = get_database_connection()

    # Test cases (assuming 'john_doe' is a valid username)
    username = "john_doe"  # Replace with actual username
    action = "view"  # Action can be "view", "create", or "delete"

    # Action: View reservations for logged-in user
    handle_reservation_action(conn, username, action)

    # Action: View reservations for a specific train
    train_id = 1  # Example train ID
    handle_reservation_action(conn, username, "view", train_id=train_id)

    # Action: Create multiple reservations for specific seats
    action = "create"
    seat_ids = [123, 124, 125]  # Example seat IDs
    handle_reservation_action(conn, username, action, seat_ids=seat_ids)

    # Action: Delete multiple reservations
    action = "delete"
    reservation_ids = [1, 2]  # Example reservation IDs to delete
    handle_reservation_action(conn, username, action, reservation_ids=reservation_ids)

    conn.close()
