import customtkinter as ctk
import tkinter as Tk
from tkinter import ttk
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from user_verification import add_user, get_user_with_verification, verify_user
from database_conn import get_database_connection
from data_handler_frontend import get_user_all_reservations, remove_reservation

class AccountViewFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.pack(fill=Tk.BOTH, expand=True)

        self.account_label = ctk.CTkLabel(self, text="Twoje konto")
        self.account_label.pack(pady=10)

        self.login_button = ctk.CTkButton(self, text="Zaloguj się", command=self.login)
        self.login_button.pack(pady=10)

        self.register_button = ctk.CTkButton(self, text="Zarejestruj się", command=self.register)
        self.register_button.pack(pady=10)

        self.logout_button = ctk.CTkButton(self, text="Wyloguj się", command=self.logout)
        self.logout_button.pack(pady=10)

        self.reservation_button = ctk.CTkButton(self, text="Twoje rezerwacje", command=self.reservation)
        self.reservation_button.pack(pady=10)

        self.user_data = None
        self.login_frame = None
        self.register_frame = None
        self.back_button = ctk.CTkButton(self, text="X", command=self.load_user_data, width=30, height=30)
        self.back_button.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)
        self.back_button.pack_forget()

        self.reservation_tab = ReservationsTabView(self)

        self.load_user_data()


    def reservation(self):
        self.back_button.pack(pady=10)
        self.reservation_tab.pack(fill=Tk.BOTH, expand=True)
        self.reservation_tab.load_reservations()
        self.login_button.pack_forget()
        self.register_button.pack_forget()
        self.logout_button.pack_forget()
        self.reservation_button.pack_forget()

    def load_user_data(self):
        if self.login_frame:
            self.login_frame.pack_forget()
        if self.register_frame:
            self.register_frame.pack_forget()
        if self.back_button:
            self.back_button.pack_forget()
        if self.reservation_tab:
            self.reservation_tab.pack_forget()
        if self.back_button:
            self.back_button.pack_forget()

        if self.user_data:
            self.account_label.configure(text=f"Witaj, {self.user_data['Username']}!")
            self.login_button.pack_forget()
            self.register_button.pack_forget()
            self.logout_button.pack(pady=10)
            self.reservation_button.pack(pady=10)
        else:
            self.account_label.configure(text="Zaloguj się lub zarejestruj, aby skorzystać z konta.")
            self.logout_button.pack_forget()
            self.login_button.pack(pady=10)
            self.register_button.pack(pady=10)
            self.reservation_button.pack_forget()

    def login(self):
        self.back_button.pack(pady=10)
        self.login_form()

    def register(self):
        self.back_button.pack(pady=10)
        self.register_form()

    def logout(self):
        self.user_data = None
        self.load_user_data()

    def login_form(self):
        self.login_button.pack_forget()
        self.register_button.pack_forget()
        self.logout_button.pack_forget()

        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.pack(pady=10)
        self.login_label_username = ctk.CTkLabel(self.login_frame, text="Nazwa użytkownika:")
        self.login_label_username.pack(pady=5)
        self.login_entry_username = ctk.CTkEntry(self.login_frame)
        self.login_entry_username.pack(pady=5)

        self.login_label_password = ctk.CTkLabel(self.login_frame, text="Hasło:")
        self.login_label_password.pack(pady=5)
        self.login_entry_password = ctk.CTkEntry(self.login_frame, show="*")
        self.login_entry_password.pack(pady=5)

        self.login_button_submit = ctk.CTkButton(self.login_frame, text="Zaloguj", command=self.login_submit)
        self.login_button_submit.pack(pady=5)

    def login_submit(self):
        username = self.login_entry_username.get()
        password = self.login_entry_password.get()
        if verify_user(username=username, password=password):
            self.user_data = get_user_with_verification(username=username, password=password)
            self.load_user_data()
            self.login_frame.pack_forget()
        else:
            self.login_label_password.configure(text="Niepoprawne dane logowania.")
            self.login_entry_password.delete(0, Tk.END)

    def register_form(self):
        self.login_button.pack_forget()
        self.register_button.pack_forget()
        self.logout_button.pack_forget()

        self.register_frame = ctk.CTkFrame(self)
        self.register_frame.pack(pady=10)
        self.register_label_username = ctk.CTkLabel(self.register_frame, text="Nazwa użytkownika:")
        self.register_label_username.pack(pady=5)
        self.register_entry_username = ctk.CTkEntry(self.register_frame)
        self.register_entry_username.pack(pady=5)

        self.register_label_email = ctk.CTkLabel(self.register_frame, text="Email:")
        self.register_label_email.pack(pady=5)
        self.register_entry_email = ctk.CTkEntry(self.register_frame)
        self.register_entry_email.pack(pady=5)

        self.register_label_phone = ctk.CTkLabel(self.register_frame, text="Telefon:")
        self.register_label_phone.pack(pady=5)
        self.register_entry_phone = ctk.CTkEntry(self.register_frame)
        self.register_entry_phone.pack(pady=5)

        self.register_label_password = ctk.CTkLabel(self.register_frame, text="Hasło:")
        self.register_label_password.pack(pady=5)
        self.register_entry_password = ctk.CTkEntry(self.register_frame, show="*")
        self.register_entry_password.pack(pady=5)

        self.register_label_password_confirm = ctk.CTkLabel(self.register_frame, text="Potwierdź hasło:")
        self.register_label_password_confirm.pack(pady=5)
        self.register_entry_password_confirm = ctk.CTkEntry(self.register_frame, show="*")
        self.register_entry_password_confirm.pack(pady=5)

        self.register_button_submit = ctk.CTkButton(self.register_frame, text="Zarejestruj", command=self.register_submit)
        self.register_button_submit.pack(pady=5)

    def register_submit(self):
        username = self.register_entry_username.get()
        email = self.register_entry_email.get()
        phone = self.register_entry_phone.get()
        password = self.register_entry_password.get()
        password_confirm = self.register_entry_password_confirm.get()

        if password == password_confirm:
            add_user(username=username, password=password, email=email, phone=phone)
            self.register_frame.pack_forget()
            self.user_data = get_user_with_verification(username=username, password=password)
            self.load_user_data()
        else:
            self.register_label_password_confirm.configure(text="Hasła nie są takie same.")
            self.register_entry_password.delete(0, Tk.END)
            self.register_entry_password_confirm.delete(0, Tk.END)

    def reset_view_frame(self):
        if self.login_frame:
            self.login_frame.pack_forget()
        if self.register_frame:
            self.register_frame.pack_forget()
        if self.back_button:
            self.back_button.pack_forget()
        if self.reservation_tab:
            self.reservation_tab.pack_forget()
        self.load_user_data()


class ReservationsTabView(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.pack(fill=Tk.BOTH, expand=True)

        self.reservation_label = ctk.CTkLabel(self, text="Twoje rezerwacje")
        self.reservation_label.pack(pady=10)

        self.reservation_list = ttk.Treeview(self, columns=("ReservationID", "ReservationDate", "StartCity", "EndCity"), show='headings')
        self.reservation_list.heading("ReservationID", text="ID Rezerwacji")
        self.reservation_list.heading("ReservationDate", text="Data Rezerwacji")
        self.reservation_list.heading("StartCity", text="Miasto Początkowe")
        self.reservation_list.heading("EndCity", text="Miasto Końcowe")

        self.reservation_list.bind("<Double-1>", self.on_reservation_select)

        # Adjust column widths
        self.reservation_list.column("ReservationID", width=100)  # Reduced by 50%
        self.reservation_list.column("ReservationDate", width=100)  # Reduced by 50%
        self.reservation_list.column("StartCity", width=200)
        self.reservation_list.column("EndCity", width=200)

        self.reservation_list.pack(pady=10)

        self.reservation_button = ctk.CTkButton(self, text="Anuluj rezerwację", command=self.cancel_reservation, state=Tk.DISABLED)
        self.reservation_button.pack(pady=10)

    def on_reservation_select(self, event):
        self.reservation_button.configure(state=Tk.NORMAL)

    def load_reservations(self):
        self.reservation_button.configure(state=Tk.DISABLED)
        for item in self.reservation_list.get_children():
            self.reservation_list.delete(item)
        for reservation in self.get_reservations():
            self.reservation_list.insert("", "end", values=(reservation['ReservationID'],
                                                            reservation['ReservationDate'],
                                                            reservation['StartCity'],
                                                            reservation['EndCity']))

    def get_reservations(self):
        return get_user_all_reservations(self.master.user_data['ID']) if self.master.user_data else []

    def cancel_reservation(self):
        try:
            selected_item = self.reservation_list.selection()[0]
            reservation_id = self.reservation_list.item(selected_item)['values'][0]
            remove_reservation(self.master.user_data['ID'], reservation_id)
            self.load_reservations()
        except Exception:
            pass

