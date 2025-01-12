from collections import defaultdict, deque
from database_conn import get_database_connection
import sqlite3

conn = get_database_connection()

def to_title_case(s):
    """Converts a string to title case."""
    return s.title()

def find_stop_id(city_name):
    """Finds the StopID for a given city name."""
    global conn
    cursor = conn.cursor()

    cursor.execute("SELECT ID FROM STOPS WHERE LOWER(City) LIKE LOWER(?)", (city_name,))
    result = cursor.fetchone()

    return result[0] if result else None

def get_stop_name(stop_id):
    """Finds the City name for a given StopID."""
    global conn
    cursor = conn.cursor()

    cursor.execute("SELECT City FROM STOPS WHERE ID = ?", (stop_id,))
    result = cursor.fetchone()

    return result[0] if result else None

def build_graph():
    """Builds a graph representation from LINE_STOPS."""
    global conn
    cursor = conn.cursor()

    # Pobieranie danych z LINE_STOPS
    cursor.execute("SELECT LineID, StopOrder, StopID FROM LINE_STOPS")
    stops = cursor.fetchall()

    graph = defaultdict(list)

    # Budowa grafu w oparciu o StopOrder
    line_stops = defaultdict(list)
    for line_id, stop_order, stop_id in stops:
        line_stops[line_id].append((stop_order, stop_id))

    for line_id, stops in line_stops.items():
        stops.sort()  # Sortowanie według StopOrder
        for i in range(len(stops) - 1):
            current_stop = stops[i][1]
            next_stop = stops[i + 1][1]
            graph[current_stop].append((next_stop, line_id))
            graph[next_stop].append((current_stop, line_id))  # Dwukierunkowe połączenie

    return graph

def find_shortest_path_with_transfers(graph, start_id, end_id):
    """Finds the shortest path allowing for line transfers, with at least two stops."""
    queue = deque([(start_id, [], None, 0)])  # (current_stop, path, current_line, transfers)
    visited = set()

    while queue:
        current_stop, path, current_line, transfers = queue.popleft()

        if (current_stop, current_line) in visited:
            continue

        visited.add((current_stop, current_line))
        path = path + [current_stop]

        # Check if the path reaches the end and has at least one intermediate stop
        if current_stop == end_id and len(path) > 2:
            return path

        for neighbor, line_id in graph[current_stop]:
            if (neighbor, line_id) not in visited:
                if current_line is None or current_line == line_id:
                    queue.append((neighbor, path, line_id, transfers))
                else:
                    queue.append((neighbor, path, line_id, transfers + 1))

    return None  # No path found

def format_path_with_lines(graph, path):
    """Formats the path into a dictionary grouping stops by line."""
    if not path:
        return {}

    formatted_path = defaultdict(list)
    current_line = None
    for i in range(len(path) - 1):
        current_stop = path[i]
        next_stop = path[i + 1]
        for neighbor, line_id in graph[current_stop]:
            if neighbor == next_stop:
                if current_line is None or current_line == line_id:
                    formatted_path[line_id].append(current_stop)
                    current_line = line_id
                else:
                    formatted_path[current_line].append(current_stop)
                    formatted_path[line_id].append(current_stop)
                    current_line = line_id
                break

    # Add the final stop to the last line
    if path:
        last_line = list(formatted_path.keys())[-1]
        formatted_path[last_line].append(path[-1])

    # Remove any lines with only one stop
    formatted_path = {line: stops for line, stops in formatted_path.items() if len(stops) > 1}

    return formatted_path

def get_line_name(line_id):
    """Finds the LineNumber for a given LineID."""
    global conn
    cursor = conn.cursor()

    cursor.execute("SELECT LineNumber FROM LINES WHERE ID = ?", (line_id,))
    result = cursor.fetchone()

    return result[0] if result else None

def display_path_with_names(formatted_path):
    """Converts stop IDs in the formatted path to names and includes line names."""
    named_path = {}
    for line_id, stops in formatted_path.items():
        line_name = get_line_name(line_id)
        named_path[line_name] = [get_stop_name(stop_id) for stop_id in stops]
    return named_path

if __name__ == "__main__":
    # Build graph
    graph = build_graph()

    # Example cities
    start_city = "KRAKÓW GŁÓWNY"
    mid_city = "GRODZISK MAZOWIECKI"
    end_city = "MAŁKINIA"

    # Find stop IDs
    start_id = find_stop_id(to_title_case(start_city))
    mid_id = find_stop_id(to_title_case(mid_city))
    end_id = find_stop_id(to_title_case(end_city))

    if not start_id or not mid_id or not end_id:
        print("One or more cities not found in the database.")
    else:
        # Find paths
        print(f"Finding path from {start_city} to {mid_city}...")
        path1 = find_shortest_path_with_transfers(graph, start_id, mid_id)
        if path1 and len(path1) > 2:
            formatted_path1 = format_path_with_lines(graph, path1)
            named_path1 = display_path_with_names(formatted_path1)
            print(f"Path by line (IDs): {dict(formatted_path1)}")
            print(f"Path by line (Names): {named_path1}")
        else:
            print("No valid path found with at least one intermediate stop.")

        print(f"Finding path from {mid_city} to {end_city}...")
        path2 = find_shortest_path_with_transfers(graph, mid_id, end_id)
        if path2 and len(path2) > 2:
            formatted_path2 = format_path_with_lines(graph, path2)
            named_path2 = display_path_with_names(formatted_path2)
            print(f"Path by line (IDs): {dict(formatted_path2)}")
            print(f"Path by line (Names): {named_path2}")
        else:
            print("No valid path found with at least one intermediate stop.")
