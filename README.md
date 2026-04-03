# SysInfo Widget

A lightweight, borderless Windows desktop widget built with Python and Tkinter.  
It displays live network and system information in a compact, always-accessible overlay — useful for IT support staff, sysadmins, or power users.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

- **IP Address** — detected via UDP socket with `ipconfig` fallback  
- **MAC Address** — from `uuid.getnode()`  
- **Username** — current Windows session user  
- **Domain status** — Active / Inactive via WMI (`Win32_ComputerSystem`)  
- **Quick Links panel** — fully configurable shortcuts (URLs, mailto, plain text)  
- **Draggable header** — reposition anywhere on screen  
- **Arrow pulse animation** — subtle hint that the widget is interactive  
- **Developer credit tooltip** — hover the ⓘ icon for 5 s  
- **Auto-collapse** — folds back after 30 s of inactivity (configurable)  
- **Sinks behind other windows** — not permanently on top  

---

## Requirements

- Windows 10 / 11  
- Python 3.9+  
- No third-party packages — standard library only (`tkinter`, `socket`, `subprocess`, `uuid`, `re`, `os`)

---

## Quick Start

```bash
git clone https://github.com/erendogan83/sysinfo-widget-for-windows.git
cd sysinfo-widget
python widget.py
```

---

## Configuration

All customisation lives in **`config.py`** — no need to touch `widget.py`.

### Title & font

```python
SETTINGS = {
    "title"            : "IT DEPARTMENT",
    "font"             : "Segoe UI",
    "width"            : 340,
    "auto_collapse_ms" : 30_000,
    "developer_credit" : "developed by Eren DOĞAN",
}
```

### Colours

```python
COLORS = {
    "header"  : "#E8490F",   # header background
    "accent"  : "#E8490F",   # accent / highlight colour
    "online"  : "#1E7E34",   # domain Active indicator
    "offline" : "#C0392B",   # domain Inactive indicator
    # ... see config.py for full list
}
```

### Quick Links

Add, remove or reorder entries in the `LINKS` list:

```python
LINKS = [
    {"type": "link", "label": "🔑  Password Reset", "url": "https://..."},
    {"type": "mail", "label": "✉  helpdesk@example.com", "address": "helpdesk@example.com"},
    {"type": "text", "label": "📞  Helpdesk: ext. 1000"},
]
```

| type   | required keys          | behaviour                        |
|--------|------------------------|----------------------------------|
| `link` | `label`, `url`         | opens URL in default browser     |
| `mail` | `label`, `address`     | opens `mailto:` in mail client   |
| `text` | `label`                | non-clickable info row           |

---

## Run on Startup (optional)

Create a shortcut to `widget.py` (or a `.bat` wrapper) and place it in:

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
```

Or use Task Scheduler for more control (run at logon, any user, highest privileges).

---

## Project Structure

```
sysinfo-widget/
├── widget.py      # Application logic — do not edit for customisation
├── config.py      # All user-facing settings (title, colours, links)
└── README.md
```

---

## License

MIT — free to use, modify and distribute. See [LICENSE](LICENSE) for details.

---

## Author

**Eren DOĞAN**  
[GitHub](https://github.com/erendogan83) · [LinkedIn](https://www.linkedin.com/in/eren-dogan27/) · [ORCID](https://orcid.org/0009-0009-0430-3395)
