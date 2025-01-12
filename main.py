import tkinter as Tk
import customtkinter as ctk
from frontend.GUI_account import AccountViewFrame
from frontend.GUI_menu import ViewFrameSettings
from frontend.GUI_ticket import BuyTicketFrame

from frontend.middleware_handler import load_and_apply_settings

def main():
    root = Tk.Tk()
    root.title("Aplikacja do zarządzania rezerwacjami biletów")
    root.resizable(False, False)
    load_and_apply_settings(root)
    ctk.set_default_color_theme("blue")

    tab_view = ctk.CTkTabview(root)
    tab_view.pack(fill=Tk.BOTH, expand=True, padx=10, pady=10)

    tab_view.add("KONTO")
    tab_view.add("KUP BILET")
    tab_view.add("USTAWIENIA APLIKACJI")

    # Ważne, aby to było pierwsze - wartości user z frame są przekazywane do innych frame'ów, zwłaszcza buy_ticket_frame
    def load_account_view():
        global account_view_frame
        account_view_frame = AccountViewFrame(tab_view.tab("KONTO"))

    def load_buy_ticket_view():
        global buy_ticket_frame
        buy_ticket_frame = BuyTicketFrame(tab_view.tab("KUP BILET"), account_view_frame)

    def load_view_settings():
        global view_settings
        view_settings = ViewFrameSettings(tab_view.tab("USTAWIENIA APLIKACJI"))

    load_account_view()
    load_buy_ticket_view()
    load_view_settings()

    last_tab = tab_view.get()

    def check_tab_change():
        nonlocal last_tab
        current_tab = tab_view.get()
        if current_tab != last_tab:
            last_tab = current_tab
            if current_tab == "KONTO":
                account_view_frame.reset_view_frame()
            elif current_tab == "KUP BILET":
                buy_ticket_frame.reset_view_frame()
            elif current_tab == "USTAWIENIA APLIKACJI":
                view_settings.reset_view_frame()
        root.after(100, check_tab_change)
    check_tab_change()


    root.mainloop()

if __name__ == "__main__":
    main()
