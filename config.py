"""
config.py  —  SysInfo Widget configuration
===========================================
Edit this file to customise the widget without touching widget.py.
"""

# ---------------------------------------------------------------------------
#  General settings
# ---------------------------------------------------------------------------

SETTINGS = {
    "title"            : "IT DEPARTMENT",   # Header bar title
    "font"             : "Segoe UI",        # Font family (Windows)
    "width"            : 340,               # Widget width in pixels
    "auto_collapse_ms" : 30_000,            # Auto-close delay (ms). 0 = disabled
    "developer_credit" : "developed by Eren DOĞAN",  # Shown on ⓘ hover (5 s)
}


# ---------------------------------------------------------------------------
#  Colour palette
# ---------------------------------------------------------------------------

COLORS = {
    # Backgrounds
    "bg"           : "#F5F5F5",   # outer frame
    "header"       : "#E8490F",   # header bar
    "header_hover" : "#C73D0A",   # arrow button hover
    "content_bg"   : "#FFFFFF",   # info panel
    "menu_bg"      : "#F0F0F0",   # quick-links panel
    "hover"        : "#FFE5D9",   # link hover background

    # Foregrounds
    "text"         : "#1A1A1A",   # primary text
    "muted"        : "#6B6B6B",   # secondary / ⓘ icon
    "accent"       : "#E8490F",   # accent colour (matches header)
    "link"         : "#C73D0A",   # hyperlink colour

    # Status indicators
    "online"       : "#1E7E34",   # domain Active
    "offline"      : "#C0392B",   # domain Inactive

    # Structural
    "border"       : "#D0D0D0",
}


# ---------------------------------------------------------------------------
#  Quick Links panel
# ---------------------------------------------------------------------------
# Each entry is a dict with a "type" key:
#
#   type "link"  → clickable URL
#       label    : displayed text (emoji supported)
#       url      : target URL
#
#   type "mail"  → opens default mail client
#       label    : displayed text
#       address  : email address
#
#   type "text"  → non-clickable info row
#       label    : displayed text
#
# Add, remove or reorder entries freely.
# ---------------------------------------------------------------------------

LINKS = [
    {
        "type"  : "link",
        "label" : "🔑  Password Reset",
        "url"   : "https://example.com/password-reset",
    },
    {
        "type"  : "link",
        "label" : "🌐  IT Portal",
        "url"   : "https://example.com/it-portal",
    },
    {
        "type"  : "link",
        "label" : "📖  Internal Phone Directory",
        "url"   : "https://example.com/directory",
    },
    {
        "type"  : "text",
        "label" : "📞  Helpdesk: ext. 1000",
    },
    {
        "type"  : "mail",
        "label" : "✉  helpdesk@example.com",
        "address": "helpdesk@example.com",
    },
]
