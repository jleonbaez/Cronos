import colorsys
import ctypes
import json
import math
import os
import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from datetime import datetime

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "countdown_config.json")

COMPACT_WIDTH_THRESHOLD = 180
COMPACT_HEIGHT_THRESHOLD = 95

FONT_SIZE_MIN = 10
FONT_SIZE_AUTO_MIN = 15
FONT_SIZE_PROBE = "999d 23:59:59"

UI_BG = "#101010"
UI_FIELD = "#1c1c1c"
UI_BORDER = "#2e2e2e"
UI_TEXT = "#e4e4e4"
UI_TEXT_DIM = "#8a8a8a"
UI_BTN = "#272727"
UI_BTN_HOVER = "#363636"
UI_ACCENT = "#4caf50"
UI_ACCENT_HOVER = "#5fc463"
UI_ACCENT_TEXT = "#0d1a0e"
UI_ACTIVE = "#2e5c32"
UI_ACTIVE_HOVER = "#376e3c"
UI_ERROR = "#ef6b6b"

WHEEL_SIZE = 200
WHEEL_BUCKETS = 12
BAR_HEIGHT = 26
RECENT_SLOTS = 8

FONT_CHOICES = [
    "Consolas", "Segoe UI", "Arial", "Courier New",
    "Verdana", "Comic Sans MS", "Times New Roman"
]

DEFAULTS = {
    "name": "Your Event",
    "bg_color": "#1e1e1e",
    "font_color": "#4caf50",
    "font_family": "Consolas",
    "font_size": 20,
    "recent_colors": [],
}


def parse_hex(value):
    if not isinstance(value, str):
        return None
    value = value.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if len(value) != 6:
        return None
    try:
        int(value, 16)
    except ValueError:
        return None
    return "#" + value.lower()


def hls_hex(hue, light, sat):
    r, g, b = colorsys.hls_to_rgb(hue % 1.0, min(1.0, max(0.0, light)), min(1.0, max(0.0, sat)))
    return "#%02x%02x%02x" % (int(r * 255 + 0.5), int(g * 255 + 0.5), int(b * 255 + 0.5))


def hex_to_hls(color):
    color = parse_hex(color) or "#4caf50"
    r = int(color[1:3], 16) / 255.0
    g = int(color[3:5], 16) / 255.0
    b = int(color[5:7], 16) / 255.0
    return colorsys.rgb_to_hls(r, g, b)


def mix(color_a, color_b, amount):
    a = parse_hex(color_a) or "#000000"
    b = parse_hex(color_b) or "#000000"
    channels = []
    for i in (1, 3, 5):
        ca = int(a[i:i + 2], 16)
        cb = int(b[i:i + 2], 16)
        channels.append(max(0, min(255, int(ca + (cb - ca) * amount))))
    return "#%02x%02x%02x" % tuple(channels)


def compute_fit_font_size(root, font_family, max_w, max_h, floor=FONT_SIZE_MIN, ceiling=500):
    floor = max(FONT_SIZE_MIN, int(floor))
    ceiling = max(floor, int(ceiling))
    lo, hi, best = floor, ceiling, floor
    while lo <= hi:
        mid = (lo + hi) // 2
        probe = tkfont.Font(root=root, family=font_family, size=mid, weight="bold")
        if probe.measure(FONT_SIZE_PROBE) <= max_w and probe.metrics("linespace") <= max_h:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def compute_max_font_size(root, font_family):
    return compute_fit_font_size(
        root, font_family,
        int(root.winfo_screenwidth() * 0.9),
        int(root.winfo_screenheight() * 0.55),
    )


def clamp_font_size(size, max_size):
    try:
        size = int(size)
    except (TypeError, ValueError, tk.TclError):
        size = DEFAULTS["font_size"]
    return max(FONT_SIZE_MIN, min(size, max_size))


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                if "target" in data:
                    data["target"] = datetime.fromisoformat(data["target"])
                for key, val in DEFAULTS.items():
                    data.setdefault(key, val)
                return data
        except Exception:
            pass
    return None


def save_config(name, target_dt, bg_color, font_color, font_family, font_size, recent_colors):
    with open(CONFIG_FILE, "w") as f:
        json.dump({
            "name": name,
            "target": target_dt.isoformat() if target_dt else None,
            "bg_color": bg_color,
            "font_color": font_color,
            "font_family": font_family,
            "font_size": font_size,
            "recent_colors": recent_colors,
        }, f)


def set_title_bar_color(root, hex_color):
    if sys.platform != "win32":
        return
    try:
        root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())

        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        DWMWA_CAPTION_COLOR = 35

        dark_value = ctypes.c_int(1)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(dark_value), ctypes.sizeof(dark_value)
        )

        hex_clean = hex_color.lstrip("#")
        r, g, b = (int(hex_clean[i:i + 2], 16) for i in (0, 2, 4))
        colorref = r | (g << 8) | (b << 16)
        color_value = ctypes.c_int(colorref)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_CAPTION_COLOR,
            ctypes.byref(color_value), ctypes.sizeof(color_value)
        )
    except Exception:
        pass


def configure_theme(root):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(
        "Cronos.TCombobox",
        fieldbackground=UI_FIELD, background=UI_FIELD, foreground=UI_TEXT,
        arrowcolor=UI_TEXT_DIM, bordercolor=UI_BORDER, lightcolor=UI_BORDER,
        darkcolor=UI_BORDER, insertcolor=UI_TEXT, relief="flat", padding=8,
    )
    style.map(
        "Cronos.TCombobox",
        fieldbackground=[("readonly", UI_FIELD), ("focus", UI_FIELD)],
        background=[("readonly", UI_FIELD), ("active", UI_FIELD)],
        foreground=[("readonly", UI_TEXT)],
        bordercolor=[("focus", UI_ACCENT), ("hover", UI_BTN_HOVER)],
        lightcolor=[("focus", UI_ACCENT)],
        darkcolor=[("focus", UI_ACCENT)],
        arrowcolor=[("active", UI_ACCENT)],
    )
    root.option_add("*TCombobox*Listbox.background", UI_FIELD)
    root.option_add("*TCombobox*Listbox.foreground", UI_TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", UI_ACCENT)
    root.option_add("*TCombobox*Listbox.selectForeground", UI_ACCENT_TEXT)
    root.option_add("*TCombobox*Listbox.borderWidth", 0)
    root.option_add("*TCombobox*Listbox.font", ("Segoe UI", 10))


def round_rect_points(x1, y1, x2, y2, r):
    return [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1,
    ]


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, bg=UI_BTN, hover=UI_BTN_HOVER, fg=UI_TEXT,
                 font=("Segoe UI", 10, "bold"), padx=16, pady=9, radius=11,
                 panel=UI_BG, repeat=False, size_for=None):
        self._font_spec = font
        self._font = tkfont.Font(root=parent, font=font)
        self._padx = padx
        self._pady = pady
        self._radius = radius
        self._min_width = self._font.measure(size_for) + padx * 2 if size_for else 0
        self._command = command
        self._repeat = repeat
        self._repeat_job = None

        width = max(self._min_width, self._font.measure(text) + padx * 2)
        height = self._font.metrics("linespace") + pady * 2

        super().__init__(parent, width=width, height=height, bg=panel,
                         highlightthickness=0, bd=0, cursor="hand2", takefocus=0)

        self._shape = self.create_polygon(
            round_rect_points(1, 1, width - 1, height - 1, radius),
            smooth=True, splinesteps=18, fill=bg, outline=""
        )
        self._label = self.create_text(width / 2, height / 2, text=text, fill=fg, font=font)
        self.set_colors(bg, hover, fg)

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def set_colors(self, bg, hover, fg):
        self._bg = bg
        self._hover = hover
        self._press = mix(bg, "#000000", 0.22)
        self.itemconfigure(self._shape, fill=bg)
        self.itemconfigure(self._label, fill=fg)

    def set_panel(self, color):
        self.configure(bg=color)

    def set_text(self, text):
        width = max(self._min_width, self._font.measure(text) + self._padx * 2)
        height = self._font.metrics("linespace") + self._pady * 2
        self.configure(width=width, height=height)
        self.coords(self._shape, *round_rect_points(1, 1, width - 1, height - 1, self._radius))
        self.coords(self._label, width / 2, height / 2)
        self.itemconfigure(self._label, text=text)

    def _on_enter(self, _):
        self.itemconfigure(self._shape, fill=self._hover)

    def _on_leave(self, _):
        self._cancel_repeat()
        self.itemconfigure(self._shape, fill=self._bg)

    def _on_press(self, _):
        self.itemconfigure(self._shape, fill=self._press)
        if self._repeat:
            self._fire()
            self._repeat_job = self.after(400, self._auto_repeat)

    def _on_release(self, event):
        was_repeating = self._repeat
        self._cancel_repeat()
        inside = 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height()
        if not was_repeating and inside:
            self._fire()
        try:
            self.itemconfigure(self._shape, fill=self._hover if inside else self._bg)
        except tk.TclError:
            pass

    def _auto_repeat(self):
        self._fire()
        self._repeat_job = self.after(45, self._auto_repeat)

    def _cancel_repeat(self):
        if self._repeat_job is not None:
            try:
                self.after_cancel(self._repeat_job)
            except tk.TclError:
                pass
            self._repeat_job = None

    def _fire(self):
        if self._command:
            self._command()


class ColorChip(tk.Canvas):
    def __init__(self, parent, color, width=56, height=30, radius=9,
                 panel=UI_BG, command=None, outline=UI_BORDER):
        super().__init__(parent, width=width, height=height, bg=panel,
                         highlightthickness=0, bd=0, takefocus=0)
        self._shape = self.create_polygon(
            round_rect_points(1, 1, width - 1, height - 1, radius),
            smooth=True, splinesteps=14, fill=color, outline=outline
        )
        if command:
            self.configure(cursor="hand2")
            self.bind("<Button-1>", lambda e: command())

    def set_color(self, color):
        self.itemconfigure(self._shape, fill=color)

    def set_panel(self, color):
        self.configure(bg=color)


def section_label(parent, text):
    return tk.Label(
        parent, text=text.upper(), bg=UI_BG, fg=UI_TEXT_DIM,
        font=("Segoe UI", 8, "bold"), anchor="w"
    )


def make_entry(parent, value="", width=None):
    wrap = tk.Frame(parent, bg=UI_BORDER, padx=1, pady=1)
    entry = tk.Entry(
        wrap, bg=UI_FIELD, fg=UI_TEXT, insertbackground=UI_ACCENT,
        relief="flat", bd=0, highlightthickness=0, font=("Segoe UI", 11),
        disabledbackground=UI_FIELD, selectbackground=UI_ACTIVE, selectforeground=UI_TEXT,
    )
    if width:
        entry.configure(width=width)
    entry.pack(fill="x", ipady=7, ipadx=8)
    entry.insert(0, value)
    entry.bind("<FocusIn>", lambda e: wrap.configure(bg=UI_ACCENT))
    entry.bind("<FocusOut>", lambda e: wrap.configure(bg=UI_BORDER))
    return wrap, entry


_WHEEL_BASE = {}
_WHEEL_IMAGES = {}


def wheel_base(size):
    cached = _WHEEL_BASE.get(size)
    if cached is not None:
        return cached
    radius = size / 2.0
    rows = []
    for y in range(size):
        dy = (y - radius + 0.5) / radius
        row = []
        for x in range(size):
            dx = (x - radius + 0.5) / radius
            dist = math.hypot(dx, dy)
            if dist > 1.0:
                row.append(None)
            else:
                hue = (math.atan2(dy, dx) / (2 * math.pi)) % 1.0
                r, g, b = colorsys.hls_to_rgb(hue, 0.5, min(1.0, dist))
                row.append((r * 255.0, g * 255.0, b * 255.0))
        rows.append(row)
    _WHEEL_BASE[size] = rows
    return rows


def wheel_image(master, size, light):
    bucket = min(WHEEL_BUCKETS, max(0, int(round(light * WHEEL_BUCKETS))))
    key = (size, bucket)
    cached = _WHEEL_IMAGES.get(key)
    if cached is not None:
        return cached

    level = bucket / float(WHEEL_BUCKETS)
    if level <= 0.5:
        scale = level * 2.0
        shift = 0.0
    else:
        scale = 2.0 - level * 2.0
        shift = (level * 2.0 - 1.0) * 255.0

    rows = wheel_base(size)
    image = tk.PhotoImage(master=master, width=size, height=size)
    fmt = "#%02x%02x%02x".__mod__
    for y in range(size):
        out = []
        for pixel in rows[y]:
            if pixel is None:
                out.append(UI_BG)
            else:
                out.append(fmt((
                    int(pixel[0] * scale + shift),
                    int(pixel[1] * scale + shift),
                    int(pixel[2] * scale + shift),
                )))
        image.put("{" + " ".join(out) + "}", to=(0, y))
    _WHEEL_IMAGES[key] = image
    return image


class ColorPicker:
    def __init__(self, parent, app, title, initial):
        self.app = app
        self.result = None
        self._wheel_job = None
        self._syncing = False

        hue, light, sat = hex_to_hls(initial)
        self.hue, self.light, self.sat = hue, light, sat

        width = 344
        height = 566
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.configure(bg=UI_BG)
        self.dialog.attributes("-topmost", True)
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)

        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        x = max(20, min(x, self.dialog.winfo_screenwidth() - width - 20))
        y = max(20, min(y, self.dialog.winfo_screenheight() - height - 70))
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        self.dialog.bind("<Escape>", lambda e: self.dialog.destroy())
        self.dialog.after(20, lambda: set_title_bar_color(self.dialog, UI_BG))

        body = tk.Frame(self.dialog, bg=UI_BG)
        body.pack(fill="both", expand=True, padx=22, pady=18)

        tk.Label(body, text=title, bg=UI_BG, fg=UI_TEXT,
                 font=("Segoe UI", 15, "bold"), anchor="w").pack(fill="x")
        tk.Label(body, text="Spin the wheel, then dial the light.", bg=UI_BG, fg=UI_TEXT_DIM,
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=(2, 14))

        footer = tk.Frame(body, bg=UI_BG)
        footer.pack(side="bottom", fill="x", pady=(14, 0))
        RoundedButton(footer, "Select", self._accept, bg=UI_ACCENT,
                      hover=UI_ACCENT_HOVER, fg=UI_ACCENT_TEXT).pack(side="right")
        RoundedButton(footer, "Cancel", self.dialog.destroy).pack(side="right", padx=(0, 8))

        self.wheel = tk.Canvas(body, width=WHEEL_SIZE, height=WHEEL_SIZE, bg=UI_BG,
                               highlightthickness=0, bd=0, cursor="crosshair")
        self.wheel.pack()
        self._wheel_img = wheel_image(self.dialog, WHEEL_SIZE, self.light)
        self._wheel_item = self.wheel.create_image(0, 0, anchor="nw", image=self._wheel_img)
        self._ring_dark = self.wheel.create_oval(0, 0, 0, 0, outline="#000000", width=3)
        self._ring = self.wheel.create_oval(0, 0, 0, 0, outline="#ffffff", width=2)
        self.wheel.bind("<Button-1>", self._on_wheel)
        self.wheel.bind("<B1-Motion>", self._on_wheel)

        bar_width = width - 44
        self.bar = tk.Canvas(body, width=bar_width, height=BAR_HEIGHT, bg=UI_BG,
                             highlightthickness=0, bd=0, cursor="sb_h_double_arrow")
        self.bar.pack(fill="x", pady=(14, 0))
        self._bar_width = bar_width
        self._bar_img = tk.PhotoImage(master=self.dialog, width=bar_width, height=BAR_HEIGHT)
        self._bar_item = self.bar.create_image(0, 0, anchor="nw", image=self._bar_img)
        self.bar.create_rectangle(0, 0, bar_width - 1, BAR_HEIGHT - 1, outline=UI_BORDER)
        self._bar_handle_dark = self.bar.create_rectangle(0, 0, 0, 0, outline="#000000", width=3)
        self._bar_handle = self.bar.create_rectangle(0, 0, 0, 0, outline="#ffffff", width=2)
        self.bar.bind("<Button-1>", self._on_bar)
        self.bar.bind("<B1-Motion>", self._on_bar)

        readout = tk.Frame(body, bg=UI_BG)
        readout.pack(fill="x", pady=(16, 0))
        self.preview = ColorChip(readout, hls_hex(hue, light, sat), width=64, height=38, radius=10)
        self.preview.pack(side="left")
        hex_wrap, self.hex_entry = make_entry(readout, "", width=9)
        self.hex_entry.configure(font=("Consolas", 11))
        hex_wrap.pack(side="left", padx=12)
        self.hex_entry.bind("<Return>", self._on_hex)
        self.hex_entry.bind("<FocusOut>", self._on_hex)

        section_label(body, "Recent").pack(fill="x", pady=(18, 6))
        recent_row = tk.Frame(body, bg=UI_BG)
        recent_row.pack(fill="x")
        self.recent_chips = []
        for index in range(RECENT_SLOTS):
            color = app.recent_colors[index] if index < len(app.recent_colors) else None
            chip = ColorChip(
                recent_row, color or UI_FIELD, width=30, height=30, radius=8,
                command=(lambda c=color: self._set_color(c)) if color else None
            )
            chip.pack(side="left", padx=(0, 6))
            self.recent_chips.append(chip)

        self._refresh()
        self.dialog.grab_set()

    def _hex(self):
        return hls_hex(self.hue, self.light, self.sat)

    def _set_color(self, color):
        hue, light, sat = hex_to_hls(color)
        self.hue, self.light, self.sat = hue, light, sat
        self._refresh()

    def _on_wheel(self, event):
        radius = WHEEL_SIZE / 2.0
        dx = (event.x - radius + 0.5) / radius
        dy = (event.y - radius + 0.5) / radius
        dist = math.hypot(dx, dy)
        if dist > 1.0:
            dx, dy, dist = dx / dist, dy / dist, 1.0
        self.hue = (math.atan2(dy, dx) / (2 * math.pi)) % 1.0
        self.sat = dist
        if self.light <= 0.02 or self.light >= 0.98:
            self.light = 0.5
        self._refresh()

    def _on_bar(self, event):
        position = min(self._bar_width - 1, max(0, event.x))
        self.light = 1.0 - position / float(self._bar_width - 1)
        self._refresh()

    def _on_hex(self, _):
        color = parse_hex(self.hex_entry.get())
        if color:
            self._set_color(color)
        else:
            self._sync_hex()

    def _sync_hex(self):
        self._syncing = True
        self.hex_entry.delete(0, "end")
        self.hex_entry.insert(0, self._hex().upper())
        self._syncing = False

    def _refresh(self):
        color = self._hex()
        self.preview.set_color(color)
        self._sync_hex()

        radius = WHEEL_SIZE / 2.0
        angle = self.hue * 2 * math.pi
        mx = radius + math.cos(angle) * self.sat * radius
        my = radius + math.sin(angle) * self.sat * radius
        for item in (self._ring_dark, self._ring):
            self.wheel.coords(item, mx - 7, my - 7, mx + 7, my + 7)

        self._render_bar()
        handle_x = (1.0 - self.light) * (self._bar_width - 1)
        handle_x = min(self._bar_width - 4, max(3, handle_x))
        for item in (self._bar_handle_dark, self._bar_handle):
            self.bar.coords(item, handle_x - 3, 2, handle_x + 3, BAR_HEIGHT - 3)

        self._schedule_wheel()

    def _render_bar(self):
        span = float(self._bar_width - 1)
        row = "{" + " ".join(
            hls_hex(self.hue, 1.0 - x / span, self.sat) for x in range(self._bar_width)
        ) + "}"
        image = tk.PhotoImage(master=self.dialog, width=self._bar_width, height=BAR_HEIGHT)
        image.put(" ".join([row] * BAR_HEIGHT), to=(0, 0))
        self._bar_img = image
        self.bar.itemconfigure(self._bar_item, image=image)

    def _schedule_wheel(self):
        if self._wheel_job is not None:
            try:
                self.dialog.after_cancel(self._wheel_job)
            except tk.TclError:
                pass
        self._wheel_job = self.dialog.after(90, self._redraw_wheel)

    def _redraw_wheel(self):
        self._wheel_job = None
        try:
            self._wheel_img = wheel_image(self.dialog, WHEEL_SIZE, self.light)
            self.wheel.itemconfigure(self._wheel_item, image=self._wheel_img)
        except tk.TclError:
            pass

    def _accept(self):
        self.result = self._hex()
        self.app.remember_color(self.result)
        self.dialog.destroy()


def ask_color(parent, app, title, initial):
    picker = ColorPicker(parent, app, title, initial)
    parent.wait_window(picker.dialog)
    return picker.result


class CountdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("")
        self.root.attributes("-topmost", True)
        if sys.platform == "win32":
            self.root.attributes("-toolwindow", True)
        self.root.minsize(80, 40)
        self.root.geometry("280x140+40+40")

        configure_theme(self.root)

        config = load_config() or {}
        self.event_name = tk.StringVar(value=config.get("name", DEFAULTS["name"]))
        self.target_dt = config.get("target")
        self.bg_color = config.get("bg_color", DEFAULTS["bg_color"])
        self.font_color = config.get("font_color", DEFAULTS["font_color"])
        self.font_family = config.get("font_family", DEFAULTS["font_family"])
        self.max_font_size = compute_max_font_size(self.root, self.font_family)
        self.font_size = clamp_font_size(
            config.get("font_size", DEFAULTS["font_size"]), self.max_font_size
        )

        raw_recent = config.get("recent_colors") or []
        self.recent_colors = []
        if isinstance(raw_recent, list):
            for value in raw_recent:
                color = parse_hex(value)
                if color and color not in self.recent_colors:
                    self.recent_colors.append(color)
        self.recent_colors = self.recent_colors[:RECENT_SLOTS]

        self.root.configure(bg=self.bg_color)

        self.name_label = tk.Label(
            root, textvariable=self.event_name, font=("Segoe UI", 13, "bold"),
            bg=self.bg_color, fg="#ffffff"
        )
        self.name_label.pack(pady=(12, 2))

        self.time_label = tk.Label(
            root, text="--:--:--:--",
            font=(self.font_family, self.font_size, "bold"),
            bg=self.bg_color, fg=self.font_color
        )
        self.time_label.pack(pady=(0, 8), expand=True, fill="both")

        self.controls_frame = tk.Frame(root, bg=self.bg_color)
        self.controls_frame.pack(pady=(0, 10))

        chip_style = {"padx": 9, "pady": 5, "radius": 9, "font": ("Segoe UI", 9, "bold"),
                      "panel": self.bg_color}

        self.edit_button = RoundedButton(
            self.controls_frame, "Set Event", self.open_edit_dialog, **chip_style
        )
        self.edit_button.pack(side="left", padx=3)

        self.appearance_button = RoundedButton(
            self.controls_frame, "Appearance", self.open_appearance_dialog, **chip_style
        )
        self.appearance_button.pack(side="left", padx=3)

        self._auto_sync = False
        self.sync_button = RoundedButton(
            self.controls_frame, "Auto Sync", self.toggle_auto_sync,
            size_for="Auto Sync ON", **chip_style
        )
        self.sync_button.pack(side="left", padx=3)

        self.root.after(50, lambda: set_title_bar_color(self.root, self.bg_color))

        self._is_compact = False
        self.root.bind("<Configure>", self.on_resize)

        if not self.target_dt:
            self.root.after(300, self.open_edit_dialog)

        self.update_countdown()

    def remember_color(self, color):
        color = parse_hex(color)
        if not color:
            return
        if color in self.recent_colors:
            self.recent_colors.remove(color)
        self.recent_colors.insert(0, color)
        del self.recent_colors[RECENT_SLOTS:]
        self._save()

    def on_resize(self, event):
        if event.widget != self.root:
            return
        w, h = self.root.winfo_width(), self.root.winfo_height()
        should_be_compact = w < COMPACT_WIDTH_THRESHOLD or h < COMPACT_HEIGHT_THRESHOLD

        if should_be_compact and not self._is_compact:
            self.name_label.pack_forget()
            self.controls_frame.pack_forget()
            self._is_compact = True
        elif not should_be_compact and self._is_compact:
            self.name_label.pack(pady=(12, 2), before=self.time_label)
            self.controls_frame.pack(pady=(0, 10))
            self._is_compact = False

        if self._auto_sync:
            self.sync_font_to_window()

    def toggle_auto_sync(self):
        self._auto_sync = not self._auto_sync
        if self._auto_sync:
            self.sync_button.set_text("Auto Sync ON")
            self.sync_button.set_colors(UI_ACTIVE, UI_ACTIVE_HOVER, UI_TEXT)
            self.sync_font_to_window()
        else:
            self.sync_button.set_text("Auto Sync")
            self.sync_button.set_colors(UI_BTN, UI_BTN_HOVER, UI_TEXT)
            self._save()

    def sync_font_to_window(self):
        w, h = self.root.winfo_width(), self.root.winfo_height()
        max_w = max(1, int(w * 0.92))
        max_h = max(1, int(h * (0.85 if self._is_compact else 0.5)))
        size = compute_fit_font_size(
            self.root, self.font_family, max_w, max_h,
            floor=FONT_SIZE_AUTO_MIN, ceiling=self.max_font_size,
        )
        if size != self.font_size:
            self.font_size = size
            self.time_label.configure(font=(self.font_family, self.font_size, "bold"))

    def _make_dialog(self, title, width, height):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.configure(bg=UI_BG)
        dialog.attributes("-topmost", True)
        dialog.resizable(False, False)
        dialog.transient(self.root)

        x = self.root.winfo_rootx() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - height) // 2
        x = max(20, min(x, dialog.winfo_screenwidth() - width - 20))
        y = max(20, min(y, dialog.winfo_screenheight() - height - 70))
        dialog.geometry(f"{width}x{height}+{x}+{y}")

        dialog.bind("<Escape>", lambda e: dialog.destroy())
        dialog.after(20, lambda: set_title_bar_color(dialog, UI_BG))
        return dialog

    def _dialog_body(self, dialog, title, subtitle):
        body = tk.Frame(dialog, bg=UI_BG)
        body.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(
            body, text=title, bg=UI_BG, fg=UI_TEXT,
            font=("Segoe UI", 16, "bold"), anchor="w"
        ).pack(fill="x")
        tk.Label(
            body, text=subtitle, bg=UI_BG, fg=UI_TEXT_DIM,
            font=("Segoe UI", 9), anchor="w"
        ).pack(fill="x", pady=(2, 18))
        return body

    def open_edit_dialog(self):
        dialog = self._make_dialog("Set Event", 400, 350)
        body = self._dialog_body(dialog, "Set Event", "What are you counting down to?")

        footer = tk.Frame(body, bg=UI_BG)
        footer.pack(side="bottom", fill="x", pady=(16, 0))

        section_label(body, "Event name").pack(fill="x", pady=(0, 5))
        name_wrap, name_entry = make_entry(body, self.event_name.get())
        name_wrap.pack(fill="x", pady=(0, 14))

        row = tk.Frame(body, bg=UI_BG)
        row.pack(fill="x")

        date_col = tk.Frame(row, bg=UI_BG)
        date_col.pack(side="left", fill="x", expand=True)
        section_label(date_col, "Date  \u00b7  DD-MM-YYYY").pack(fill="x", pady=(0, 5))
        date_wrap, date_entry = make_entry(
            date_col, self.target_dt.strftime("%d-%m-%Y") if self.target_dt else ""
        )
        date_wrap.pack(fill="x")

        time_col = tk.Frame(row, bg=UI_BG)
        time_col.pack(side="left", padx=(14, 0))
        section_label(time_col, "Time  \u00b7  24h").pack(fill="x", pady=(0, 5))
        time_wrap, time_entry = make_entry(
            time_col, self.target_dt.strftime("%H:%M") if self.target_dt else "09:00", width=7
        )
        time_wrap.pack()

        error = tk.Label(
            body, text="", bg=UI_BG, fg=UI_ERROR, font=("Segoe UI", 9),
            anchor="w", justify="left", wraplength=340
        )
        error.pack(fill="x", pady=(12, 0))

        def save_and_close():
            try:
                target = datetime.strptime(
                    f"{date_entry.get().strip()} {time_entry.get().strip()}",
                    "%d-%m-%Y %H:%M"
                )
            except ValueError:
                error.configure(text="Use DD-MM-YYYY for the date and HH:MM for the time.")
                return

            self.event_name.set(name_entry.get().strip() or "Your Event")
            self.target_dt = target
            self._save()
            dialog.destroy()

        RoundedButton(footer, "Save event", save_and_close, bg=UI_ACCENT,
                      hover=UI_ACCENT_HOVER, fg=UI_ACCENT_TEXT).pack(side="right")
        RoundedButton(footer, "Cancel", dialog.destroy).pack(side="right", padx=(0, 8))

        name_entry.focus_set()

    def open_appearance_dialog(self):
        dialog = self._make_dialog("Appearance", 420, 570)
        body = self._dialog_body(dialog, "Appearance", "Make the countdown yours.")

        chosen = {"fg": self.font_color, "bg": self.bg_color}
        font_var = tk.StringVar(value=self.font_family)
        size_var = tk.StringVar(value=str(self.font_size))

        footer = tk.Frame(body, bg=UI_BG)
        footer.pack(side="bottom", fill="x", pady=(16, 0))

        preview_border = tk.Frame(body, bg=UI_BORDER, padx=1, pady=1)
        preview_border.pack(fill="x", pady=(0, 18))
        preview = tk.Frame(preview_border, bg=chosen["bg"], height=96)
        preview.pack(fill="both")
        preview.pack_propagate(False)
        preview_label = tk.Label(preview, text="12d 04:32:18", bg=chosen["bg"], fg=chosen["fg"])
        preview_label.place(relx=0.5, rely=0.5, anchor="center")

        section_label(body, "Font").pack(fill="x", pady=(0, 5))
        font_menu = ttk.Combobox(
            body, textvariable=font_var, values=FONT_CHOICES, state="readonly",
            style="Cronos.TCombobox", font=("Segoe UI", 10), height=7
        )
        font_menu.pack(fill="x", pady=(0, 14))

        section_label(body, "Size").pack(fill="x", pady=(0, 5))
        size_row = tk.Frame(body, bg=UI_BG)
        size_row.pack(fill="x", pady=(0, 14))

        size_wrap, size_entry = make_entry(size_row, str(self.font_size), width=5)
        size_entry.configure(font=("Segoe UI", 11, "bold"), justify="center")
        size_entry.configure(textvariable=size_var)

        def current_size():
            try:
                return max(FONT_SIZE_MIN, min(int(size_var.get()), self.max_font_size))
            except ValueError:
                return self.font_size

        def bump(delta):
            size_var.set(str(max(FONT_SIZE_MIN, min(current_size() + delta, self.max_font_size))))

        RoundedButton(size_row, "\u2212", lambda: bump(-1), padx=13, pady=6, radius=10,
                      font=("Segoe UI", 12, "bold"), repeat=True).pack(side="left")
        size_wrap.pack(side="left", padx=8)
        RoundedButton(size_row, "+", lambda: bump(1), padx=13, pady=6, radius=10,
                      font=("Segoe UI", 12, "bold"), repeat=True).pack(side="left")
        tk.Label(
            size_row, text=f"{FONT_SIZE_MIN} \u2013 {self.max_font_size}",
            bg=UI_BG, fg=UI_TEXT_DIM, font=("Segoe UI", 9)
        ).pack(side="right")

        def color_row(label, key, title):
            section_label(body, label).pack(fill="x", pady=(0, 5))
            row = tk.Frame(body, bg=UI_BG)
            row.pack(fill="x", pady=(0, 14))

            def pick():
                color = ask_color(dialog, self, title, chosen[key])
                if color:
                    chosen[key] = color
                    refresh()

            chip = ColorChip(row, chosen[key], width=58, height=32, radius=9, command=pick)
            chip.pack(side="left")

            hex_label = tk.Label(
                row, text=chosen[key].upper(), bg=UI_BG, fg=UI_TEXT_DIM, font=("Consolas", 10)
            )
            hex_label.pack(side="left", padx=12)

            RoundedButton(row, "Change", pick, padx=13, pady=6, radius=10,
                          font=("Segoe UI", 9, "bold")).pack(side="right")
            return chip, hex_label

        def refresh():
            size = current_size()
            fitted = compute_fit_font_size(
                dialog, font_var.get(), 330, 62,
                floor=FONT_SIZE_MIN, ceiling=max(FONT_SIZE_MIN, size)
            )
            preview.configure(bg=chosen["bg"])
            preview_label.configure(
                bg=chosen["bg"], fg=chosen["fg"],
                font=(font_var.get(), fitted, "bold")
            )
            fg_chip.set_color(chosen["fg"])
            fg_hex.configure(text=chosen["fg"].upper())
            bg_chip.set_color(chosen["bg"])
            bg_hex.configure(text=chosen["bg"].upper())

        fg_chip, fg_hex = color_row("Digit color", "fg", "Digit color")
        bg_chip, bg_hex = color_row("Background color", "bg", "Background color")

        size_var.trace_add("write", lambda *_: refresh())
        font_menu.bind("<<ComboboxSelected>>", lambda e: refresh())
        refresh()

        def save_and_close():
            if self._auto_sync:
                self.toggle_auto_sync()
            self.font_family = font_var.get()
            self.max_font_size = compute_max_font_size(self.root, self.font_family)
            self.font_size = clamp_font_size(current_size(), self.max_font_size)
            self.font_color = chosen["fg"]
            self.bg_color = chosen["bg"]
            self.apply_appearance()
            self._save()
            dialog.destroy()

        RoundedButton(footer, "Apply", save_and_close, bg=UI_ACCENT,
                      hover=UI_ACCENT_HOVER, fg=UI_ACCENT_TEXT).pack(side="right")
        RoundedButton(footer, "Cancel", dialog.destroy).pack(side="right", padx=(0, 8))

    def apply_appearance(self):
        self.root.configure(bg=self.bg_color)
        self.name_label.configure(bg=self.bg_color)
        self.time_label.configure(bg=self.bg_color, fg=self.font_color, font=(self.font_family, self.font_size, "bold"))
        self.controls_frame.configure(bg=self.bg_color)
        for button in (self.edit_button, self.appearance_button, self.sync_button):
            button.set_panel(self.bg_color)
        set_title_bar_color(self.root, self.bg_color)

    def _save(self):
        save_config(
            self.event_name.get(), self.target_dt,
            self.bg_color, self.font_color, self.font_family, self.font_size,
            self.recent_colors
        )

    def update_countdown(self):
        if self.target_dt:
            remaining = self.target_dt - datetime.now()
            total_seconds = int(remaining.total_seconds())

            if total_seconds <= 0:
                self.time_label.config(text="TIME'S UP!")
            else:
                days, rem = divmod(total_seconds, 86400)
                hours, rem = divmod(rem, 3600)
                minutes, seconds = divmod(rem, 60)
                self.time_label.config(text=f"{days}d {hours:02}:{minutes:02}:{seconds:02}")
        else:
            self.time_label.config(text="No event set")

        self.root.after(1000, self.update_countdown)


if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownApp(root)
    root.mainloop()
