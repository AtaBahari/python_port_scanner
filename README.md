# Simple Port Scanner (Python)

A lightweight, script-mode TCP port scanner written in Python.  
Provides flexible scanning via command-line arguments or an optional interactive menu: scan common ports, custom ranges, specific ports, or full-range sweeps, with ThreadPool-based concurrency and CSV/JSON output.

- **Version:** v1.1.1  
- **Build date:** 2025-10-03

> **Warning:** Only scan targets you own or have explicit permission to test. Unauthorized scanning may be illegal and may be detected by intrusion detection systems.

---

## Repository contents

- `cli_port_scanner.py` — Interactive, menu-driven scanner (recommended for end users).  
- `port_scanner.py` — Script-mode scanner (if included).  
- `.gitignore` — Recommended ignore rules for this project.  
- `LICENSE` — MIT license.  
- `README.md` — This file.

---

## Short description

A small, script-driven TCP port scanner with an optional interactive menu.  
Scan all ports, common ports, ranges, or a custom list of ports. Results can be saved as CSV or JSON.

---

## Requirements

- Python 3.7 or newer (3.8+ recommended).  
- Optional: `pyfiglet` (for ASCII banner): `pip install pyfiglet`.  
- No other external libraries required — scanning uses Python standard library.

---

## Full Installation & Setup

1. Clone the repository or download the ZIP and extract it, then change into the project folder:
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

2. (Recommended) Create and activate a virtual environment:

- macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate

- Windows (PowerShell):
python -m venv .venv
.\.venv\Scripts\Activate.ps1

Deactivate with:
deactivate

3. (Optional) Install decorative banner:
pip install pyfiglet

4. (Optional, Unix/macOS) Make scripts executable:
chmod +x cli_port_scanner.py
./cli_port_scanner.py --help
Or run with Python:
python cli_port_scanner.py --help

5. Windows PATH note:
C:\Path\to\python.exe cli_port_scanner.py

6. Security note: Always obtain explicit permission before scanning systems you do not own.

---

## Interactive menu (run & behavior)

Run:
python cli_port_scanner.py

Menu behavior:
- Main menu:
  1. Run Scanner
  2. Contact / About
  3. Exit
- Scanner submenu:
  - Scan ALL ports (1–65535) — heavy; requires confirmation.
  - Scan common ports.
  - Scan a RANGE (e.g., 1000-2000).
  - Scan SPECIFIC ports (e.g., 22,80,8000-8100).
  - Back / Exit.
- Saving output:
  - Enter `report.csv` or `report.json` for file.
  - Enter a filename without extension → choose CSV/JSON.
  - Leave blank → auto-generates <host>_YYYYMMDD_HHMMSS.<ext>.
  - Type 'n' / 'no' to skip saving.

---

## Command-line usage (script-mode)

Typical flags:
- `--host` / `-H` : target hostname or IP (required).  
- `--start` / `--end` : start & end port numbers.  
- `--ports` : comma-separated list/ranges (22,80,8000-8100).  
- `--threads` : concurrency.  
- `--timeout` : socket timeout (seconds).  
- `--output` : .csv or .json path.

---

## Output format

CSV/JSON fields: host, ip, port, status, scanned_at  
- status is open or closed.  
- scanned_at is ISO8601 timestamp.

---

## Examples & recommended workflows

- Quick check: scan common ports (22,80,443).  
- Save results: use CSV/JSON.  
- Full audit: only on authorized, isolated networks; conservative threads/timeouts.

---

## Troubleshooting

- python: command not found → install Python or try python3.  
- DNS fails → use IP.  
- Slow scans → increase timeout/reduce threads.  
- File permission errors → check write access.  
- Corporate networks may block scans → obtain authorization.

---

## Contact

- Author: ata bahari  
- Email: iatabahari@gmail.com  
- GitHub: https://github.com/atabahri  
- Telegram / Instagram / X: @atabahari

---

## License

MIT — see LICENSE file.

---

## Changelog

- v1.1.1 (2025-10-03) — auto CSV/JSON filename, selectable output, improved submenu handling, minor bug fixes.  
- v1.1.0 (2025-10-03) — version/build date, improved output, CSV saving.  
- v1.0.0 — initial release.
'@; Set-Content -Path README.md -Value $readme -Encoding UTF8
