import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
import pytest
import sqlite3

from lines_graph_calc import (
    to_title_case, find_stop_id, build_graph, find_shortest_path_with_transfers,
    format_path_with_lines, display_path_with_names
)

TEST_DATABASE_PATH = "./backend/database.db"

@pytest.fixture(scope="module")
def conn():
    return sqlite3.connect(TEST_DATABASE_PATH)

@pytest.fixture(scope="module")
def graph(conn):
    return build_graph()

def test_find_stop_id(conn):
    assert find_stop_id(to_title_case("KRAKÓW GŁÓWNY")) == 141
    assert find_stop_id(to_title_case("WARSZAWA WSCHODNIA")) == 326
    assert find_stop_id(to_title_case("NON_EXISTENT_CITY")) is None

def test_find_shortest_path_with_transfers(graph):
    start_id = 141  # KRAKÓW GŁÓWNY
    mid_id = 80    # GRODZISK MAZOWIECKI
    end_id = 182   # MAŁKINIA

    path1 = find_shortest_path_with_transfers(graph, start_id, mid_id)
    assert path1 == [141, 136, 80]

    path2 = find_shortest_path_with_transfers(graph, mid_id, end_id)
    assert path2 == [80, 326, 323, 182]

def test_format_path_with_lines(graph):
    path = [141, 136, 80]
    formatted_path = format_path_with_lines(graph, path)
    assert formatted_path == {1: [141, 136, 80]}

def test_display_path_with_names(conn, graph):
    formatted_path = {1: [141, 136, 80]}
    named_path = display_path_with_names(formatted_path)
    assert named_path == {'100': ['Kraków Główny', 'Kozłów', 'Grodzisk Mazowiecki']}