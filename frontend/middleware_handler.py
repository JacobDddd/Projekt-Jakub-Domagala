from yaml import load, Loader, dump, Dumper
import customtkinter as ctk

def change_window_size(yaml_data, root):
    try:
        if yaml_data["window_size"]["selected"] == "1200x850":
            root.geometry("1200x850")
        elif yaml_data["window_size"]["selected"] == "1000x700":
            root.geometry("1000x700")
        else:
            root.geometry("800x600")
    except Exception:
        generate_default_yaml_fixture()

def change_theme(yaml_data, root):
    try:
        if yaml_data["theme_mode"]["selected"] == "Jasny":
            ctk.set_appearance_mode("light")
        elif yaml_data["theme_mode"]["selected"] == "Ciemny":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("system")
    except Exception:
        generate_default_yaml_fixture()

def change_settings(yaml_data, root):
    try:
        change_window_size(yaml_data, root)
        change_theme(yaml_data, root)
    except Exception:
        generate_default_yaml_fixture()

def dump_settings(yaml_data):
    try:
        with open('settings.yaml', 'w') as file:
            dump(yaml_data, file, Dumper=Dumper)
    except Exception:
        raise Exception("Error while dumping settings.yaml")

def load_settings():
    try:
        return load(open("settings.yaml"), Loader=Loader)
    except Exception:
        generate_default_yaml_fixture()
        return load(open("settings.yaml"), Loader=Loader)

def update_yaml_data_settings(yaml_data, key, value):
    try:
        yaml_data[key]['selected'] = value
        dump_settings(yaml_data)
    except Exception:
        generate_default_yaml_fixture()

def generate_default_yaml_fixture():
    data = {
        "window_size": {
            "options": ["1200x850", "1000x700", "800x600"],
            "selected": "800x600"
        },
        "theme_mode": {
            "options": ["Jasny", "Ciemny", "Systemowy"],
            "selected": "Systemowy"
        }
    }
    dump_settings(data)

def load_and_apply_settings(root):
    yaml_data = load_settings()
    change_settings(yaml_data, root)
    return yaml_data