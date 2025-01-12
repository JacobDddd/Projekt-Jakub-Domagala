import customtkinter as ctk
import sys
import os
import tkinter as Tk
from tkinter import ttk
import tkcalendar
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from database_conn import get_database_connection
from data_handler_frontend import get_user_all_reservations, get_reservation_day_density
from data_handler_frontend import get_available_seats_for_day, make_reservations
from lines_graph_calc import find_shortest_path_with_transfers, format_path_with_lines, build_graph, display_path_with_names

conn = get_database_connection()
cursor = conn.cursor()
all_stops = cursor.execute("SELECT ID, City FROM STOPS").fetchall()


class BuyTicketFrame(ctk.CTkFrame):
    def __init__(self, master, account_frame=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.pack(fill="both", expand=True)
        self.account_frame = account_frame
        self.ticket_label = ctk.CTkLabel(self, text="Kup bilet")
        self.ticket_label.pack(pady=10)

        self.container_frame = ctk.CTkFrame(self)
        self.container_frame.pack(pady=10)

        self.from_label = ctk.CTkLabel(self.container_frame, text="Z:")
        self.from_label.pack(side="left", padx=5, pady=5)
        self.from_combobox = ttk.Combobox(self.container_frame, values=[stop[1] for stop in all_stops])
        self.from_combobox.pack(side="left", padx=5, pady=5)
        self.from_combobox.bind('<KeyRelease>', self.filter_stops)

        self.to_label = ctk.CTkLabel(self.container_frame, text="Do:")
        self.to_label.pack(side="left", padx=5, pady=5)
        self.to_combobox = ttk.Combobox(self.container_frame, values=[stop[1] for stop in all_stops])
        self.to_combobox.pack(side="left", padx=5, pady=5)
        self.to_combobox.bind('<KeyRelease>', self.filter_stops)

        self.date_label = ctk.CTkLabel(self.container_frame, text="Data:")
        self.date_label.pack(side="left", padx=5, pady=5)
        self.date_entry = tkcalendar.DateEntry(self.container_frame, date_pattern='dd/MM/yyyy')
        self.date_entry.pack(side="left", padx=5, pady=5)

        self.check_and_buy_button = ctk.CTkButton(self, text="Sprawdź dostępność i kup bilet", command=self.check_and_buy)
        self.check_and_buy_button.pack(pady=10)

    def filter_stops(self, event):
        widget = event.widget
        value = widget.get().lower()
        filtered_stops = [stop[1] for stop in all_stops if value in stop[1].lower()]
        widget['values'] = filtered_stops

    def check_and_buy(self):
        from_stop_name = self.from_combobox.get()
        to_stop_name = self.to_combobox.get()
        from_id = next(stop[0] for stop in all_stops if stop[1] == from_stop_name)
        to_id = next(stop[0] for stop in all_stops if stop[1] == to_stop_name)
        date = self.date_entry.get_date().strftime('%Y-%m-%d')

        graph = build_graph()
        path = find_shortest_path_with_transfers(graph, from_id, to_id)
        formatted_path = format_path_with_lines(graph, path)
        formatted_path_human_readable = display_path_with_names(formatted_path)

        if path:
            for widget in self.winfo_children():
                if isinstance(widget, TrainScheduleFrame):
                    widget.destroy()
            self.display_schedule(formatted_path_human_readable, formatted_path, date)
        else:
            no_path_label = ctk.CTkLabel(self.master, text="Brak dostępnego połączenia")
            no_path_label.pack(pady=10)

    def display_schedule(self, path, pathID, date):
        schedule_frame = TrainScheduleFrame(self, path, pathID, date)
        schedule_frame.pack(fill="both", expand=True)

    def reset_view_frame(self):
        for widget in self.winfo_children():
            if isinstance(widget, TrainScheduleFrame):
                widget.destroy()


class TrainScheduleFrame(ctk.CTkFrame):
    def __init__(self, master, path, pathID, date, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.pack(fill="both", expand=True)
        self.schedule_label = ctk.CTkLabel(self, text="Rozkład jazdy")
        self.schedule_label.pack(pady=10)

        # Configure a frame to handle resizing
        treeview_frame = ctk.CTkFrame(self)
        treeview_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(treeview_frame, columns=("nr_pociagu", "trasa", "wypelnienie"), show="headings")
        self.tree.heading("nr_pociagu", text="Nr Pociągu")
        self.tree.heading("trasa", text="Trasa")
        self.tree.heading("wypelnienie", text="Wypełnienie (%)")
        self.tree.column("nr_pociagu", minwidth=100, width=100)
        self.tree.column("wypelnienie", minwidth=100, width=100)
        self.tree.column("trasa", minwidth=300, width=500)

        # Add vertical scrollbar for the treeview
        scrollbar = ttk.Scrollbar(treeview_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.path = path
        self.path_with_id = pathID
        self.date = date
        self.make_reservation_empty_memory_dict()
        self.load_schedule()

    def load_schedule(self):
        for line, stops in self.path.items():
            density = get_reservation_day_density(self.date, stops, [line])
            self.tree.insert("", "end", values=(line, " - ".join(stops), density[line]))

        self.add_reservation_buttons()

    def make_reservation_empty_memory_dict(self):
        self.chosen_reservations = {}
        for line in self.path.keys():
            self.chosen_reservations[line] = None

    def add_reservation_buttons(self):
        # Create a scrollable frame for the buttons
        button_frame = ctk.CTkScrollableFrame(self, orientation="horizontal", height=50)
        button_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Add buttons to the button_frame
        for idx, line in enumerate(self.path.keys(), start=1):
            button = ctk.CTkButton(button_frame, text=f"Wybierz rezerwację na przesiadce {idx}", command=lambda l=line, d=self.date: self.select_reservation(l, d))
            button.pack(side="left", padx=10, pady=5)

        # Create a frame for the "Zakończ rezerwację" button
        finish_button_frame = ctk.CTkFrame(self)
        finish_button_frame.pack(side="right", padx=5, pady=5)

        # Add the "Zakończ rezerwację" button
        self.finish_button = ctk.CTkButton(finish_button_frame, text="Zakończ rezerwację", state="disabled", command=self.finish_reservation)
        self.finish_button.pack()

    def select_reservation(self, line, date):
        reservation_window = ReservationWindow(self, line, date)
        reservation_window.grab_set()
        reservation_window.wait_window()
        self.check_if_all_reservations_are_selected()

    def check_if_all_reservations_are_selected(self):
        if all(self.chosen_reservations.values()) and self.master.account_frame.user_data:
            self.finish_button.configure(state="normal")
        else:
            self.finish_button.configure(state="disabled")

    def finish_reservation(self):
        make_reservations(self.master.account_frame.user_data, self.path_with_id, self.date, self.chosen_reservations)
        self.destroy()

class ReservationWindow(ctk.CTkToplevel):
    def __init__(self, master, line, date, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.line = line
        self.date = date
        self.selected_seat = None

        self.title(f"Rezerwacja - Linia {line}")
        self.geometry("600x400")

        self.label = ctk.CTkLabel(self, text=f"Wybierz wagon i miejsce dla linii {line}")
        self.label.pack(pady=10)

        self.wagon_listbox = ttk.Treeview(self, show="tree")
        self.wagon_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.wagon_listbox.bind('<Double-1>', self.on_wagon_select)

        self.confirm_button = ctk.CTkButton(self, text="Zatwierdź", state="disabled", command=self.confirm_selection)
        self.confirm_button.pack(pady=10)
        self.line_reservation_data = get_available_seats_for_day(self.date, self.line)

        self.load_wagons()

    def load_wagons(self):
        for idx, wagon_data in enumerate(self.line_reservation_data[1].values(), start=1):
            self.wagon_listbox.insert("", "end", text=f"Wagon {idx} - {wagon_data['class']}")

    def on_wagon_select(self, _):
        selected_wagon_index = self.wagon_listbox.index(self.wagon_listbox.selection()[0])
        self.selected_wagon_id = list(self.line_reservation_data[1].keys())[selected_wagon_index]
        selected_wagon_data = self.line_reservation_data[1][self.selected_wagon_id]
        self.selected_wagon_data_with_ids = {self.selected_wagon_id: self.line_reservation_data[0][self.selected_wagon_id]}

        if selected_wagon_data['class'] == 'compartment':
            self.show_compartment_selection(self.selected_wagon_id, selected_wagon_data)
        else:
            self.show_seat_selection(self.selected_wagon_id, selected_wagon_data['seats'][0])

    def show_compartment_selection(self, wagon_id, wagon_data):
        self.wagon_listbox.delete(*self.wagon_listbox.get_children())
        for compartment_id in wagon_data['seats'].keys():
            self.wagon_listbox.insert("", "end", text=f"Przedział {compartment_id}")
        self.wagon_listbox.bind('<Double-1>', lambda event: self.on_compartment_select(event, wagon_id, wagon_data))

    def on_compartment_select(self, event, wagon_id, wagon_data):
        selected_compartment_index = self.wagon_listbox.index(self.wagon_listbox.selection()[0])
        selected_compartment_id = list(wagon_data['seats'].keys())[selected_compartment_index]
        self.selected_compartment_id = selected_compartment_id
        selected_seats = wagon_data['seats'][selected_compartment_id]
        self.seat_data_with_ids = {selected_compartment_id: self.line_reservation_data[0][wagon_id]["seats"][selected_compartment_id]}

        self.show_seat_selection(wagon_id, selected_seats)

    def show_seat_selection(self, wagon_id, seats):
        self.wagon_listbox.delete(*self.wagon_listbox.get_children())
        for seat in seats:
            self.wagon_listbox.insert("", "end", text=f"Miejsce {seat}")
        self.wagon_listbox.bind('<Double-1>', lambda event: self.on_seat_select(event, wagon_id))

    def on_seat_select(self, _, wagon_id):
        selected_seat_index = self.wagon_listbox.index(self.wagon_listbox.selection()[0])
        self.selected_seat_idx = selected_seat_index
        self.confirm_button.configure(state="normal")

    def confirm_selection(self):
        if self.selected_seat_idx is not None:
            chosen_wagon = self.line_reservation_data[0][self.selected_wagon_id]
            if chosen_wagon['class'] == 'compartment':
                chosen_compartment = self.selected_compartment_id
            else:
                chosen_compartment = 0
            chosen_seat_id = self.line_reservation_data[0][self.selected_wagon_id]["seats"][chosen_compartment][self.selected_seat_idx]
            self.master.chosen_reservations[self.line] = chosen_seat_id
            self.master.check_if_all_reservations_are_selected()
            self.destroy()
