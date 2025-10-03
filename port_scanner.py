#!/usr/bin/env python3
"""
cli_port_scanner.py
Interactive menu-driven port scanner for terminals (Windows & *nix).

- Landing page uses pyfiglet for a banner if installed (optional).
- Main menu: 1) Run Scanner  2) Contact/About  3) Exit
- Scanner submenu: All ports / Common / Range / Specific / Back / Exit

WARNING: Only scan systems you own or have explicit permission to test.
"""

import os
import socket
import csv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import sys

# Script metadata
__version__ = "v1.1.1"
__build_date__ = "2025-10-03"

# Try to import pyfiglet for a nicer banner. If not available, fallback to plain text.
try:
    from pyfiglet import Figlet
    HAVE_PYFIGLET = True
except Exception:
    HAVE_PYFIGLET = False

# Common ports list for the "common ports" option
COMMON_PORTS = [
    21, 22, 23, 25, 53, 67, 68, 69, 80, 110, 111, 123,
    135, 139, 143, 161, 389, 443, 445, 465, 587, 631,
    993, 995, 3306, 3389, 5900, 6379, 8080
]

# Contact info (customized by user)
CONTACT_INFO = {
    "name": "ata bahari",
    "email": "iatabahari@gmail.com",
    "github": "https://github.com/atabahri",
    "telegram": "atabahari",
    "instagram": "atabahari",
    "x": "atabahari"
}


def clear_screen():
    """Clear the terminal screen (cross-platform)."""
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def print_banner(text="PORT SCANNER", font="slant"):
    """Print a banner using pyfiglet if available, otherwise print plain text."""
    if HAVE_PYFIGLET:
        try:
            print(Figlet(font=font).renderText(text))
        except Exception:
            print(text)
    else:
        print("=" * 60)
        print(text.center(60))
        print("=" * 60)


def scan_port(host_ip, port, timeout=1.0):
    """Scan a single TCP port. Return (port, is_open)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((host_ip, port))
            return port, (result == 0)
    except Exception:
        return port, False


def choose_output_filename(hostname, default_format="csv"):
    """
    Prompt the user to choose an output filename and format.

    Behavior:
    - If the user types 'n' or 'no' -> returns None (skip saving).
    - If the user provides a filename with .csv or .json extension -> uses it.
    - If the user provides a filename without extension -> asks format (CSV/JSON) then appends it.
    - If the user leaves the input blank -> auto-generate
       <safe-host>_YYYYMMDD_HHMMSS.<ext> where ext = chosen format (default csv).
    """
    while True:
        name_in = input("Optional output filename (leave empty = auto-name, or type 'n' to skip saving): ").strip()
        if name_in.lower() in ('n', 'no'):
            return None

        # If blank -> auto-generate
        if name_in == "":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_host = hostname.replace('/', '_').replace(':', '_').replace('\\', '_')
            filename = f"{safe_host}_{timestamp}.{default_format}"
            return filename

        base, ext = os.path.splitext(name_in)
        if ext:
            ext_clean = ext.lstrip('.').lower()
            if ext_clean not in ('csv', 'json'):
                print("Unsupported extension. Use .csv or .json, or leave empty to auto-name.")
                continue
            return name_in  # keep as provided

        # No extension provided -> ask for format
        fmt_choice = input("Choose output format: [1] csv (default)  [2] json : ").strip()
        if fmt_choice == '2' or fmt_choice.lower() in ('json', 'j'):
            fmt = 'json'
        else:
            fmt = 'csv'
        filename = f"{name_in}.{fmt}"
        return filename


def run_scan(target_ip, ports, threads=100, timeout=1.0, save_path=None):
    """
    Scan ports in parallel and optionally save results to CSV or JSON depending on save_path extension.

    Returns list of open ports (ints).
    """
    if not ports:
        print("[!] No ports to scan.")
        return []

    total = len(ports)
    print(f"\n[+] Starting scan: {target_ip} — {total} ports — threads={threads} timeout={timeout}")
    open_ports = []
    results = []  # list of dicts for JSON or CSV output
    start_time = datetime.now()

    max_workers = min(max(1, threads), total)

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        future_map = {ex.submit(scan_port, target_ip, p, timeout): p for p in ports}
        try:
            for future in as_completed(future_map):
                p = future_map[future]
                try:
                    port, is_open = future.result()
                    status = "open" if is_open else "closed"
                except Exception:
                    port = p
                    status = "closed"

                if status == "open":
                    print(f"[+] Port {port} OPEN")
                    open_ports.append(port)

                results.append({
                    "host": target_ip,
                    "ip": target_ip,
                    "port": port,
                    "status": status,
                    "scanned_at": datetime.now().isoformat()
                })
        except KeyboardInterrupt:
            print("\n[!] Scan interrupted by user.")
            return open_ports

    elapsed = (datetime.now() - start_time).total_seconds()
    print("\n--- Scan complete ---")
    print(f"Open ports ({len(open_ports)}): {', '.join(map(str, open_ports)) if open_ports else 'None'}")
    print(f"Elapsed: {elapsed:.2f}s")

    # Save results if requested
    if save_path:
        _, ext = os.path.splitext(save_path)
        ext = ext.lstrip('.').lower()
        try:
            if ext == 'json':
                with open(save_path, 'w', encoding='utf-8') as fh:
                    json.dump(results, fh, indent=2, ensure_ascii=False)
                print(f"[+] Results saved to {save_path} (JSON)")
            else:
                # default/CSV
                with open(save_path, 'w', newline='', encoding='utf-8') as fh:
                    writer = csv.writer(fh)
                    writer.writerow(["host", "ip", "port", "status", "scanned_at"])
                    for row in results:
                        writer.writerow([row["host"], row["ip"], row["port"], row["status"], row["scanned_at"]])
                print(f"[+] Results saved to {save_path} (CSV)")
        except Exception as e:
            print(f"[!] Failed to write output file: {e}")

    return open_ports


def parse_ports_input(spec):
    """
    Parse a string like '22,80,8000-8100' into a sorted list of unique ports.
    Returns None on invalid input.
    """
    if not spec:
        return None
    ports = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            try:
                a_str, b_str = part.split("-", 1)
                a = int(a_str); b = int(b_str)
                if a < 1 or b > 65535 or a > b:
                    return None
                for p in range(a, b + 1):
                    ports.add(p)
            except Exception:
                return None
        else:
            try:
                p = int(part)
                if 1 <= p <= 65535:
                    ports.add(p)
                else:
                    return None
            except Exception:
                return None
    return sorted(ports)


def resolve_host(host):
    """Resolve hostname to IP. Return IP string or None on failure."""
    try:
        ip = socket.gethostbyname(host)
        return ip
    except Exception:
        return None


def prompt_int(prompt, default=None, minv=None, maxv=None):
    """Prompt user for integer input with optional default and range validation."""
    while True:
        s = input(prompt).strip()
        if s == "" and default is not None:
            return default
        try:
            v = int(s)
            if minv is not None and v < minv:
                print("Value is below minimum.")
                continue
            if maxv is not None and v > maxv:
                print("Value is above maximum.")
                continue
            return v
        except ValueError:
            print("Please enter a valid integer.")


def input_host():
    """Prompt user to enter a hostname or IP, resolve it, or accept 'q' to quit."""
    while True:
        host = input("\nEnter target (hostname or IP) or 'q' to cancel: ").strip()
        if not host:
            continue
        if host.lower() in ('q', 'quit', 'exit'):
            return None
        ip = resolve_host(host)
        if ip:
            return host, ip
        else:
            print("[!] Could not resolve host. Try again or type 'q' to cancel.")


def scanner_submenu(hostname, ip):
    """Scanner submenu for the resolved target host."""
    while True:
        clear_screen()
        print_banner("PORT SCANNER", font="slant")
        print(f"\nTarget: {hostname} ({ip})")
        print("1) Scan ALL ports (1-65535)  [CAUTION: heavy]")
        print("2) Scan common ports")
        print("3) Scan a RANGE of ports (e.g. 1000-2000)")
        print("4) Scan SPECIFIC ports (e.g. 22,80,8000-8100)")
        print("5) Back (change target)")
        print("6) Exit")
        choice = input("Select [1-6]: ").strip()
        if choice == '1':
            confirm = input("Scan ALL ports (1-65535)? This is heavy. Type 'yes' to confirm: ").strip().lower()
            if confirm != 'yes':
                continue
            threads = prompt_int("Threads (default 200): ", default=200, minv=1, maxv=2000)
            try:
                timeout = float(input("Timeout seconds (default 1.0): ").strip() or "1.0")
            except ValueError:
                timeout = 1.0
            out = choose_output_filename(hostname)
            ports = list(range(1, 65536))
            run_scan(ip, ports, threads=threads, timeout=timeout, save_path=out)
            input("\nPress Enter to return to scanner menu...")
        elif choice == '2':
            print(f"Common ports: {', '.join(map(str, COMMON_PORTS))}")
            threads = prompt_int("Threads (default 100): ", default=100, minv=1, maxv=2000)
            try:
                timeout = float(input("Timeout seconds (default 1.0): ").strip() or "1.0")
            except ValueError:
                timeout = 1.0
            out = choose_output_filename(hostname)
            run_scan(ip, COMMON_PORTS, threads=threads, timeout=timeout, save_path=out)
            input("\nPress Enter to return to scanner menu...")
        elif choice == '3':
            rng = input("Enter range as start-end (e.g. 1000-2000): ").strip()
            if '-' not in rng:
                print("Invalid format. Use start-end.")
                input("\nPress Enter to return to scanner menu...")
                continue
            try:
                a_str, b_str = rng.split("-", 1)
                a = int(a_str); b = int(b_str)
                if a < 1 or b > 65535 or a > b:
                    print("Invalid range values.")
                    input("\nPress Enter to return to scanner menu...")
                    continue
                ports = list(range(a, b + 1))
            except Exception:
                print("Invalid numbers.")
                input("\nPress Enter to return to scanner menu...")
                continue
            threads = prompt_int("Threads (default 200): ", default=200, minv=1, maxv=2000)
            try:
                timeout = float(input("Timeout seconds (default 1.0): ").strip() or "1.0")
            except ValueError:
                timeout = 1.0
            out = choose_output_filename(hostname)
            run_scan(ip, ports, threads=threads, timeout=timeout, save_path=out)
            input("\nPress Enter to return to scanner menu...")
        elif choice == '4':
            spec = input("Enter ports (comma separated, ranges allowed): ").strip()
            parsed = parse_ports_input(spec)
            if parsed is None:
                print("Invalid ports specification.")
                input("\nPress Enter to return to scanner menu...")
                continue
            threads = prompt_int("Threads (default 100): ", default=100, minv=1, maxv=2000)
            try:
                timeout = float(input("Timeout seconds (default 1.0): ").strip() or "1.0")
            except ValueError:
                timeout = 1.0
            out = choose_output_filename(hostname)
            run_scan(ip, parsed, threads=threads, timeout=timeout, save_path=out)
            input("\nPress Enter to return to scanner menu...")
        elif choice == '5':
            return  # back to host selection
        elif choice == '6':
            print("Exiting. Goodbye.")
            sys.exit(0)
        else:
            print("Invalid choice. Enter a number between 1 and 6.")
            input("\nPress Enter to continue...")


def main_menu():
    """Main landing menu with banner and three options: Run Scanner, Contact, Exit."""
    while True:
        clear_screen()
        print_banner("PORT SCANNER", font="slant")
        print(f"Version: {__version__}    Build date: {__build_date__}")
        print("=== Welcome to Simple CLI Port Scanner ===")
        print("\nMain Menu:")
        print("1) Run Scanner")
        print("2) Contact / About")
        print("3) Exit")
        choice = input("Select [1-3]: ").strip()
        if choice == '1':
            host_entry = input_host()
            if host_entry is None:
                continue
            hostname, ip = host_entry
            scanner_submenu(hostname, ip)
        elif choice == '2':
            clear_screen()
            print_banner("CONTACT", font="small")
            print("\nContact Information:")
            print(f"Name:      {CONTACT_INFO.get('name')}")
            print(f"Email:     {CONTACT_INFO.get('email')}")
            print(f"GitHub:    {CONTACT_INFO.get('github')}")
            print(f"Telegram:  {CONTACT_INFO.get('telegram')}")
            print(f"Instagram: {CONTACT_INFO.get('instagram')}")
            print(f"X:         {CONTACT_INFO.get('x')}")
            input("\nPress Enter to return to main menu...")
        elif choice == '3':
            clear_screen()
            print("Goodbye.")
            return
        else:
            print("Invalid choice. Enter 1, 2 or 3.")
            input("\nPress Enter to continue...")


if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")
        sys.exit(0)
