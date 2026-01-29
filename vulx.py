import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import os, sys, json, subprocess

# ================= OPTIONAL PIL =================
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except:
    PIL_AVAILABLE = False

# ================= PATHS =================
BASE = Path(__file__).parent
USERS_FILE = BASE / "users.txt"
CONFIG_FILE = BASE / "config.json"
STARTUP_SOUND = BASE / "startup_vulx.wav"
APPS_DIR = BASE / "apps"
GAMES_DIR = BASE / "games"

APPS_DIR.mkdir(exist_ok=True)
GAMES_DIR.mkdir(exist_ok=True)

# ================= CONFIG =================
DEFAULT_CONFIG = {
    "theme": "dark",
    "accent": "#f5c542",
    "wallpaper": None
}

def load_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except:
            pass
    CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, indent=4))
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=4))

CONFIG = load_config()

# ================= USERS =================
def load_users():
    users = {}
    if USERS_FILE.exists():
        for l in USERS_FILE.read_text().splitlines():
            if ":" in l:
                u, p = l.split(":", 1)
                users[u.strip()] = p.strip()
    return users

# ================= SOUND =================
def play_startup_sound():
    if not STARTUP_SOUND.exists():
        return
    try:
        if sys.platform.startswith("win"):
            import winsound
            winsound.PlaySound(
                str(STARTUP_SOUND),
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )
        elif sys.platform == "darwin":
            subprocess.Popen(["afplay", str(STARTUP_SOUND)])
        else:
            subprocess.Popen(["paplay", str(STARTUP_SOUND)])
    except:
        pass

# ================= SPLASH =================
def welcome_screen(root):
    s = tk.Toplevel(root)
    s.overrideredirect(True)
    s.configure(bg="black")

    w, h = 480, 260
    x = (s.winfo_screenwidth() - w) // 2
    y = (s.winfo_screenheight() - h) // 2
    s.geometry(f"{w}x{h}+{x}+{y}")

    tk.Label(
        s,
        text="VULX OS",
        fg=CONFIG["accent"],
        bg="black",
        font=("Segoe UI", 32, "bold")
    ).pack(expand=True)

    play_startup_sound()
    s.after(1500, s.destroy)

# ================= DRAG =================
def make_draggable(w):
    def start(e):
        w._dx, w._dy = e.x, e.y
    def drag(e):
        w.place(
            x=w.winfo_x() + e.x - w._dx,
            y=w.winfo_y() + e.y - w._dy
        )
    w.bind("<Button-1>", start)
    w.bind("<B1-Motion>", drag)

# ================= ABOUT =================
def open_about(parent):
    win = tk.Toplevel(parent)
    win.title("About Vulx OS")
    win.geometry("420x260")
    win.resizable(False, False)

    tk.Label(
        win,
        text="VULX OS",
        font=("Segoe UI", 20, "bold")
    ).pack(pady=10)

    tk.Label(
        win,
        text=(
            "Vulx OS 1.0\n\n"
            "A Python-based desktop shell\n"
            "Built with Tkinter\n\n"
            "Apps • Games • Customization\n\n"
            "Developer: CmdBar"
        ),
        justify="center"
    ).pack(pady=10)


# ================= FILE EXPLORER =================
def open_file_explorer(parent):
    win = tk.Toplevel(parent)
    win.title("File Explorer")
    win.geometry("900x600")

    history = []
    index = -1
    path_var = tk.StringVar()

    top = tk.Frame(win)
    top.pack(fill="x")

    def load(p):
        path_var.set(str(p))
        tree.delete(*tree.get_children())
        try:
            for i in sorted(p.iterdir()):
                tree.insert("", "end", iid=str(i), text=i.name)
        except:
            pass

    def go(p):
        nonlocal index
        p = Path(p)
        if not p.exists():
            return
        history[:] = history[:index + 1]
        history.append(p)
        index += 1
        load(p)

    def back():
        nonlocal index
        if index > 0:
            index -= 1
            load(history[index])

    def forward():
        nonlocal index
        if index < len(history) - 1:
            index += 1
            load(history[index])

    tk.Button(top, text="⟵", command=back).pack(side="left")
    tk.Button(top, text="⟶", command=forward).pack(side="left")
    tk.Entry(top, textvariable=path_var).pack(
        side="left", fill="x", expand=True
    )

    tree = ttk.Treeview(win)
    tree.pack(fill="both", expand=True)

    def open_item(_):
        sel = tree.focus()
        if not sel:
            return
        p = Path(sel)
        if p.is_dir():
            go(p)
        else:
            try:
                os.startfile(p)
            except:
                pass

    tree.bind("<Double-1>", open_item)

    if sys.platform.startswith("win"):
        for d in ["C:/", "D:/"]:
            if Path(d).exists():
                history.append(Path(d))
        index = 0
        load(history[0])
    else:
        go(Path.home())

# ================= SETTINGS =================
def open_settings(parent):
    win = tk.Toplevel(parent)
    win.title("Settings")
    win.geometry("420x360")

    def set_wallpaper():
        f = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )
        if f:
            CONFIG["wallpaper"] = f
            save_config(CONFIG)
            messagebox.showinfo(
                "Wallpaper",
                "Restart Vulx to apply"
            )

    tk.Label(
        win,
        text="Appearance",
        font=("Segoe UI", 14, "bold")
    ).pack(pady=10)

    tk.Button(
        win,
        text="Set Wallpaper",
        command=set_wallpaper
    ).pack(pady=10)

    tk.Label(win, text="Accent Color").pack(pady=10)
    for c in ["#f5c542", "#4aa3ff", "#ff5555", "#50fa7b", "#bd93f9"]:
        tk.Button(
            win,
            bg=c,
            width=12,
            command=lambda col=c: (
                CONFIG.update(accent=col),
                save_config(CONFIG)
            )
        ).pack(pady=3)

# ================= DESKTOP =================
def desktop_screen(username):
    desk = tk.Toplevel()
    desk.attributes("-fullscreen", True)

    bg = "#111"

    if CONFIG["wallpaper"] and PIL_AVAILABLE:
        try:
            img = Image.open(CONFIG["wallpaper"])
            img = img.resize(
                (desk.winfo_screenwidth(),
                 desk.winfo_screenheight()),
                Image.LANCZOS
            )
            photo = ImageTk.PhotoImage(img)
            c = tk.Canvas(desk, highlightthickness=0)
            c.pack(fill="both", expand=True)
            c.create_image(0, 0, image=photo, anchor="nw")
            c.image = photo
        except:
            desk.configure(bg=bg)
    else:
        desk.configure(bg=bg)

    icon = tk.Button(
        desk,
        text="About Vulx",
        width=14,
        height=2
    )
    icon.place(x=60, y=80)
    make_draggable(icon)
    icon.bind(
        "<Double-Button-1>",
        lambda e: open_about(desk)
    )

    bar = tk.Frame(desk, bg="#222", height=40)
    bar.pack(side="bottom", fill="x")

    start = tk.Frame(
        desk,
        bg="#1b1b1b",
        highlightbackground="#333",
        highlightthickness=1
    )

    def toggle():
        if start.winfo_ismapped():
            start.place_forget()
        else:
            start.place(
                x=10,
                y=desk.winfo_screenheight() - 360,
                width=260,
                height=340
            )

    tk.Button(bar, text="Start",
              command=toggle).pack(side="left", padx=10)

    start.bind("<Button-1>", lambda e: "break")

    tk.Label(
        start,
        text=f"👤 {username}",
        fg=CONFIG["accent"],
        bg="#1b1b1b",
        font=("Segoe UI", 12, "bold")
    ).pack(pady=10)

    def add(t, c):
        tk.Button(start, text=t,
                  width=25, command=c).pack(pady=5)

    add("📁 File Explorer", lambda: open_file_explorer(desk))
    add("⚙ Settings", lambda: open_settings(desk))
    add("🕹 Games Folder", lambda: os.startfile(GAMES_DIR))
    add("⏻ Shut Down Vulx", desk.destroy)

# ================= LOGIN =================
def login_screen(root):
    users = load_users()
    win = tk.Toplevel(root)
    win.title("Vulx Login")
    win.geometry("350x280")
    win.grab_set()

    tk.Label(
        win,
        text="VULX LOGIN",
        font=("Segoe UI", 18)
    ).pack(pady=20)

    u_entry = tk.Entry(win)
    p_entry = tk.Entry(win, show="*")
    u_entry.pack(pady=5)
    p_entry.pack(pady=5)

    def login():
        username = u_entry.get().strip()
        password = p_entry.get().strip()

        if username in users and users[username] == password:
            win.destroy()
            desktop_screen(username)
        else:
            messagebox.showerror(
                "Login Failed",
                "Invalid credentials"
            )

    tk.Button(
        win,
        text="Login",
        command=login
    ).pack(pady=20)

    win.bind("<Return>", lambda e: login())

# ================= MAIN =================
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    welcome_screen(root)
    root.after(1600, lambda: login_screen(root))

    root.mainloop()
