#!/usr/bin/env python3
"""
GDork v1.0 — PHP Google Dork Generator
Current as of 25/03/2026
Operators sourced from Google Search Central (Dec 2025) + expert testing.

For authorised security research / penetration testing only.
"""

import sys
try:
    import curses
except ImportError:
    try:
        import windows_curses as curses   # pip install windows-curses
    except ImportError:
        print("Missing dependency. Run:  pip install windows-curses pyperclip")
        sys.exit(1)
import random
try:
    import pyperclip
    HAS_CLIPBOARD = True
except ImportError:
    HAS_CLIPBOARD = False

# ═══════════════════════════════════════════════════════════════════════════════
# 2026 OPERATOR REFERENCE
# Source: Google Search Central (updated Dec 10 2025) + real-world testing
# Deprecated (DO NOT USE): cache:, related:, link:, info:, phonebook:, ~
# ═══════════════════════════════════════════════════════════════════════════════

OPERATOR_NOTES = """
WORKING OPERATORS — as of 25/03/2026
Source: Google Search Central (Dec 2025) + expert consensus
──────────────────────────────────────────────────────────

STABLE (reliable):
  "phrase"       Exact phrase match (forces literal string)
  -term          Exclude term from results
  OR  |          Either term (OR must be UPPERCASE)
  *              Wildcard for any word/phrase
  site:          Restrict to domain or TLD
                   e.g. site:example.com  OR  site:.gov
  filetype:      Match specific file extension
                   e.g. filetype:php  filetype:sql
  ext:           Alias for filetype:
  inurl:         Term must appear in the URL
  allinurl:      ALL terms must appear in the URL
  intitle:       Term must appear in the page <title>
  allintitle:    ALL terms must appear in the page title
  intext:        Term must appear in the body text
  allintext:     ALL terms must appear in the body text
  imagesize:     Filter images by pixel dimensions
                   e.g. imagesize:1920x1080

INCONSISTENT (beta / unreliable — use as hints only):
  before:YYYY-MM-DD   Results indexed before date
  after:YYYY-MM-DD    Results indexed after date
                       (both in beta since April 2019)
  AROUND(N)           Proximity — two terms within N words
                       (frequently ignored by Google)
  define:             Dictionary definition lookup

DEPRECATED — REMOVED, do not use:
  cache:     Removed January 2024
  related:   Removed 2023
  link:      Removed 2017
  info:      Removed 2019
  ~          Synonym tilde — removed 2013
  +          Forced inclusion — removed 2011

BOOLEAN LOGIC:
  space / AND    Implicit AND (both terms required)
  OR  |          Either term
  -              NOT / exclude
  "exact"        Forces literal phrase, no synonyms
  (group)        Parentheses group expressions

EXAMPLES:
  site:*.edu filetype:php inurl:admin
  intitle:"login" inurl:.php -site:github.com
  intext:"DB_PASSWORD" filetype:php after:2023-01-01
  allinurl:admin login php -site:stackoverflow.com
"""

# ═══════════════════════════════════════════════════════════════════════════════
# DORK COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

PHP_FILES = [
    "index.php", "login.php", "admin.php", "config.php", "upload.php",
    "search.php", "register.php", "user.php", "profile.php", "checkout.php",
    "payment.php", "db.php", "connect.php", "includes/config.php",
    "wp-config.php", "phpinfo.php", "install.php", "setup.php",
    "panel.php", "dashboard.php", "manage.php", "api.php", "ajax.php",
    "download.php", "view.php", "file.php", "backup.php", "data.php",
    "redirect.php", "reset.php", "token.php", "export.php", "report.php",
]

PHP_PARAMS = [
    "id", "page", "file", "path", "dir", "search", "q", "query",
    "url", "redirect", "cat", "category", "lang", "user", "username",
    "item", "product", "order", "ref", "return", "target", "src",
    "doc", "pdf", "include", "module", "view", "action", "type",
    "token", "key", "hash", "pass", "password", "cmd", "exec",
]

INURL_PATTERNS = [
    "inurl:{file}",
    "inurl:{file}?{param}=",
    "inurl:/{file}",
    "inurl:php?{param}=",
    "inurl:{param}= filetype:php",
    'inurl:{file} intext:"{param}"',
    "allinurl:{param} {file}",
    'inurl:{file} intitle:"index of"',
]

INTITLE_PATTERNS = [
    'intitle:"Index of" "{file}"',
    'intitle:"phpinfo()"',
    'intitle:"PHP Error" "{file}"',
    'intitle:"Admin Panel" inurl:.php',
    'intitle:"Login" inurl:{file}',
    'intitle:"Dashboard" inurl:.php',
    'intitle:"Setup" inurl:{file}',
    'intitle:"Configuration" filetype:php',
    'allintitle:admin login php',
    'intitle:"Control Panel" inurl:.php',
    'intitle:"File Manager" inurl:.php',
]

FILETYPE_PATTERNS = [
    "filetype:php inurl:{param}=",
    "filetype:php {file}",
    'filetype:php intitle:"index of"',
    "filetype:php inurl:admin",
    "filetype:php inurl:login",
    "filetype:php inurl:config",
    "filetype:php inurl:upload",
    "filetype:php inurl:backup",
    "ext:php inurl:{param}=",
    "ext:php intext:{param}",
    "filetype:php inurl:shell",
    "filetype:php allinurl:admin panel",
]

ERROR_PATTERNS = [
    '"Warning: mysql_fetch" filetype:php',
    '"Warning: include(" filetype:php',
    '"Fatal error:" filetype:php',
    '"mysql_connect()" filetype:php',
    '"Notice: Undefined variable" filetype:php',
    '"Warning: pg_connect()" filetype:php',
    '"ORA-" filetype:php',
    '"SQL syntax" filetype:php',
    'intext:"Warning: mysqli" filetype:php',
    'intext:"PDOException" filetype:php',
    'intext:"stack trace:" filetype:php',
    'intitle:"Fatal error" inurl:.php',
]

EXPOSED_PATTERNS = [
    '"Index of" "backup" filetype:php',
    '"Index of" "db" inurl:.php',
    '"phpMyAdmin" inurl:php',
    '"phpmyadmin" filetype:php',
    '"adminer.php" inurl:adminer',
    '"db_config.php" inurl:config',
    'inurl:wp-config.php filetype:php',
    '"config.php.bak" OR "config.php.old"',
    'inurl:".php~" OR inurl:".php.bak"',
    '"passwd" OR "password" filetype:php inurl:config',
    'intext:"DB_PASSWORD" filetype:php',
    'intext:"define(\'DB_" filetype:php',
    '"env.php" OR ".env" inurl:php',
    'filetype:php inurl:shell intext:uname',
]

SQLI_PATTERNS = [
    'inurl:{file}?{param}=1 intext:"sql"',
    'inurl:"{param}=" filetype:php intext:"mysql_"',
    'allinurl:{param} php intext:"SELECT"',
    'inurl:{file} intext:"You have an error in your SQL"',
    'filetype:php inurl:{param}= intext:"Warning: mysql"',
    'inurl:php?{param}= intext:"ODBC"',
]

UPLOAD_PATTERNS = [
    'inurl:{file} intitle:"file upload"',
    'filetype:php inurl:upload intext:"Choose File"',
    'intitle:"Upload" inurl:upload.php',
    'inurl:fileupload.php OR inurl:upload_file.php',
    'filetype:php intext:"move_uploaded_file"',
    'intitle:"Upload Manager" inurl:.php',
]

LOGIN_PATTERNS = [
    'inurl:{file} intitle:"login" intext:"username"',
    'intitle:"Login" inurl:login.php -site:github.com',
    'inurl:admin/login.php',
    'filetype:php intitle:"admin login"',
    'intext:"Username" intext:"Password" filetype:php',
    'inurl:login.php intext:"Forgot password"',
    'intitle:"Member Login" filetype:php',
]

CATEGORIES = {
    "inurl":      INURL_PATTERNS,
    "intitle":    INTITLE_PATTERNS,
    "filetype":   FILETYPE_PATTERNS,
    "error leak": ERROR_PATTERNS,
    "exposed":    EXPOSED_PATTERNS,
    "sqli":       SQLI_PATTERNS,
    "upload":     UPLOAD_PATTERNS,
    "login":      LOGIN_PATTERNS,
}
CATEGORY_KEYS = list(CATEGORIES.keys())

# ── Option data ───────────────────────────────────────────────────────────────

SITE_TYPES = {
    "None":          "",
    ".com":          "site:.com",
    ".org":          "site:.org",
    ".net":          "site:.net",
    ".edu":          "site:.edu",
    ".gov":          "site:.gov",
    ".mil":          "site:.mil",
    ".co.uk":        "site:.co.uk",
    ".com.au":       "site:.com.au",
    ".io":           "site:.io",
    ".dev":          "site:.dev",
    "Subdomain (*)": "site:*.",
}

COUNTRIES = {
    "None":         "",
    "Australia":    "site:.au",
    "USA":          "site:.us",
    "UK":           "site:.uk",
    "Canada":       "site:.ca",
    "Germany":      "site:.de",
    "France":       "site:.fr",
    "Brazil":       "site:.br",
    "India":        "site:.in",
    "Japan":        "site:.jp",
    "China":        "site:.cn",
    "Russia":       "site:.ru",
    "Netherlands":  "site:.nl",
    "South Africa": "site:.za",
}

DATE_RANGES = {
    "None":        ("", ""),
    "After 2023":  ("after:2023-01-01", ""),
    "After 2024":  ("after:2024-01-01", ""),
    "2023-2024":   ("after:2023-01-01", "before:2025-01-01"),
    "2024-2025":   ("after:2024-01-01", "before:2025-12-31"),
    "Before 2023": ("", "before:2023-01-01"),
    "Before 2022": ("", "before:2022-01-01"),
}

NOISE_EXCLUDES = [
    "-site:github.com",
    "-site:stackoverflow.com",
    "-site:pastebin.com",
    "-site:reddit.com",
    "-site:youtube.com",
    "-inurl:demo",
    "-intitle:demo",
]

# ═══════════════════════════════════════════════════════════════════════════════
# DORK GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def generate_dork(category: str, options: dict) -> str:
    pattern = random.choice(CATEGORIES[category])
    f = random.choice(PHP_FILES)
    p = random.choice(PHP_PARAMS)
    parts = [pattern.format(file=f, param=p)]

    # site type (TLD) — ignored if domain is set
    if not options.get("domain", "").strip():
        if options.get("site_type") and options["site_type"] != "None":
            st = SITE_TYPES[options["site_type"]]
            if st == "site:*.":
                parts.append(f"site:*.{random.choice(['com','net','org'])}")
            elif st:
                parts.append(st)
        elif options.get("country") and options["country"] != "None":
            cc = COUNTRIES[options["country"]]
            if cc:
                parts.append(cc)

    # specific domain (overrides TLD/country)
    if options.get("domain", "").strip():
        parts.append(f"site:{options['domain'].strip()}")

    # keywords
    for kw in options.get("keywords", []):
        kw = kw.strip()
        if kw:
            parts.append(f'intext:"{kw}"' if " " in kw else f"intext:{kw}")

    # exclude keywords
    for ex in options.get("excludes", []):
        ex = ex.strip()
        if ex:
            parts.append(f'-intext:"{ex}"' if " " in ex else f"-intext:{ex}")

    # date range (before/after — beta operators)
    dr = options.get("date_range", "None")
    if dr and dr != "None":
        after_op, before_op = DATE_RANGES[dr]
        if after_op:
            parts.append(after_op)
        if before_op:
            parts.append(before_op)

    # noise filter
    if options.get("exclude_noise"):
        parts.extend(random.sample(NOISE_EXCLUDES, k=min(2, len(NOISE_EXCLUDES))))

    return " ".join(parts)


def generate_batch(category: str, count: int, options: dict) -> list:
    cat = category if category != "[ ALL CATEGORIES ]" else random.choice(CATEGORY_KEYS)
    dorks: set = set()
    attempts = 0
    while len(dorks) < count and attempts < count * 20:
        dorks.add(generate_dork(cat, options))
        attempts += 1
    return list(dorks)


# ═══════════════════════════════════════════════════════════════════════════════
# BANNER  (multi-colour nerd face + GDork wordmark)
# ═══════════════════════════════════════════════════════════════════════════════

BANNER_ROWS = [
    [(" ██████╗ ", 6), ("██████╗  ", 7), ("██████╗  ", 8), ("██████╗  ", 9), ("██╗  ██╗", 6)],
    [("██╔════╝ ", 6), ("██╔══██╗ ", 7), ("██╔═══██╗", 8), ("██╔══██╗ ", 9), ("██║ ██╔╝", 6)],
    [("██║  ███╗", 6), ("██║  ██║ ", 7), ("██║   ██║", 8), ("██████╔╝ ", 9), ("█████╔╝ ", 6)],
    [("██║   ██║", 6), ("██║  ██║ ", 7), ("██║   ██║", 8), ("██╔══██╗ ", 9), ("██╔═██╗ ", 6)],
    [("╚██████╔╝", 6), ("██████╔╝ ", 7), ("╚██████╔╝", 8), ("██║  ██╗ ", 9), ("██║  ██╗", 6)],
    [(" ╚═════╝ ", 6), ("╚═════╝  ", 7), (" ╚═════╝ ", 8), ("╚═╝  ╚═╝ ", 9), ("╚═╝  ╚═╝", 6)],
    [(" P H P  ", 12), ("·  ", 10), ("G O O G L E  ", 7),
     ("·  ", 10), ("D O R K  G E N", 9), ("  ·  ", 10), ("v 1 . 0", 8)],
    [("·" * 55, 5)],
]
BANNER_HEIGHT = len(BANNER_ROWS)


# ═══════════════════════════════════════════════════════════════════════════════
# DRAWING HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def safe_addstr(win, y, x, text, attr=0):
    try:
        win.addstr(y, x, text, attr)
    except curses.error:
        pass


def draw_box(win, y, x, h, w, title=""):
    try:
        win.attron(curses.color_pair(3))
        win.addch(y, x, curses.ACS_ULCORNER)
        win.addch(y, x + w - 1, curses.ACS_URCORNER)
        win.addch(y + h - 1, x, curses.ACS_LLCORNER)
        win.addch(y + h - 1, x + w - 1, curses.ACS_LRCORNER)
        for i in range(1, w - 1):
            win.addch(y, x + i, curses.ACS_HLINE)
            win.addch(y + h - 1, x + i, curses.ACS_HLINE)
        for i in range(1, h - 1):
            win.addch(y + i, x, curses.ACS_VLINE)
            win.addch(y + i, x + w - 1, curses.ACS_VLINE)
        if title:
            win.addstr(y, x + 2, f" {title} ", curses.color_pair(4) | curses.A_BOLD)
        win.attroff(curses.color_pair(3))
    except curses.error:
        pass


def draw_banner(win, start_y, max_x):
    for row_i, row in enumerate(BANNER_ROWS):
        total_len = sum(len(c) for c, _ in row)
        cur_x = max(0, (max_x - total_len) // 2)
        for chunk, pair in row:
            if cur_x >= max_x:
                break
            safe = chunk[:max(0, max_x - cur_x)]
            try:
                win.addstr(start_y + row_i, cur_x, safe,
                           curses.color_pair(pair) | curses.A_BOLD)
            except curses.error:
                pass
            cur_x += len(safe)


# ═══════════════════════════════════════════════════════════════════════════════
# SCREENS
# ═══════════════════════════════════════════════════════════════════════════════

def menu_screen(stdscr):
    """Main category selector."""
    curses.curs_set(0)
    stdscr.keypad(True)
    sel = 0
    items = CATEGORY_KEYS + ["[ ALL CATEGORIES ]", "[ QUIT ]"]

    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        draw_banner(stdscr, 1, max_x)

        menu_y = BANNER_HEIGHT + 2
        box_w = 48
        box_x = max(0, max_x // 2 - box_w // 2)
        draw_box(stdscr, menu_y, box_x, len(items) + 4, box_w, "SELECT CATEGORY")

        for i, item in enumerate(items):
            label = f"  {item.upper():<{box_w - 6}}"
            y = menu_y + 2 + i
            attr = curses.color_pair(1) | curses.A_BOLD | curses.A_REVERSE if i == sel \
                else curses.color_pair(1)
            safe_addstr(stdscr, y, box_x + 2, label[:box_w - 4], attr)

        hint = "↑↓/jk Navigate   Enter Select   q Quit   ? Operators"
        safe_addstr(stdscr, max_y - 2, 2, hint[:max_x - 4], curses.color_pair(5))
        stdscr.refresh()

        key = stdscr.getch()
        if key in (curses.KEY_UP, ord('k')) and sel > 0:
            sel -= 1
        elif key in (curses.KEY_DOWN, ord('j')) and sel < len(items) - 1:
            sel += 1
        elif key in (curses.KEY_ENTER, 10, 13):
            chosen = items[sel]
            return None if chosen == "[ QUIT ]" else chosen
        elif key == ord('?'):
            operator_help_screen(stdscr)
        elif key in (ord('q'), 27):
            return None


def options_screen(stdscr, category: str):
    """
    Options builder — returns a dict or None (go back).

    Fields:
      Site Type (TLD)          cycle through SITE_TYPES
      Country TLD              cycle through COUNTRIES
      Specific Domain          free-text  (overrides TLD/country)
      Keywords (intext)        comma-separated free-text
      Exclude Keywords         comma-separated free-text
      Date Range               cycle through DATE_RANGES
      Filter Noise             toggle (exclude github, SO, etc.)
      How Many Dorks           free-text number 1-100
    """
    curses.curs_set(0)
    stdscr.keypad(True)

    site_type_keys  = list(SITE_TYPES.keys())
    country_keys    = list(COUNTRIES.keys())
    date_range_keys = list(DATE_RANGES.keys())

    # internal state
    state = {
        "site_type":     0,
        "country":       0,
        "domain":        "",
        "keywords":      "",
        "excludes":      "",
        "date_range":    0,
        "exclude_noise": False,
        "count":         "10",
    }

    FIELDS = [
        # (display label,            ftype,    state key,        choices list)
        ("Site Type (TLD)",          "cycle",  "site_type",      site_type_keys),
        ("Country TLD",              "cycle",  "country",        country_keys),
        ("Specific Domain",          "text",   "domain",         None),
        ("Keywords  (intext, CSV)",  "text",   "keywords",       None),
        ("Exclude Keywords  (CSV)",  "text",   "excludes",       None),
        ("Date Range",               "cycle",  "date_range",     date_range_keys),
        ("Filter Noise (github etc)","toggle", "exclude_noise",  None),
        ("How Many Dorks  (1-100)",  "text",   "count",          None),
    ]

    sel     = 0
    editing = False
    edit_buf = ""
    status  = ""

    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        draw_banner(stdscr, 1, max_x)

        box_y = BANNER_HEIGHT + 2
        box_w = min(64, max_x - 4)
        box_x = max(0, max_x // 2 - box_w // 2)
        box_h = len(FIELDS) + 6
        draw_box(stdscr, box_y, box_x, box_h, box_w,
                 f"OPTIONS  ▸  {category.upper()}")

        for i, (label, ftype, skey, choices) in enumerate(FIELDS):
            y = box_y + 2 + i
            if ftype == "cycle":
                val = choices[state[skey]]
            elif ftype == "toggle":
                val = "YES ✔" if state[skey] else "NO"
            else:
                val = edit_buf if (editing and i == sel) else (state[skey] or "—")

            # truncate so we don't overflow box
            val_w = box_w - 40
            row = f"  {label:<35} {val[:val_w]}"
            attr = curses.color_pair(1) | curses.A_BOLD | curses.A_REVERSE if i == sel \
                else curses.color_pair(2)
            safe_addstr(stdscr, y, box_x + 1, row[:box_w - 2], attr)

        hint_y = box_y + box_h - 2
        if editing:
            safe_addstr(stdscr, hint_y, box_x + 2,
                        "Type  Enter=confirm  ESC=cancel",
                        curses.color_pair(8) | curses.A_BOLD)
        else:
            safe_addstr(stdscr, hint_y, box_x + 2,
                        "Enter=edit/cycle  Space=toggle  G=generate  Q=back",
                        curses.color_pair(5))

        if status:
            safe_addstr(stdscr, max_y - 3, 2, status[:max_x - 4], curses.color_pair(7))

        stdscr.refresh()
        key = stdscr.getch()

        if editing:
            if key in (curses.KEY_ENTER, 10, 13):
                state[FIELDS[sel][2]] = edit_buf
                editing = False
                edit_buf = ""
            elif key == 27:
                editing = False
                edit_buf = ""
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                edit_buf = edit_buf[:-1]
            elif 32 <= key <= 126:
                edit_buf += chr(key)
        else:
            ftype = FIELDS[sel][1]
            skey  = FIELDS[sel][2]
            choices = FIELDS[sel][3]

            if key in (curses.KEY_UP, ord('k')) and sel > 0:
                sel -= 1
            elif key in (curses.KEY_DOWN, ord('j')) and sel < len(FIELDS) - 1:
                sel += 1
            elif key in (curses.KEY_ENTER, 10, 13):
                if ftype == "cycle":
                    state[skey] = (state[skey] + 1) % len(choices)
                elif ftype == "toggle":
                    state[skey] = not state[skey]
                else:
                    editing = True
                    edit_buf = state[skey]
            elif key == ord(' ') and ftype == "toggle":
                state[skey] = not state[skey]
            elif key in (ord('g'), ord('G')):
                try:
                    n = int(state["count"])
                    if not (1 <= n <= 100):
                        raise ValueError
                except ValueError:
                    status = "✘  Count must be 1–100. Fix 'How Many Dorks'."
                    continue
                return {
                    "site_type":     site_type_keys[state["site_type"]],
                    "country":       country_keys[state["country"]],
                    "domain":        state["domain"],
                    "keywords":      [k.strip() for k in state["keywords"].split(",") if k.strip()],
                    "excludes":      [k.strip() for k in state["excludes"].split(",") if k.strip()],
                    "date_range":    date_range_keys[state["date_range"]],
                    "exclude_noise": state["exclude_noise"],
                    "count":         n,
                }
            elif key in (ord('q'), ord('Q'), 27):
                return None


def results_screen(stdscr, category: str, options: dict):
    """Display generated dorks with scroll, copy, save, regen."""
    curses.curs_set(0)
    stdscr.keypad(True)
    scroll = 0
    dorks = generate_batch(category, options["count"], options)
    status_msg = ""

    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()

        title = f" GDork v1.0  ▸  {category.upper()}  ▸  {len(dorks)} DORKS "
        safe_addstr(stdscr, 0, 0, title[:max_x].ljust(max_x),
                    curses.color_pair(1) | curses.A_REVERSE)

        box_h = max_y - 4
        box_w = max_x - 4
        draw_box(stdscr, 1, 2, box_h, box_w, "RESULTS")

        visible = box_h - 2
        for i in range(visible):
            idx = scroll + i
            if idx >= len(dorks):
                break
            line = f"  [{idx + 1:02d}]  {dorks[idx]}"
            safe_addstr(stdscr, 2 + i, 3, line[:box_w - 2], curses.color_pair(2))

        if len(dorks) > visible:
            pct = int((scroll / max(1, len(dorks) - visible)) * 100)
            safe_addstr(stdscr, 1, max_x - 8, f" {pct:3d}% ", curses.color_pair(5))

        bar = f"  [r] Regen  [c] Copy  [s] Save  [?] Operators  [q] Back   {status_msg}"
        safe_addstr(stdscr, max_y - 2, 0, bar[:max_x].ljust(max_x), curses.color_pair(5))
        stdscr.refresh()
        status_msg = ""

        key = stdscr.getch()
        if key in (curses.KEY_UP, ord('k')) and scroll > 0:
            scroll -= 1
        elif key in (curses.KEY_DOWN, ord('j')) and scroll < max(0, len(dorks) - visible):
            scroll += 1
        elif key == ord('r'):
            dorks = generate_batch(category, options["count"], options)
            scroll = 0
            status_msg = "✔ Regenerated!"
        elif key == ord('c'):
            if HAS_CLIPBOARD:
                try:
                    pyperclip.copy("\n".join(dorks))
                    status_msg = "✔ Copied to clipboard!"
                except Exception:
                    status_msg = "✘ Clipboard error (try: sudo apt install xclip)"
            else:
                status_msg = "✘ pyperclip not installed  (pip install pyperclip)"
        elif key == ord('s'):
            fname = f"dorks_{category.replace(' ', '_')}.txt"
            with open(fname, "w") as fh:
                fh.write(f"# GDork v1.0  |  Category: {category}  |  {len(dorks)} dorks\n")
                fh.write(f"# Options: {options}\n\n")
                fh.write("\n".join(dorks) + "\n")
            status_msg = f"✔ Saved → {fname}"
        elif key == ord('?'):
            operator_help_screen(stdscr)
        elif key in (ord('q'), 27):
            break


def operator_help_screen(stdscr):
    """Scrollable 2026 operator reference."""
    curses.curs_set(0)
    stdscr.keypad(True)
    lines = OPERATOR_NOTES.strip().splitlines()
    scroll = 0

    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        draw_box(stdscr, 0, 0, max_y - 1, max_x,
                 "GOOGLE DORK OPERATORS  ─  25/03/2026")
        visible = max_y - 3
        for i in range(visible):
            idx = scroll + i
            if idx >= len(lines):
                break
            line = lines[idx]
            if line.startswith("  ") and ":" in line:
                color = curses.color_pair(4) | curses.A_BOLD
            elif any(line.startswith(h) for h in ("STABLE", "INCON", "DEPR", "BOOL", "EXAM", "WORK")):
                color = curses.color_pair(9) | curses.A_BOLD
            else:
                color = curses.color_pair(10)
            safe_addstr(stdscr, 1 + i, 2, line[:max_x - 4], color)

        safe_addstr(stdscr, max_y - 2, 2, "↑↓/jk Scroll   q/ESC Close",
                    curses.color_pair(5))
        stdscr.refresh()

        key = stdscr.getch()
        if key in (curses.KEY_UP, ord('k')) and scroll > 0:
            scroll -= 1
        elif key in (curses.KEY_DOWN, ord('j')) and scroll < max(0, len(lines) - visible):
            scroll += 1
        elif key in (ord('q'), 27):
            break


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main(stdscr):
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1,  curses.COLOR_GREEN,   -1)   # menu / title bar
    curses.init_pair(2,  curses.COLOR_CYAN,    -1)   # results body
    curses.init_pair(3,  curses.COLOR_GREEN,   -1)   # box borders
    curses.init_pair(4,  curses.COLOR_YELLOW,  -1)   # labels / highlights
    curses.init_pair(5,  curses.COLOR_WHITE,   -1)   # dim / help text
    curses.init_pair(6,  curses.COLOR_BLUE,    -1)   # Google Blue  (G)
    curses.init_pair(7,  curses.COLOR_RED,     -1)   # Google Red   (D)
    curses.init_pair(8,  curses.COLOR_YELLOW,  -1)   # Google Yellow(O)
    curses.init_pair(9,  curses.COLOR_GREEN,   -1)   # Google Green (r/k)
    curses.init_pair(10, curses.COLOR_WHITE,   -1)   # Bright / nerd face
    curses.init_pair(11, curses.COLOR_CYAN,    -1)   # Glasses / shirt
    curses.init_pair(12, curses.COLOR_MAGENTA, -1)   # Buck teeth / PHP tag

    while True:
        category = menu_screen(stdscr)
        if category is None:
            break

        options = options_screen(stdscr, category)
        if options is None:
            continue

        results_screen(stdscr, category, options)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nBye!")
        sys.exit(0)
