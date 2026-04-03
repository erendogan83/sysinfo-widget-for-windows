"""
SysInfo Widget
--------------
A lightweight Windows desktop widget that displays network and system
information in a compact, always-accessible overlay.

Author : Eren DOĞAN  <https://github.com/erendogan83>
License: MIT
"""

import os
import re
import socket
import subprocess
import tkinter as tk
import uuid

from config import COLORS, LINKS, SETTINGS


# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------

def make_link(parent: tk.Frame, text: str, command=None, fg: str = None) -> tk.Label:
    """Return a clickable label styled as a hyperlink."""
    fg = fg or COLORS["link"]
    lbl = tk.Label(
        parent, text=text,
        fg=fg, bg=COLORS["menu_bg"],
        font=(SETTINGS["font"], 9),
        cursor="hand2", anchor="w",
    )
    lbl.bind("<Enter>", lambda e: lbl.config(fg=COLORS["accent"], bg=COLORS["hover"]))
    lbl.bind("<Leave>", lambda e: lbl.config(fg=fg, bg=COLORS["menu_bg"]))
    if command:
        lbl.bind("<Button-1>", lambda e: command())
    return lbl


# ---------------------------------------------------------------------------
#  Widget
# ---------------------------------------------------------------------------

class SysInfoWidget:
    """
    Borderless desktop overlay widget.

    Features
    --------
    - Shows IP address, MAC address, username and domain status
    - Collapsible quick-links panel (configurable via config.py)
    - Draggable header
    - Arrow button with pulse animation to hint interactivity
    - Hidden developer credit tooltip on the ⓘ icon (hover 5 s)
    - Auto-collapse after configurable idle timeout
    """

    W = SETTINGS["width"]

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", False)  # sinks behind other windows on click

        self.is_open      = False
        self.links_open   = False
        self.timer        = None
        self._drag_x      = 0
        self._drag_y      = 0
        self._tooltip_job = None
        self._tooltip_win = None
        self._arrow_job   = None
        self._arrow_phase = 0

        self._build_ui()
        self.root.update_idletasks()
        self._position_window()
        self.collapse()
        self.root.deiconify()
        self.root.lift()
        self._animate_arrow()

    # ------------------------------------------------------------------
    #  UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        C = COLORS

        self.frame = tk.Frame(
            self.root, bg=C["bg"],
            highlightbackground=C["border"], highlightthickness=1,
        )
        self.frame.pack(fill="both", expand=True)

        # ── Header ────────────────────────────────────────────────
        self.header = tk.Frame(self.frame, bg=C["header"], height=36)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        tk.Frame(self.header, bg="#FFFFFF", width=3).pack(side="left", fill="y")

        tk.Label(
            self.header, text=f"  {SETTINGS['title']}",
            fg="#FFFFFF", bg=C["header"],
            font=(SETTINGS["font"], 9, "bold"),
        ).pack(side="left")

        self.arrow_btn = tk.Label(
            self.header, text="▼",
            fg="#FFFFFF", bg=C["header"],
            font=(SETTINGS["font"], 11, "bold"),
            cursor="hand2", width=3,
        )
        self.arrow_btn.pack(side="right", padx=6)
        self.arrow_btn.bind("<Button-1>", self.toggle)
        self.arrow_btn.bind("<Enter>", lambda e: (
            self.arrow_btn.config(bg=C["header_hover"]),
            self._stop_arrow_anim(),
        ))
        self.arrow_btn.bind("<Leave>", lambda e: (
            self.arrow_btn.config(bg=C["header"]),
            self._animate_arrow() if not self.is_open else None,
        ))

        self.header.bind("<ButtonPress-1>", self._drag_start)
        self.header.bind("<B1-Motion>",     self._drag_move)

        # ── Info panel ────────────────────────────────────────────
        self.content = tk.Frame(self.frame, bg=C["content_bg"])

        def _info_lbl():
            return tk.Label(
                self.content, fg=C["text"], bg=C["content_bg"],
                font=(SETTINGS["font"], 9), anchor="w",
            )

        self.lbl_ip     = _info_lbl()
        self.lbl_mac    = _info_lbl()
        self.lbl_user   = _info_lbl()
        self.lbl_domain = tk.Label(
            self.content, fg=C["text"], bg=C["content_bg"],
            font=(SETTINGS["font"], 9, "bold"), anchor="w",
        )

        self.lbl_ip.pack(    fill="x", padx=12, pady=(10, 2))
        self.lbl_mac.pack(   fill="x", padx=12, pady=2)
        self.lbl_user.pack(  fill="x", padx=12, pady=2)
        self.lbl_domain.pack(fill="x", padx=12, pady=(2, 8))

        tk.Frame(self.content, bg=C["border"],     height=1).pack(fill="x")
        tk.Frame(self.content, bg=C["content_bg"], height=1).pack(fill="x")

        # ── Quick Links toggle row ─────────────────────────────────
        row = tk.Frame(self.content, bg=C["content_bg"])
        row.pack(fill="x", padx=12, pady=(8, 10))

        self.links_btn = tk.Label(
            row, text="▸  Quick Links",
            fg=C["accent"], bg=C["content_bg"],
            font=(SETTINGS["font"], 9, "bold"), cursor="hand2",
        )
        self.links_btn.pack(side="left")
        self.links_btn.bind("<Button-1>", self.toggle_links)
        self.links_btn.bind("<Enter>", lambda e: self.links_btn.config(fg=C["link"]))
        self.links_btn.bind("<Leave>", lambda e: self.links_btn.config(fg=C["accent"]))

        # ⓘ developer credit (hover 5 s → tooltip 1 s)
        self.lbl_info = tk.Label(
            row, text="  ⓘ",
            fg=C["muted"], bg=C["content_bg"],
            font=(SETTINGS["font"], 9, "italic"), cursor="hand2",
        )
        self.lbl_info.pack(side="left")
        self.lbl_info.bind("<Enter>", self._tooltip_enter)
        self.lbl_info.bind("<Leave>", self._tooltip_leave)

        # ── Quick Links panel ─────────────────────────────────────
        self.links_frame = tk.Frame(
            self.content, bg=C["menu_bg"],
            highlightbackground=C["border"], highlightthickness=1,
        )

        for item in LINKS:
            if item["type"] == "link":
                url = item["url"]
                make_link(
                    self.links_frame, item["label"],
                    command=lambda u=url: self._open_url(u),
                ).pack(fill="x", padx=10, pady=2)

            elif item["type"] == "mail":
                addr = item["address"]
                make_link(
                    self.links_frame, item["label"],
                    fg=COLORS["link"],
                    command=lambda a=addr: self._open_mail(a),
                ).pack(fill="x", padx=10, pady=2)

            elif item["type"] == "text":
                tk.Label(
                    self.links_frame, text=item["label"],
                    fg=C["text"], bg=C["menu_bg"],
                    font=(SETTINGS["font"], 9), anchor="w",
                ).pack(fill="x", padx=10, pady=2)

        # bottom padding inside links panel
        tk.Frame(self.links_frame, bg=C["menu_bg"], height=6).pack()

    # ------------------------------------------------------------------
    #  Arrow animation
    # ------------------------------------------------------------------

    def _animate_arrow(self) -> None:
        self._stop_arrow_anim()
        if self.is_open:
            return
        colors = ["#FFFFFF", "#FFD0BB", "#FFFFFF", "#FFD0BB", "#FFFFFF"]
        sizes  = [11, 12, 13, 12, 11]

        def _step():
            if self.is_open:
                return
            self.arrow_btn.config(
                fg=colors[self._arrow_phase % len(colors)],
                font=(SETTINGS["font"], sizes[self._arrow_phase % len(sizes)], "bold"),
            )
            self._arrow_phase += 1
            self._arrow_job = self.root.after(450, _step)

        _step()

    def _stop_arrow_anim(self) -> None:
        if self._arrow_job:
            self.root.after_cancel(self._arrow_job)
            self._arrow_job = None

    # ------------------------------------------------------------------
    #  Tooltip (developer credit)
    # ------------------------------------------------------------------

    def _tooltip_enter(self, _event) -> None:
        self._tooltip_job = self.root.after(5000, self._show_tooltip)

    def _tooltip_leave(self, _event) -> None:
        if self._tooltip_job:
            self.root.after_cancel(self._tooltip_job)
            self._tooltip_job = None
        self._hide_tooltip()

    def _show_tooltip(self) -> None:
        if self._tooltip_win:
            return
        x = self.lbl_info.winfo_rootx()
        y = self.lbl_info.winfo_rooty() + self.lbl_info.winfo_height() + 4
        self._tooltip_win = tw = tk.Toplevel(self.root)
        tw.overrideredirect(True)
        tw.attributes("-topmost", True)
        tw.geometry(f"+{x}+{y}")
        tk.Label(
            tw,
            text=f"  {SETTINGS['developer_credit']}  ",
            bg=COLORS["accent"], fg="#FFFFFF",
            font=(SETTINGS["font"], 9, "bold"),
            relief="flat", pady=6, padx=4,
        ).pack()
        self.root.after(1000, self._hide_tooltip)

    def _hide_tooltip(self) -> None:
        if self._tooltip_win:
            try:
                self._tooltip_win.destroy()
            except Exception:
                pass
            self._tooltip_win = None

    # ------------------------------------------------------------------
    #  Window positioning & sizing
    # ------------------------------------------------------------------

    def _position_window(self) -> None:
        x = self.root.winfo_screenwidth() - self.W - 10
        self.root.geometry(f"{self.W}x36+{x}+10")

    def _x(self) -> int: return self.root.winfo_x()
    def _y(self) -> int: return self.root.winfo_y()

    def _set_height(self, h: int) -> None:
        self.root.geometry(f"{self.W}x{h}+{self._x()}+{self._y()}")

    def _natural_height(self) -> int:
        self.root.update_idletasks()
        return self.frame.winfo_reqheight()

    # ------------------------------------------------------------------
    #  Drag
    # ------------------------------------------------------------------

    def _drag_start(self, event) -> None:
        self._drag_x = event.x_root - self._x()
        self._drag_y = event.y_root - self._y()

    def _drag_move(self, event) -> None:
        self.root.geometry(
            f"{self.W}x{self.root.winfo_height()}"
            f"+{event.x_root - self._drag_x}+{event.y_root - self._drag_y}"
        )

    # ------------------------------------------------------------------
    #  Expand / collapse
    # ------------------------------------------------------------------

    def toggle(self, _event=None) -> None:
        self.collapse() if self.is_open else self.expand()

    def expand(self) -> None:
        self.is_open = True
        self._stop_arrow_anim()
        self.arrow_btn.config(text="▲", fg="#FFFFFF",
                              font=(SETTINGS["font"], 11, "bold"))
        self._refresh_info()
        self.content.pack(fill="x")
        self._set_height(self._natural_height())
        self._start_timer()

    def collapse(self) -> None:
        self.is_open    = False
        self.links_open = False
        self.arrow_btn.config(text="▼", fg="#FFFFFF",
                              font=(SETTINGS["font"], 11, "bold"))
        self.links_frame.pack_forget()
        self.content.pack_forget()
        self._set_height(36)
        self._cancel_timer()
        self._arrow_phase = 0
        self._animate_arrow()

    def toggle_links(self, _event=None) -> None:
        self._reset_timer()
        if self.links_open:
            self.links_frame.pack_forget()
            self.links_open = False
            self.links_btn.config(text="▸  Quick Links", fg=COLORS["accent"])
        else:
            self.links_frame.pack(fill="x")
            self.links_open = True
            self.links_btn.config(text="▾  Quick Links", fg=COLORS["link"])
        self._set_height(self._natural_height())

    # ------------------------------------------------------------------
    #  System info
    # ------------------------------------------------------------------

    def _refresh_info(self) -> None:
        self.lbl_ip.config(    text=f"IP Address   :  {self._get_ip()}")
        self.lbl_mac.config(   text=f"MAC Address  :  {self._get_mac()}")
        self.lbl_user.config(  text=f"Username     :  {os.environ.get('USERNAME', socket.gethostname())}")
        status, detail = self._get_domain()
        self.lbl_domain.config(
            text=f"Domain       :  {status}  ({detail})",
            fg=COLORS["online"] if status == "Active" else COLORS["offline"],
        )

    def _get_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            if ip and not ip.startswith("127."):
                return ip
        except Exception:
            pass
        try:
            out = subprocess.check_output(
                ["ipconfig"], creationflags=subprocess.CREATE_NO_WINDOW,
            ).decode("cp857", errors="ignore")
            for ip in re.findall(r"IPv4[^:]*:\s*([0-9.]+)", out, re.IGNORECASE):
                if not ip.startswith("127.") and not ip.startswith("169.254."):
                    return ip
        except Exception:
            pass
        return "Not found"

    def _get_mac(self) -> str:
        try:
            raw = uuid.UUID(int=uuid.getnode()).hex[-12:]
            return ":".join(raw[i:i+2].upper() for i in range(0, 12, 2))
        except Exception:
            return "Not found"

    def _get_domain(self) -> tuple[str, str]:
        try:
            ps = (
                "$cs=Get-CimInstance Win32_ComputerSystem;"
                'Write-Output ("POD="+$cs.PartOfDomain);'
                'Write-Output ("DOM="+$cs.Domain)'
            )
            out = subprocess.check_output(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
                creationflags=subprocess.CREATE_NO_WINDOW, timeout=5,
            ).decode(errors="ignore")
            pod = re.search(r"POD=(True|False)", out, re.IGNORECASE)
            dom = re.search(r"DOM=(.+)", out)
            if pod and pod.group(1).lower() == "true":
                return "Active", (dom.group(1).strip() if dom else "Joined")
            return "Inactive", "Workgroup / Local"
        except Exception:
            pass
        ud = os.environ.get("USERDNSDOMAIN") or os.environ.get("USERDOMAIN", "")
        if ud and ud.lower() not in ("workgroup", socket.gethostname().lower()):
            return "Active", ud
        return "Inactive", "Unknown"

    # ------------------------------------------------------------------
    #  URL / mail helpers
    # ------------------------------------------------------------------

    def _open_url(self, url: str) -> None:
        self._reset_timer()
        try:
            subprocess.Popen(
                ["cmd", "/c", "start", "", url],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except Exception:
            os.startfile(url)

    def _open_mail(self, address: str) -> None:
        self._reset_timer()
        try:
            subprocess.Popen(
                ["cmd", "/c", "start", "", f"mailto:{address}"],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except Exception:
            os.startfile(f"mailto:{address}")

    # ------------------------------------------------------------------
    #  Auto-collapse timer
    # ------------------------------------------------------------------

    def _start_timer(self) -> None:
        self._cancel_timer()
        self.timer = self.root.after(SETTINGS["auto_collapse_ms"], self.collapse)

    def _cancel_timer(self) -> None:
        if self.timer:
            self.root.after_cancel(self.timer)
            self.timer = None

    def _reset_timer(self) -> None:
        if self.is_open:
            self._start_timer()


# ---------------------------------------------------------------------------
#  Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    SysInfoWidget(root)
    root.mainloop()
