import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import shutil
import subprocess
import threading
import time
import webbrowser

# ---------- Paths ----------
SOURCE = Path(__file__).parent           # folder where vulxinstall.py is
TARGET = Path("C:/VUlX")                 # install folder
APPS_DIR = TARGET / "apps"

TARGET.mkdir(exist_ok=True)
APPS_DIR.mkdir(exist_ok=True)

# ---------- Copy everything ----------
def copy_core_files():
    for item in SOURCE.iterdir():
        # Skip installer itself and junk
        if item.name in ("vulxinstall.py", "__pycache__"):
            continue

        dest = TARGET / item.name

        try:
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
        except Exception as e:
            print(f"Failed to copy {item}: {e}")

# ---------- Apps to install ----------
APP_STORE = [
    {
        "name": "Vulxium Browser",
        "description": "Chromium-based browser for Vulx",
        "type": "url",
        "url": "https://www.google.com",
        "launcher": "vulxium.py"
    },
    {
        "name": "LibreOffice",
        "description": "Free Office Suite",
        "type": "url",
        "url": "https://www.libreoffice.org/download/",
        "launcher": "libreoffice.url"
    }
]

def install_apps():
    for app in APP_STORE:
        app_dir = APPS_DIR / app["name"].replace(" ", "_")
        app_dir.mkdir(exist_ok=True)
        launcher_path = app_dir / app["launcher"]

        if app["type"] == "url":
            if app["launcher"].endswith(".py"):
                launcher_path.write_text(
                    "import webbrowser\n"
                    f"webbrowser.open('{app['url']}')\n"
                )
            else:
                launcher_path.write_text(
                    "[InternetShortcut]\n"
                    f"URL={app['url']}\n"
                )

# ---------- Installer logic ----------
def install():
    username = user_entry.get().strip()
    password = pass_entry.get().strip()

    if not username or not password:
        messagebox.showerror("Error", "Username and password required")
        return

    threading.Thread(
        target=do_install,
        args=(username, password),
        daemon=True
    ).start()

def do_install(username, password):
    try:
        progress['value'] = 0
        status.config(text="Copying Vulx files...")
        root.update()

        copy_core_files()
        progress.step(40)
        root.update()

        status.config(text="Installing apps...")
        install_apps()
        progress.step(40)
        root.update()

        # Save user
        users_file = TARGET / "users.txt"
        users_file.parent.mkdir(exist_ok=True)
        with open(users_file, "a", encoding="utf-8") as f:
            f.write(f"{username}:{password}\n")

        progress['value'] = 100
        status.config(text="Installation complete")
        root.update()

        time.sleep(0.5)
        messagebox.showinfo(
            "Vulx Installer",
            "Vulx installed successfully!"
        )

        subprocess.Popen(
            f'start python "{TARGET / "vulx.py"}"',
            shell=True
        )
        root.destroy()

    except Exception as e:
        messagebox.showerror("Installer Error", str(e))

# ---------- GUI ----------
root = tk.Tk()
root.title("Vulx Installer")
root.geometry("520x420")
root.resizable(False, False)

tk.Label(
    root,
    text="VUlX Setup",
    font=("Segoe UI", 18, "bold")
).pack(pady=15)

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Username:", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w")
user_entry = tk.Entry(frame, font=("Segoe UI", 11))
user_entry.grid(row=0, column=1, padx=10)

tk.Label(frame, text="Password:", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="w")
pass_entry = tk.Entry(frame, font=("Segoe UI", 11), show="*")
pass_entry.grid(row=1, column=1, padx=10)

status = tk.Label(root, text="Ready to install", font=("Segoe UI", 11))
status.pack(pady=10)

progress = ttk.Progressbar(root, length=420)
progress.pack(pady=10)

tk.Button(
    root,
    text="Install & Launch",
    font=("Segoe UI", 12),
    command=install
).pack(pady=15)

root.mainloop()
