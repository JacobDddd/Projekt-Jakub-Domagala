import customtkinter as ctk
import tkinter as Tk
from frontend.middleware_handler import change_window_size, change_theme, dump_settings, load_settings, update_yaml_data_settings


class ViewFrameSettings(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.pack(fill=Tk.BOTH, expand=True)

        self.yaml_data = load_settings()
        self.create_widgets()
        self.apply_settings()

    def create_widgets(self):
        self.title_label = ctk.CTkLabel(self, text="USTAWIENIA APLIKACJI", font=("Arial", 24))
        self.title_label.pack(pady=(20, 10))

        self.window_size_label = ctk.CTkLabel(self, text="Rozmiar okna:", anchor="w", width=300)
        self.window_size_label.pack()

        self.window_size_menu = ctk.CTkComboBox(self, values=["1200x850", "1000x700", "800x600"], width=300)
        self.window_size_menu.set(self.yaml_data["window_size"]["selected"])
        self.window_size_menu.pack(pady=(0, 20))

        self.theme_mode_label = ctk.CTkLabel(self, text="Motyw kolorystyczny:", anchor="w", width=300)
        self.theme_mode_label.pack()

        self.theme_mode_menu = ctk.CTkComboBox(self, values=["Jasny", "Ciemny", "Systemowy"], width=300)
        self.theme_mode_menu.set(self.yaml_data["theme_mode"]["selected"])
        self.theme_mode_menu.pack(pady=(0, 20))

        self.apply_and_save_button = ctk.CTkButton(self, text="Zapisz i zastosuj", command=self.apply_settings)
        self.apply_and_save_button.pack()


    def apply_settings(self):
        update_yaml_data_settings(self.yaml_data, "window_size", self.window_size_menu.get())
        update_yaml_data_settings(self.yaml_data, "theme_mode", self.theme_mode_menu.get())
        dump_settings(self.yaml_data)
        change_window_size(self.yaml_data, self.master.master.master)
        change_theme(self.yaml_data, self.master.master.master)

    def reset_view_frame(self):
        self.yaml_data = load_settings()
        self.window_size_menu.set(self.yaml_data["window_size"]["selected"])
        self.theme_mode_menu.set(self.yaml_data["theme_mode"]["selected"])