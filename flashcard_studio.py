#!/usr/bin/env python3
"""Flashcard Studio v1.9 — 3-column Setup, clean numbering."""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from reportlab.lib.pagesizes import A4, A5, LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont

try:
    from PIL import Image, ImageDraw, ImageTk, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

pdfmetrics.registerFont(TTFont("DejaVuSans",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))

PAGES = {"A4": A4, "A5": A5, "Letter": LETTER}

BG         = "#f4f6f8"
PANEL      = "#ffffff"
DIVIDER    = "#d8dee4"
TEXT       = "#1f2328"
MUTED      = "#8a9199"
GREEN      = "#2e7d32"
GREEN_D    = "#1b5e20"
GREEN_L    = "#e8f5e9"
GREEN_HOV  = "#c8e6c9"
BLUE       = "#1976d2"
BLUE_D     = "#0d47a1"
PREVIEW_BG = "#e4e7eb"
SLIDER_BG  = "#cfd8e3"
SHADOW     = "#d4d8dd"

DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

CLOSEUP_W = 260
CLOSEUP_H = 180

SLIDER_LEN = 110
STEP_SIZE  = 26


class RoundButton(tk.Canvas):
    _cache = {}

    def __init__(self, parent, text, command, size=STEP_SIZE,
                 fg=GREEN_D, fg_hover="white",
                 fill=GREEN_L, fill_hover=GREEN, bg=PANEL):
        super().__init__(parent, width=size, height=size, bg=bg,
                         highlightthickness=0, bd=0)
        self.command = command
        self.size = size
        self.text = text
        self.colors = {"normal": (fill, fg), "hover": (fill_hover, fg_hover)}
        self._state = "normal"
        self._photo = None
        self._render()
        self.bind("<Button-1>", lambda e: self.command())
        self.bind("<Enter>", lambda e: self._set_state("hover"))
        self.bind("<Leave>", lambda e: self._set_state("normal"))

    def _set_state(self, state):
        if self._state != state:
            self._state = state
            self._render()

    def _render(self):
        self.delete("all")
        fill, fg = self.colors[self._state]
        s = self.size
        if HAS_PIL:
            key = (s, fill, fg, self.text)
            if key not in RoundButton._cache:
                scale = 4
                big = s * scale
                img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
                d = ImageDraw.Draw(img)
                d.ellipse((2*scale, 2*scale, big - 2*scale, big - 2*scale),
                          fill=fill)
                try:
                    fnt = ImageFont.truetype(DEJAVU_BOLD, int(s * 0.55 * scale))
                except Exception:
                    fnt = ImageFont.load_default()
                d.text((big/2, big/2 + scale*0.5), self.text,
                       fill=fg, font=fnt, anchor="mm")
                img = img.resize((s, s), Image.LANCZOS)
                RoundButton._cache[key] = ImageTk.PhotoImage(img)
            self._photo = RoundButton._cache[key]
            self.create_image(0, 0, image=self._photo, anchor="nw")
        else:
            self.create_oval(2, 2, s-2, s-2, fill=fill, outline=fill)
            self.create_text(s/2, s/2, text=self.text, fill=fg,
                             font=("Sans", int(s*0.5), "bold"))


class TickCheck(tk.Frame):
    _cache = {}

    def __init__(self, parent, text, variable, command=None,
                 bg=PANEL, fg=TEXT, accent=GREEN):
        super().__init__(parent, bg=bg, cursor="hand2")
        self.var = variable
        self.command = command
        self.bg = bg
        self.fg = fg
        self.accent = accent
        self.size = 22
        self.canvas = tk.Canvas(self, width=self.size, height=self.size,
                                bg=bg, highlightthickness=0, bd=0)
        self.canvas.pack(side="left")
        self.label = tk.Label(self, text=text, bg=bg, fg=fg,
                              font=("Sans", 10, "bold"), cursor="hand2")
        self.label.pack(side="left", padx=(8, 0))
        for w in (self.canvas, self.label):
            w.bind("<Button-1>", self._toggle)
        self.var.trace_add("write", lambda *a: self._draw())
        self._photo = None
        self._draw()

    def _toggle(self, _event=None):
        self.var.set(not self.var.get())
        if self.command:
            self.command()

    def _draw(self):
        self.canvas.delete("all")
        s = self.size
        checked = bool(self.var.get())
        if HAS_PIL:
            key = (s, checked, self.accent)
            if key not in TickCheck._cache:
                scale = 4
                big = s * scale
                img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
                d = ImageDraw.Draw(img)
                pad = int(1.5 * scale)
                r = int(5 * scale)
                box = (pad, pad, big - pad, big - pad)
                if checked:
                    d.rounded_rectangle(box, radius=r, fill=self.accent)
                    pts = [(s*0.24*scale, s*0.53*scale),
                           (s*0.43*scale, s*0.72*scale),
                           (s*0.78*scale, s*0.32*scale)]
                    d.line(pts, fill="white", width=int(2.8*scale), joint="curve")
                else:
                    d.rounded_rectangle(box, radius=r, fill="white",
                                        outline="#c0c6cd", width=int(2*scale))
                img = img.resize((s, s), Image.LANCZOS)
                TickCheck._cache[key] = ImageTk.PhotoImage(img)
            self._photo = TickCheck._cache[key]
            self.canvas.create_image(0, 0, image=self._photo, anchor="nw")
        else:
            if checked:
                self.canvas.create_rectangle(2, 2, s-2, s-2,
                                             fill=self.accent, outline=self.accent)
                self.canvas.create_line(
                    s*0.24, s*0.53, s*0.43, s*0.72, s*0.78, s*0.32,
                    fill="white", width=3, capstyle="round", joinstyle="round")
            else:
                self.canvas.create_rectangle(2, 2, s-2, s-2,
                                             fill="white", outline="#c0c6cd", width=2)


class App:
    def __init__(self, root):
        self.root = root
        root.title("Flashcard Studio")
        root.geometry("1160x1080")
        root.minsize(1020, 820)
        self._setup_theme()
        self.headers, self.all_rows, self.cards = [], [], []
        self.selected = 0
        self.front_cells, self.back_cells = [], []
        self.pan_x, self.pan_y = 0, 0
        self._drag_start = None
        self._did_drag = False
        self._build()

    def _setup_theme(self):
        self.root.configure(bg=BG)
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", background=BG, foreground=TEXT, font=("Sans", 11))
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Sans", 11))
        style.configure("TLabelframe", background=PANEL, foreground=TEXT,
                        borderwidth=1, relief="solid")
        style.configure("TLabelframe.Label", background=PANEL, foreground=GREEN_D,
                        font=("Sans", 12, "bold"))
        style.configure("TButton", padding=(12, 6), font=("Sans", 11))

        style.configure("Browse.TButton", padding=(14, 8),
                        font=("Sans", 11, "bold"),
                        background=BLUE, foreground="white", borderwidth=0)
        style.map("Browse.TButton",
                  background=[("active", BLUE_D), ("pressed", BLUE_D)])

        style.configure("Accent.TButton", padding=(26, 11),
                        font=("Sans", 13, "bold"),
                        background=GREEN, foreground="white", borderwidth=0)
        style.map("Accent.TButton",
                  background=[("active", GREEN_D), ("pressed", GREEN_D)])

    def _build(self):
        # Bottom bar
        bottom = ttk.Frame(self.root)
        bottom.pack(side="bottom", fill="x", padx=14, pady=8)
        self.stats = tk.StringVar(value="No cards loaded")
        ttk.Label(bottom, textvariable=self.stats,
                  font=("Sans", 12, "bold")).pack(side="left", padx=8)
        ttk.Button(bottom, text="▶   Generate PDF", style="Accent.TButton",
                   command=self.generate).pack(side="right", padx=4)

        # 3. Selected card — close-up
        f3b = ttk.LabelFrame(self.root,
            text="  3.  Selected card — close-up  ")
        f3b.pack(side="bottom", fill="x", padx=14, pady=(4, 6))
        inner = tk.Frame(f3b, bg=PANEL)
        inner.pack(anchor="center", pady=8)

        self.detail_front = tk.Canvas(inner, bg=PANEL,
                                      width=CLOSEUP_W, height=CLOSEUP_H,
                                      highlightthickness=0)
        self.detail_front.pack(side="left")

        arrow_frame = tk.Frame(inner, bg=PANEL, width=70, height=CLOSEUP_H)
        arrow_frame.pack(side="left")
        arrow_frame.pack_propagate(False)
        tk.Label(arrow_frame, text="➜", bg=PANEL, fg=GREEN,
                 font=("Sans", 44, "bold")).pack(expand=True)

        self.detail_back = tk.Canvas(inner, bg=PANEL,
                                     width=CLOSEUP_W, height=CLOSEUP_H,
                                     highlightthickness=0)
        self.detail_back.pack(side="left")

        self.detail_front.bind("<Configure>", lambda e: self._draw_detail())
        self.detail_back.bind("<Configure>", lambda e: self._draw_detail())

        # ===== 1. Setup (3 balanced columns) =====
        f1 = ttk.LabelFrame(self.root, text="  1.  Setup  ")
        f1.pack(side="top", fill="x", padx=14, pady=4)

        body = tk.Frame(f1, bg=PANEL)
        body.pack(fill="x", padx=16, pady=10)

        # --- LEFT: Card content ---
        left = tk.Frame(body, bg=PANEL)
        left.grid(row=0, column=0, sticky="nw")

        tk.Label(left, text="CARD CONTENT", bg=PANEL, fg=GREEN_D,
                 font=("Sans", 9, "bold")).grid(row=0, column=0, columnspan=2,
                                                sticky="w", pady=(0, 4))
        tk.Label(left, text="Front side", bg=PANEL, fg=TEXT,
                 font=("Sans", 11, "bold")).grid(row=1, column=0,
                                                 padx=(0, 8), pady=1, sticky="w")
        self.front_var = tk.StringVar()
        self.front_cb = ttk.Combobox(left, textvariable=self.front_var,
                                     state="readonly", width=18,
                                     font=("Sans", 11))
        self.front_cb.grid(row=1, column=1, pady=1, sticky="w", ipady=1)

        tk.Label(left, text="Back side", bg=PANEL, fg=TEXT,
                 font=("Sans", 11, "bold")).grid(row=2, column=0,
                                                 padx=(0, 8), pady=1, sticky="w")
        self.back_var = tk.StringVar()
        self.back_cb = ttk.Combobox(left, textvariable=self.back_var,
                                    state="readonly", width=18,
                                    font=("Sans", 11))
        self.back_cb.grid(row=2, column=1, pady=1, sticky="w", ipady=1)

        tk.Label(left, text="Paper", bg=PANEL, fg=TEXT,
                 font=("Sans", 11, "bold")).grid(row=3, column=0,
                                                 padx=(0, 8), pady=1, sticky="w")
        paper = tk.Frame(left, bg=PANEL)
        paper.grid(row=3, column=1, pady=1, sticky="w")
        self.page_size = tk.StringVar(value="A4")
        cb = ttk.Combobox(paper, textvariable=self.page_size,
                          values=list(PAGES), state="readonly",
                          width=7, font=("Sans", 11))
        cb.pack(side="left", ipady=1)
        cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        self.orientation = tk.StringVar(value="portrait")
        cb2 = ttk.Combobox(paper, textvariable=self.orientation,
                           values=["portrait", "landscape"],
                           state="readonly", width=10, font=("Sans", 11))
        cb2.pack(side="left", padx=(6, 0), ipady=1)
        cb2.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        self.mirror = tk.BooleanVar(value=True)
        TickCheck(left, "Mirror backs (double-sided)",
                  self.mirror, command=self.refresh
                  ).grid(row=4, column=0, columnspan=2,
                         pady=(6, 0), sticky="w")

        self.front_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        self.back_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        # --- Divider 1 ---
        tk.Frame(body, bg=DIVIDER, width=1).grid(row=0, column=1,
                                                  sticky="ns", padx=24)

        # --- MIDDLE: Grid layout ---
        mid = tk.Frame(body, bg=PANEL)
        mid.grid(row=0, column=2, sticky="nw")

        tk.Label(mid, text="GRID LAYOUT", bg=PANEL, fg=GREEN_D,
                 font=("Sans", 9, "bold")).grid(row=0, column=0, columnspan=3,
                                                sticky="w", pady=(0, 4))

        self.cards_per_row = tk.IntVar(value=5)
        self.cards_per_col = tk.IntVar(value=7)
        self.front_size   = tk.DoubleVar(value=36)
        self.back_size    = tk.DoubleVar(value=16)

        self._compact_row(mid, 1, "Cards per row",        self.cards_per_row, 1, 10, True)
        self._compact_row(mid, 2, "Cards per column",     self.cards_per_col, 1, 10, True)
        self._compact_row(mid, 3, "Front font size (pt)", self.front_size, 8, 80, False)
        self._compact_row(mid, 4, "Back font size (pt)",  self.back_size, 6, 40, False)

        # --- Divider 2 ---
        tk.Frame(body, bg=DIVIDER, width=1).grid(row=0, column=3,
                                                  sticky="ns", padx=24)

        # --- RIGHT: File / Browse ---
        right = tk.Frame(body, bg=PANEL)
        right.grid(row=0, column=4, sticky="nw")

        tk.Label(right, text="DATA FILE", bg=PANEL, fg=GREEN_D,
                 font=("Sans", 9, "bold")).grid(row=0, column=0, sticky="w",
                                                pady=(0, 4))

        ttk.Button(right, text="📂   Browse…", style="Browse.TButton",
                   command=self.load_file).grid(row=1, column=0,
                                                sticky="w", pady=(2, 6))

        self.file_var = tk.StringVar(value="No file loaded")
        tk.Label(right, textvariable=self.file_var, bg=PANEL, fg=MUTED,
                 font=("Sans", 10, "italic"), wraplength=170,
                 justify="left").grid(row=2, column=0, sticky="w")

        # ===== 2. Preview =====
        f2 = ttk.LabelFrame(self.root,
            text="  2.  Preview — scroll to zoom · click a card · drag to pan  ")
        f2.pack(side="top", fill="both", expand=True, padx=14, pady=4)
        f2.columnconfigure(0, weight=1)
        f2.rowconfigure(0, weight=1)
        self.preview = tk.Canvas(f2, bg=PREVIEW_BG, highlightthickness=0,
                                 height=200, cursor="fleur")
        self.preview.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=8)
        self.preview.bind("<Configure>", lambda e: self._draw_preview())
        self.preview.bind("<Button-4>", lambda e: self._on_scroll(+1))
        self.preview.bind("<Button-5>", lambda e: self._on_scroll(-1))
        self.preview.bind("<MouseWheel>",
                          lambda e: self._on_scroll(1 if e.delta > 0 else -1))
        self.preview.bind("<ButtonPress-1>", self._on_press)
        self.preview.bind("<B1-Motion>",     self._on_drag)
        self.preview.bind("<ButtonRelease-1>", self._on_release)

        zf = tk.Frame(f2, bg=PANEL)
        zf.grid(row=0, column=1, sticky="n", padx=12, pady=8)
        tk.Label(zf, text="Zoom", bg=PANEL, fg=TEXT,
                 font=("Sans", 10, "bold")).pack(pady=(0, 4))
        self.zoom = tk.DoubleVar(value=1.0)
        tk.Scale(zf, from_=1.0, to=5.0, resolution=0.1, orient="vertical",
                 variable=self.zoom, showvalue=False,
                 sliderlength=18, troughcolor=SLIDER_BG,
                 bg=BLUE, activebackground=BLUE_D,
                 highlightthickness=0, bd=0, width=16, length=160,
                 command=lambda v: self._draw_preview()).pack()
        self.zoom_lbl = tk.Label(zf, text="100%", bg=PANEL, fg=TEXT,
                                  width=6, anchor="center",
                                  font=("Sans", 10, "bold"))
        self.zoom_lbl.pack(pady=6)
        tk.Button(zf, text="Reset view",
                  command=self._reset_view,
                  bg="#f0f2f4", fg=TEXT, activebackground="#e1e5ea",
                  bd=1, relief="solid", padx=8, pady=4,
                  font=("Sans", 10, "bold"), cursor="hand2",
                  highlightthickness=0).pack(fill="x")
        self.zoom.trace_add("write", lambda *a: self._update_zoom_label())

    # --- compact row ---
    def _compact_row(self, parent, row, label, var, lo, hi, is_int, inc=1):
        tk.Label(parent, text=label, bg=PANEL, fg=TEXT,
                 font=("Sans", 11, "bold")
                 ).grid(row=row, column=0, padx=(0, 8), pady=1, sticky="w")

        tk.Scale(parent, from_=lo, to=hi, resolution=inc, orient="horizontal",
                 variable=var, showvalue=False, sliderlength=14,
                 troughcolor=SLIDER_BG, bg=BLUE, activebackground=BLUE_D,
                 highlightthickness=0, bd=0, width=12, length=SLIDER_LEN
                 ).grid(row=row, column=1, padx=(0, 8), pady=1)

        ctl = tk.Frame(parent, bg=PANEL)
        ctl.grid(row=row, column=2, pady=1, sticky="w")

        def bump(d):
            try:
                v = var.get() + d
            except tk.TclError:
                v = lo
            v = max(lo, min(hi, v))
            if is_int:
                var.set(int(round(v)))
            else:
                var.set(round(v, 1))

        RoundButton(ctl, "−", lambda: bump(-inc), size=STEP_SIZE).pack(side="left")
        ttk.Entry(ctl, textvariable=var, width=4, justify="center",
                  font=("Sans", 11, "bold")).pack(side="left", padx=4, ipady=0)
        RoundButton(ctl, "+", lambda: bump(+inc), size=STEP_SIZE).pack(side="left")

        var.trace_add("write", lambda *a: self.refresh())

    # --- zoom / pan ---
    def _on_scroll(self, direction):
        v = round(min(5.0, max(1.0, self.zoom.get() + direction * 0.1)), 1)
        self.zoom.set(v)

    def _reset_view(self):
        self.zoom.set(1.0)
        self.pan_x, self.pan_y = 0, 0
        self._draw_preview()

    def _update_zoom_label(self):
        self.zoom_lbl.config(text=f"{int(round(self.zoom.get() * 100))}%")

    def _on_press(self, event):
        self._drag_start = (event.x, event.y, self.pan_x, self.pan_y)
        self._did_drag = False

    def _on_drag(self, event):
        if not self._drag_start: return
        x0, y0, px0, py0 = self._drag_start
        dx, dy = event.x - x0, event.y - y0
        if abs(dx) > 3 or abs(dy) > 3:
            self._did_drag = True
        self.pan_x = px0 + dx
        self.pan_y = py0 + dy
        self._draw_preview()

    def _on_release(self, event):
        if not self._did_drag:
            self._on_click(event)
        self._drag_start = None
        self._did_drag = False

    # --- data ---
    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[
            ("All supported", "*.xlsx *.csv *.txt"),
            ("Excel", "*.xlsx"), ("CSV", "*.csv"), ("Text", "*.txt")])
        if not path: return
        try:
            self.headers, self.all_rows = self._read(path)
        except Exception as e:
            messagebox.showerror("Read error", str(e)); return
        self.file_var.set(os.path.basename(path))
        self.front_cb["values"] = self.headers
        self.back_cb["values"] = self.headers
        if self.headers:
            self.front_cb.current(0)
            self.back_cb.current(min(1, len(self.headers) - 1))
        self.selected = 0
        self.pan_x, self.pan_y = 0, 0
        self.refresh()

    def _read(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext == ".xlsx":
            import openpyxl
            wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
            data = [list(r) for r in wb.active.iter_rows(values_only=True)]
        elif ext == ".csv":
            import csv
            with open(path, encoding="utf-8") as f:
                data = list(csv.reader(f))
        else:
            with open(path, encoding="utf-8") as f:
                lines = [l.rstrip("\n") for l in f
                         if l.strip() and not l.startswith("#")]
            data = [l.split("\t") for l in lines]
        if not data: return [], []
        if ext == ".txt":
            headers = [f"Column {i+1}" for i in range(len(data[0]))]
            rows = data
        else:
            headers = [str(c) if c is not None and str(c).strip() else f"Column {i+1}"
                       for i, c in enumerate(data[0])]
            rows = data[1:]
        return headers, rows

    def _cards(self):
        if not self.all_rows: return []
        try:
            fi = self.headers.index(self.front_var.get())
            bi = self.headers.index(self.back_var.get())
        except ValueError:
            return []
        out = []
        for r in self.all_rows:
            if len(r) <= max(fi, bi): continue
            f = "" if r[fi] is None else str(r[fi]).strip()
            b = "" if r[bi] is None else str(r[bi]).strip()
            if f and b and f != "None" and b != "None":
                out.append((f, b))
        return out

    def refresh(self):
        try:
            self.cards = self._cards()
            if self.selected >= len(self.cards):
                self.selected = 0
            self.stats.set(f"{len(self.cards)} cards  ·  selected #{self.selected + 1}"
                           if self.cards else "No cards loaded")
        except Exception:
            pass
        self._draw_preview()
        self._draw_detail()

    # --- geometry ---
    def _params(self):
        pw, ph = PAGES[self.page_size.get()]
        if self.orientation.get() == "landscape":
            pw, ph = ph, pw
        cols = max(1, int(self.cards_per_row.get()))
        rows = max(1, int(self.cards_per_col.get()))
        cw = pw / cols
        ch = ph / rows
        return pw, ph, cw, ch, cols, rows

    # --- preview ---
    def _draw_preview(self):
        self.preview.delete("all")
        self.front_cells, self.back_cells = [], []
        W = self.preview.winfo_width(); H = self.preview.winfo_height()
        if W < 20 or H < 20: return
        try:
            pw, ph, cw, ch, cols, rows = self._params()
            fs = self.front_size.get(); bs = self.back_size.get()
            zoom = self.zoom.get()
        except tk.TclError:
            return

        pad = 20; gap_between = 26; label_h = 18
        base = (W - 2*pad - gap_between) / (2*pw)
        scale = base * zoom
        if scale <= 0: return

        page_w = pw * scale; page_h = ph * scale
        total_w = 2 * page_w + gap_between
        left_x  = (W - total_w) / 2 + self.pan_x
        right_x = left_x + page_w + gap_between
        top_y = label_h + 12 + self.pan_y

        self.preview.create_rectangle(left_x+3, top_y+3,
                                      left_x + page_w+3, top_y + page_h+3,
                                      outline="", fill=SHADOW)
        self.preview.create_rectangle(right_x+3, top_y+3,
                                      right_x + page_w+3, top_y + page_h+3,
                                      outline="", fill=SHADOW)
        self.preview.create_rectangle(left_x, top_y, left_x + page_w, top_y + page_h,
                                      outline=DIVIDER, fill="white", width=1)
        self.preview.create_rectangle(right_x, top_y, right_x + page_w, top_y + page_h,
                                      outline=DIVIDER, fill="white", width=1)
        self.preview.create_text(left_x + page_w/2, top_y - 6,
                                 text=f"FRONT   ({cols}×{rows} = {cols*rows} cards)",
                                 anchor="s", font=("Sans", 10, "bold"), fill=GREEN_D)
        self.preview.create_text(right_x + page_w/2, top_y - 6,
                                 text=f"BACK   ({cols}×{rows} = {cols*rows} cards)",
                                 anchor="s", font=("Sans", 10, "bold"), fill=GREEN_D)

        def build_cells(px, is_back):
            cells = []
            for i in range(cols * rows):
                col = i % cols; row = i // cols
                if is_back and self.mirror.get():
                    col = cols - 1 - col
                x0 = px + col * cw * scale
                y0 = top_y + row * ch * scale
                x1 = x0 + cw * scale; y1 = y0 + ch * scale
                cells.append((i, x0, y0, x1, y1))
                self.preview.create_rectangle(x0, y0, x1, y1,
                                              outline="#eef1f4")
            return cells

        self.front_cells = build_cells(left_x, False)
        self.back_cells = build_cells(right_x, True)

        def draw_text(cells, key, size_pt):
            for i, x0, y0, x1, y1 in cells:
                if i < len(self.cards):
                    txt = self.cards[i][key]
                    px = max(3, min(size_pt * scale, (y1-y0) * 0.9))
                    try:
                        self.preview.create_text((x0+x1)/2, (y0+y1)/2,
                            text=txt, font=("DejaVu Sans", -int(px)))
                    except Exception:
                        pass

        draw_text(self.front_cells, 0, fs)
        draw_text(self.back_cells, 1, bs)

        if self.cards and 0 <= self.selected < len(self.cards):
            for i, x0, y0, x1, y1 in self.front_cells:
                if i == self.selected:
                    self.preview.create_rectangle(x0, y0, x1, y1,
                        outline="#d32f2f", width=3); break
            for i, x0, y0, x1, y1 in self.back_cells:
                if i == self.selected:
                    self.preview.create_rectangle(x0, y0, x1, y1,
                        outline="#1976d2", width=3); break

    def _on_click(self, event):
        x, y = event.x, event.y
        for lst in (self.front_cells, self.back_cells):
            for i, x0, y0, x1, y1 in lst:
                if x0 <= x <= x1 and y0 <= y <= y1:
                    if i < len(self.cards):
                        self.selected = i
                        self.stats.set(f"{len(self.cards)} cards  ·  selected #{i+1}")
                        self._draw_preview()
                        self._draw_detail()
                    return

    # --- detail ---
    def _draw_detail(self):
        for cv in (self.detail_front, self.detail_back):
            cv.delete("all")

        if not self.cards or not (0 <= self.selected < len(self.cards)):
            for cv in (self.detail_front, self.detail_back):
                W = cv.winfo_width() or CLOSEUP_W
                H = cv.winfo_height() or CLOSEUP_H
                pad = 8
                x0, y0, x1, y1 = pad, pad, W - pad, H - pad
                cv.create_rectangle(x0, y0, x1, y1,
                                    outline="#d0d6dc", width=2,
                                    dash=(6, 4), fill="#fbfcfd")
                cv.create_text((x0+x1)/2, (y0+y1)/2,
                               text="No card selected",
                               fill="#b6bdc4",
                               font=("Sans", 11, "italic"))
            return

        front, back = self.cards[self.selected]
        try:
            pw, ph, cw, ch, cols, rows = self._params()
            fs = self.front_size.get(); bs = self.back_size.get()
        except tk.TclError:
            return
        cw_mm = cw / mm; ch_mm = ch / mm
        if cw_mm <= 0 or ch_mm <= 0: return
        aspect = cw_mm / ch_mm

        def render(cv, text, size_pt, color):
            W = cv.winfo_width(); H = cv.winfo_height()
            if W < 20 or H < 20: return
            pad = 10
            avail_w = W - 2*pad; avail_h = H - 2*pad
            if avail_w / avail_h > aspect:
                card_h = avail_h; card_w = card_h * aspect
            else:
                card_w = avail_w; card_h = card_w / aspect
            x0 = (W - card_w)/2; y0 = (H - card_h)/2
            x1 = x0 + card_w;    y1 = y0 + card_h
            cv.create_rectangle(x0+2, y0+2, x1+2, y1+2,
                                outline="", fill="#e6e9ec")
            cv.create_rectangle(x0, y0, x1, y1,
                                outline=color, width=3, fill="white")
            px_per_mm = card_w / cw_mm
            px_size = size_pt * 0.3528 * px_per_mm
            px_size = max(6, min(px_size, card_h * 0.9))
            cv.create_text((x0+x1)/2, (y0+y1)/2, text=text,
                           font=("DejaVu Sans", -int(px_size)))

        render(self.detail_front, front, fs, "#d32f2f")
        render(self.detail_back, back, bs, "#1976d2")

    # --- generate ---
    def generate(self):
        if not self.cards:
            messagebox.showwarning("Nothing to export",
                                   "Load a file and pick columns first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")], initialfile="flashcards.pdf")
        if not path: return
        try:
            self._write_pdf(path)
        except Exception as e:
            messagebox.showerror("PDF error", str(e)); return
        messagebox.showinfo("Done", f"PDF written to:\n{path}")

    def _write_pdf(self, path):
        pw, ph, cw, ch, cols, rows = self._params()
        per = cols * rows
        c = canvas.Canvas(path, pagesize=(pw, ph))
        fs = self.front_size.get(); bs = self.back_size.get()

        def draw(items, is_back):
            for i, (f, b) in enumerate(items):
                col, row = i % cols, i // cols
                if is_back and self.mirror.get():
                    col = cols - 1 - col
                x = col * cw
                y = ph - (row + 1) * ch
                c.setLineWidth(0.4)
                c.rect(x, y, cw, ch)
                cx, cy = x + cw/2, y + ch/2
                if is_back:
                    c.setFont("DejaVuSans", bs)
                    c.drawCentredString(cx, cy - bs/3, b)
                else:
                    c.setFont("STSong-Light", fs)
                    c.drawCentredString(cx, cy - fs/3, f)
            c.showPage()

        for i in range(0, len(self.cards), per):
            chunk = self.cards[i:i+per]
            draw(chunk, False)
            draw(chunk, True)
        c.save()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
