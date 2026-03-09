import tkinter as tk
import psutil
import time
import threading
import json
import os
from collections import deque

CONFIG_FILE = os.path.join(
    os.environ.get('APPDATA', os.path.expanduser('~')), 'Speedify', 'config.json'
)

# Near-black chroma key — becomes transparent.
# Using #000001 instead of pure black so Label widgets (#1e1e1e bg) are never
# accidentally treated as transparent.
CHROMA = "#000001"


def _load_config():
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_config(data):
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass


def format_speed(mbps, prefix):
    """Adaptive units: KB/s / Mbps / Gbps."""
    if mbps < 0.001:
        return f"{prefix} 0 KB/s"
    if mbps < 1.0:
        kbps = mbps * 1024
        return f"{prefix} {kbps:.0f} KB/s" if kbps >= 10 else f"{prefix} {kbps:.1f} KB/s"
    if mbps >= 1000:
        return f"{prefix} {mbps / 1000:.1f} Gbps"
    return f"{prefix} {mbps:.1f} Mbps"


class NetworkSpeedMonitor:
    W, H = 240, 32        # compact pill dimensions
    BG   = "#1e1e1e"      # pill fill  (must NOT equal CHROMA)
    SEP  = "#383838"      # separator line
    DL   = "#00D4AA"      # teal  – download
    UL   = "#FF6B6B"      # coral – upload
    DIM  = "#666666"      # close-button idle colour
    FONT = ("Segoe UI", 10, "bold")

    def __init__(self, root):
        self.root = root
        root.title("Speedify")
        root.overrideredirect(True)          # no title bar
        root.configure(bg=CHROMA)
        root.wm_attributes("-transparentcolor", CHROMA)   # pill shape
        root.wm_attributes("-topmost", True)
        root.lift()
        root.focus_force()

        # ── position ──────────────────────────────────────────────────────────
        cfg = _load_config()
        self._on_top = tk.BooleanVar(value=cfg.get('on_top', True))
        self._apply_on_top()

        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        cx, cy = cfg.get('x'), cfg.get('y')
        if (cx is not None and cy is not None
                and 0 <= cx <= sw - self.W and 0 <= cy <= sh - self.H):
            x, y = cx, cy
        else:
            x, y = (sw - self.W) // 2, (sh - self.H) // 2
        root.geometry(f"{self.W}x{self.H}+{x}+{y}")

        # ── canvas ────────────────────────────────────────────────────────────
        self.cv = tk.Canvas(root, bg=CHROMA, highlightthickness=0,
                            width=self.W, height=self.H)
        self.cv.pack(fill=tk.BOTH, expand=True)

        self._draw_pill()
        self._build_labels()
        self._build_close()
        self._build_menu()

        # ── drag state ────────────────────────────────────────────────────────
        # Anchor-offset method: on press store (mouse_abs - window_pos).
        # On move: new_pos = mouse_abs - stored_offset.
        # Works even if the B1-Motion event fires on multiple widgets because
        # recomputing the same expression always yields the same result.
        self._dragging = False
        self._off_x = self._off_y = 0

        # Bind to root → catches events propagated from every child widget.
        # Also bind directly to canvas + labels as a belt-and-suspenders guard,
        # because some Label clicks don't propagate on all Windows versions.
        self._attach_drag(root, self.cv, self.dl_lbl, self.ul_lbl)

        # ── network thread ────────────────────────────────────────────────────
        io = psutil.net_io_counters()
        self._prev  = (io.bytes_recv, io.bytes_sent, time.time())
        self._dl_h  = deque(maxlen=8)
        self._ul_h  = deque(maxlen=8)
        self._alive = True
        threading.Thread(target=self._monitor, daemon=True).start()

    # ── drawing ───────────────────────────────────────────────────────────────

    def _draw_pill(self):
        w, h, r = self.W, self.H, self.H // 2
        pts = [
            r, 0,   w-r, 0,   w, 0,
            w, r,   w, h-r,   w, h,
            w-r, h, r, h,     0, h,
            0, h-r, 0, r,     0, 0,
        ]
        self.cv.create_polygon(pts, smooth=True,
                               fill=self.BG, outline="#333333", width=1)
        mid = self.W // 2
        self.cv.create_line(mid, 7, mid, self.H - 7, fill=self.SEP, width=1)

    # ── widgets ───────────────────────────────────────────────────────────────

    def _build_labels(self):
        mid, cy = self.W // 2, self.H // 2
        self.dl_lbl = tk.Label(self.cv, text="↓ 0 Mbps",
                               font=self.FONT, bg=self.BG, fg=self.DL)
        self.dl_lbl.place(x=8, y=cy, anchor="w")

        self.ul_lbl = tk.Label(self.cv, text="↑ 0 Mbps",
                               font=self.FONT, bg=self.BG, fg=self.UL)
        self.ul_lbl.place(x=mid + 5, y=cy, anchor="w")

    def _build_close(self):
        self.x_lbl = tk.Label(self.cv, text="×", font=("Segoe UI", 11),
                              bg=self.BG, fg=self.DIM, cursor="hand2")
        self.x_lbl.place(x=self.W - 6, y=self.H // 2, anchor="e")
        self.x_lbl.bind("<Enter>",         lambda _: self.x_lbl.config(fg="#FF6B6B"))
        self.x_lbl.bind("<Leave>",         lambda _: self.x_lbl.config(fg=self.DIM))
        self.x_lbl.bind("<ButtonPress-1>", self._close_click)
        self.x_lbl.bind("<Button-3>",      self._show_menu)

    def _build_menu(self):
        m = tk.Menu(self.root, tearoff=0,
                    bg="#2a2a2a", fg="#FFFFFF",
                    activebackground="#444444", activeforeground="#FFFFFF",
                    font=("Segoe UI", 10), relief="flat")
        m.add_checkbutton(label="Always on Top",
                          variable=self._on_top, command=self._apply_on_top)
        m.add_separator()
        m.add_command(label="Reset Position", command=self._reset_pos)
        m.add_separator()
        m.add_command(label="Close", command=self.quit)
        self._menu = m

    # ── drag ──────────────────────────────────────────────────────────────────

    def _attach_drag(self, *widgets):
        for w in widgets:
            w.bind("<ButtonPress-1>",   self._drag_start)
            w.bind("<ButtonRelease-1>", self._drag_stop)
            w.bind("<B1-Motion>",       self._drag_move)
            w.bind("<Button-3>",        self._show_menu)

    def _drag_start(self, e):
        self._dragging = True
        self._off_x = e.x_root - self.root.winfo_x()
        self._off_y = e.y_root - self.root.winfo_y()

    def _drag_stop(self, e):
        self._dragging = False

    def _drag_move(self, e):
        if not self._dragging:
            return
        # Anchor-offset: no accumulation, idempotent when called multiple times
        self.root.geometry(f"+{e.x_root - self._off_x}+{e.y_root - self._off_y}")

    def _close_click(self, e):
        self._dragging = False           # cancel any live drag
        self.root.after(1, self.quit)    # quit after event chain finishes
        return "break"                   # stop propagation → no drag_start on root

    # ── interactions ──────────────────────────────────────────────────────────

    def _show_menu(self, e):
        try:
            self._menu.tk_popup(e.x_root, e.y_root)
        finally:
            self._menu.grab_release()

    def _apply_on_top(self):
        self.root.wm_attributes("-topmost", self._on_top.get())

    def _reset_pos(self):
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"+{(sw - self.W) // 2}+{(sh - self.H) // 2}")

    # ── network ───────────────────────────────────────────────────────────────

    def _monitor(self):
        while self._alive:
            try:
                pr, ps, pt = self._prev
                io = psutil.net_io_counters()
                cr, cs, ct = io.bytes_recv, io.bytes_sent, time.time()
                dt = ct - pt
                if dt > 0:
                    dl = max(0.0, (cr - pr) * 8 / (dt * 1e6))
                    ul = max(0.0, (cs - ps) * 8 / (dt * 1e6))
                    self._dl_h.append(dl)
                    self._ul_h.append(ul)
                    self.root.after(0, self._refresh,
                                    sum(self._dl_h) / len(self._dl_h),
                                    sum(self._ul_h) / len(self._ul_h))
                self._prev = cr, cs, ct
                time.sleep(1.0)
            except Exception:
                time.sleep(2.0)

    def _refresh(self, dl, ul):
        self.dl_lbl.config(text=format_speed(dl, "↓"), fg=self._tint(self.DL, dl))
        self.ul_lbl.config(text=format_speed(ul, "↑"), fg=self._tint(self.UL, ul))

    @staticmethod
    def _tint(col, mbps):
        r, g, b = (int(col[i:i + 2], 16) for i in (1, 3, 5))
        f = 1 + min(1.0, mbps / 100) * 0.5
        return f"#{min(255, int(r*f)):02x}{min(255, int(g*f)):02x}{min(255, int(b*f)):02x}"

    # ── exit ──────────────────────────────────────────────────────────────────

    def quit(self):
        self._alive = False
        _save_config({'x': self.root.winfo_x(), 'y': self.root.winfo_y(),
                      'on_top': self._on_top.get()})
        self.root.destroy()


def main():
    root = tk.Tk()
    NetworkSpeedMonitor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
