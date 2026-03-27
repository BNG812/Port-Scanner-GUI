import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socket
import threading
from datetime import datetime

# --- SETTINGS ---
THEME_BG = "#0a0a0a"       # Deep Black
THEME_FG = "#00ff41"       # Matrix Green
THEME_ACCENT = "#1a1a1a"   # Dark Gray
FONT_MAIN = ("Consolas", 11)
FONT_BOLD = ("Consolas", 14, "bold")

COMMON_PORTS = {21:"FTP", 22:"SSH", 23:"Telnet", 25:"SMTP", 53:"DNS", 80:"HTTP",
                110:"POP3", 143:"IMAP", 443:"HTTPS", 3306:"MySQL", 5432:"PostgreSQL",
                8080:"HTTP-Proxy"}

def scan_port(target_ip, port, results):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        if sock.connect_ex((target_ip, port)) == 0:
            service = COMMON_PORTS.get(port, "Unknown")
            results.append({"port": port, "service": service})
        sock.close()
    except:
        pass

def start_scan():
    target = entry_target.get().strip()
    if not target:
        messagebox.showerror("SYSTEM ERROR", "Target field null.")
        return

    try:
        target_ip = socket.gethostbyname(target)
    except:
        messagebox.showerror("NETWORK ERROR", "DNS Resolution Failed.")
        return

    try:
        start_p = int(entry_start.get() or 1)
        end_p = int(entry_end.get() or 1024)
    except:
        messagebox.showerror("VALUE ERROR", "Invalid port syntax.")
        return

    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"[>] INITIALIZING SCAN ON: {target} ({target_ip})...\n")
    result_text.insert(tk.END, f"[>] TIMESTAMP: {datetime.now().strftime('%H:%M:%S')}\n")
    result_text.insert(tk.END, "-"*65 + "\n")
    status_label.config(text="STATUS: SCAN_IN_PROGRESS...", fg="#ff9900")

    results = []
    threads = []

    def worker():
        for port in range(start_p, end_p + 1):
            t = threading.Thread(target=scan_port, args=(target_ip, port, results))
            threads.append(t)
            t.start()
            if len(threads) >= 150:
                for tt in threads: tt.join()
                threads.clear()

        for t in threads: t.join()

        # Display results in Terminal Style
        result_text.insert(tk.END, f"[+] SCAN COMPLETE\n")
        result_text.insert(tk.END, f"[+] OPEN PORTS IDENTIFIED: {len(results)}\n\n")
        result_text.insert(tk.END, f"{'PORT':<10} {'PROTOCOL':<15} {'STATUS'}\n")
        result_text.insert(tk.END, "="*65 + "\n")

        for r in sorted(results, key=lambda x: x['port']):
            result_text.insert(tk.END, f"{r['port']:<10} {r['service']:<15} [ACTIVE]\n")

        status_label.config(text="STATUS: SYSTEM_READY", fg=THEME_FG)

    threading.Thread(target=worker, daemon=True).start()

# --- GUI CONSTRUCTION ---
root = tk.Tk()
root.title("SENTINEL v1.0 | PORT_SCANNER")
root.geometry("900x750")
root.configure(bg=THEME_BG)

# Header
tk.Label(root, text="[ PROJECT SENTINEL ]", font=("Consolas", 22, "bold"),
         fg=THEME_FG, bg=THEME_BG).pack(pady=20)

# Input Container
input_frame = tk.Frame(root, bg=THEME_BG, highlightbackground=THEME_FG, highlightthickness=1)
input_frame.pack(pady=10, padx=40, fill="x")

# Labels & Entries
label_style = {"font": FONT_MAIN, "fg": THEME_FG, "bg": THEME_BG}
entry_style = {"font": FONT_MAIN, "bg": "#111", "fg": "#00ff00",
               "insertbackground": "white", "borderwidth": 1, "relief": "flat"}

tk.Label(input_frame, text="TARGET_HOST:", **label_style).grid(row=0, column=0, sticky="w", padx=10, pady=10)
entry_target = tk.Entry(input_frame, width=40, **entry_style)
entry_target.grid(row=0, column=1, padx=10, pady=10)
entry_target.insert(0, "scanme.nmap.org")

tk.Label(input_frame, text="START_PORT:", **label_style).grid(row=1, column=0, sticky="w", padx=10, pady=5)
entry_start = tk.Entry(input_frame, width=15, **entry_style)
entry_start.grid(row=1, column=1, sticky="w", padx=10, pady=5)
entry_start.insert(0, "1")

tk.Label(input_frame, text="END_PORT:", **label_style).grid(row=2, column=0, sticky="w", padx=10, pady=5)
entry_end = tk.Entry(input_frame, width=15, **entry_style)
entry_end.grid(row=2, column=1, sticky="w", padx=10, pady=5)
entry_end.insert(0, "1024")

# Execution Button
scan_btn = tk.Button(root, text="[ EXECUTE_SCAN ]", font=FONT_BOLD, bg=THEME_BG,
                     fg=THEME_FG, activebackground=THEME_FG, activeforeground=THEME_BG,
                     command=start_scan, borderwidth=1, relief="ridge", cursor="hand2")
scan_btn.pack(pady=20)

# Status Bar
status_label = tk.Label(root, text="STATUS: SYSTEM_READY", font=FONT_MAIN, fg=THEME_FG, bg=THEME_BG)
status_label.pack(pady=5)

# Scrolled Terminal Window
result_text = scrolledtext.ScrolledText(root, height=22, font=FONT_MAIN, bg="#050505",
                                        fg=THEME_FG, insertbackground="white",
                                        highlightthickness=1, highlightbackground="#333")
result_text.pack(padx=40, pady=10, fill="both", expand=True)

# Footer
tk.Label(root, text="RECON_TOOL // AUTH_USER: Manveer Singh // WEEK_4_INTERNSHIP",
         font=("Consolas", 8), fg="#444", bg=THEME_BG).pack(pady=10)

root.mainloop()