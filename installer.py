"""
Speedify Installer
Installs the app to %LOCALAPPDATA%/Speedify, creates shortcuts,
and registers with Windows Programs & Features.
"""
import os
import sys
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import winreg

APP_NAME    = "Speedify"
APP_VERSION = "1.0"
APP_DESC    = "Network Speed Monitor"
EXE_NAME    = "speedify.exe"

INSTALL_DIR = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), APP_NAME)
REG_KEY     = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\Speedify"


def _bundled_exe():
    """Locate the bundled speedify.exe (works both frozen and plain)."""
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, EXE_NAME)


def _make_shortcut(target, lnk_path, description=""):
    """Create a .lnk shortcut via PowerShell."""
    ps = (
        f"$ws = New-Object -ComObject WScript.Shell; "
        f"$s = $ws.CreateShortcut('{lnk_path}'); "
        f"$s.TargetPath = '{target}'; "
        f"$s.WorkingDirectory = '{os.path.dirname(target)}'; "
        f"$s.Description = '{description}'; "
        f"$s.Save()"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
        capture_output=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def _register_uninstall(install_dir, uninstall_cmd):
    """Add entry to Windows Programs & Features."""
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_KEY)
        vals = {
            "DisplayName":    (winreg.REG_SZ,    APP_NAME),
            "DisplayVersion": (winreg.REG_SZ,    APP_VERSION),
            "Publisher":      (winreg.REG_SZ,    APP_NAME),
            "InstallLocation":(winreg.REG_SZ,    install_dir),
            "UninstallString":(winreg.REG_SZ,    uninstall_cmd),
            "NoModify":       (winreg.REG_DWORD, 1),
            "NoRepair":       (winreg.REG_DWORD, 1),
        }
        for name, (kind, val) in vals.items():
            winreg.SetValueEx(key, name, 0, kind, val)
        winreg.CloseKey(key)
    except Exception:
        pass


def _write_uninstaller(install_dir):
    """Write uninstall.bat to the install directory."""
    bat = os.path.join(install_dir, "uninstall.bat")
    start_menu = os.path.join(
        os.environ.get('APPDATA', ''),
        r'Microsoft\Windows\Start Menu\Programs',
        f'{APP_NAME}.lnk',
    )
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop', f'{APP_NAME}.lnk')
    content = f"""@echo off
taskkill /IM {EXE_NAME} /F >nul 2>&1
del "{start_menu}" >nul 2>&1
del "{desktop}" >nul 2>&1
reg delete "HKCU\\{REG_KEY}" /f >nul 2>&1
echo Uninstalling {APP_NAME}...
start /b "" cmd /c "ping -n 3 127.0.0.1 >nul && rd /s /q \\"{install_dir}\\""
echo {APP_NAME} has been removed.
"""
    with open(bat, 'w') as f:
        f.write(content)
    return bat


# ── Installer GUI ────────────────────────────────────────────────────────────

BG    = "#1a1a1a"
CARD  = "#222222"
TEAL  = "#00D4AA"
WHITE = "#FFFFFF"
DIM   = "#888888"


class InstallerApp:
    def __init__(self, root):
        self.root = root
        root.title(f"{APP_NAME} Setup")
        root.geometry("420x300")
        root.resizable(False, False)
        root.configure(bg=BG)

        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"420x300+{(sw-420)//2}+{(sh-300)//2}")

        # Try to set icon if available
        ico = _bundled_exe().replace(EXE_NAME, "network_icon.ico")
        try:
            if os.path.exists(ico):
                root.iconbitmap(ico)
        except Exception:
            pass

        # Header
        tk.Label(root, text=APP_NAME, font=("Segoe UI", 26, "bold"),
                 bg=BG, fg=TEAL).pack(pady=(22, 2))
        tk.Label(root, text=APP_DESC, font=("Segoe UI", 11),
                 bg=BG, fg=DIM).pack()
        tk.Label(root, text=f"Version {APP_VERSION}", font=("Segoe UI", 9),
                 bg=BG, fg="#555555").pack(pady=(2, 12))

        # Install path
        tk.Label(root, text=f"Install location:  {INSTALL_DIR}",
                 font=("Segoe UI", 9), bg=BG, fg=DIM).pack()

        # Desktop shortcut checkbox
        self._desktop = tk.BooleanVar(value=True)
        tk.Checkbutton(root, text="Create Desktop shortcut",
                       variable=self._desktop,
                       bg=BG, fg=WHITE, selectcolor=CARD,
                       activebackground=BG, activeforeground=WHITE,
                       font=("Segoe UI", 10)).pack(pady=(10, 0))

        # Progress bar (styled)
        style = ttk.Style()
        style.theme_use('default')
        style.configure("green.Horizontal.TProgressbar",
                        troughcolor=CARD, background=TEAL,
                        darkcolor=TEAL, lightcolor=TEAL, bordercolor=CARD)
        self.pb = ttk.Progressbar(root, length=380, mode='determinate',
                                  style="green.Horizontal.TProgressbar")
        self.pb.pack(pady=(14, 4), padx=20)

        self.status = tk.Label(root, text="Ready to install.",
                               font=("Segoe UI", 9), bg=BG, fg=DIM)
        self.status.pack()

        # Install button
        self.btn = tk.Button(root, text="  Install  ",
                             font=("Segoe UI", 13, "bold"),
                             bg=TEAL, fg="#000000", borderwidth=0,
                             padx=20, pady=6, cursor="hand2",
                             command=self._start,
                             activebackground="#00b894",
                             activeforeground="#000000")
        self.btn.pack(pady=14)

        tk.Label(root, text=f"© 2025 {APP_NAME}", font=("Segoe UI", 8),
                 bg=BG, fg="#444444").pack(side=tk.BOTTOM, pady=6)

    def _set(self, text, pct=None):
        self.status.config(text=text)
        if pct is not None:
            self.pb['value'] = pct
        self.root.update_idletasks()

    def _start(self):
        self.btn.config(state='disabled')
        threading.Thread(target=self._install, daemon=True).start()

    def _install(self):
        try:
            self.root.after(0, self._set, "Creating install directory…", 10)
            os.makedirs(INSTALL_DIR, exist_ok=True)

            self.root.after(0, self._set, "Copying files…", 35)
            dst_exe = os.path.join(INSTALL_DIR, EXE_NAME)
            shutil.copy2(_bundled_exe(), dst_exe)

            self.root.after(0, self._set, "Writing uninstaller…", 50)
            bat = _write_uninstaller(INSTALL_DIR)

            self.root.after(0, self._set, "Creating Start Menu shortcut…", 65)
            start_menu_lnk = os.path.join(
                os.environ.get('APPDATA', ''),
                r'Microsoft\Windows\Start Menu\Programs',
                f'{APP_NAME}.lnk',
            )
            _make_shortcut(dst_exe, start_menu_lnk, APP_DESC)

            if self._desktop.get():
                self.root.after(0, self._set, "Creating Desktop shortcut…", 78)
                desktop_lnk = os.path.join(
                    os.path.expanduser('~'), 'Desktop', f'{APP_NAME}.lnk'
                )
                _make_shortcut(dst_exe, desktop_lnk, APP_DESC)

            self.root.after(0, self._set, "Registering with Windows…", 90)
            _register_uninstall(INSTALL_DIR, f'"{bat}"')

            self.root.after(0, self._set, "Done!", 100)
            self.root.after(0, self._success, dst_exe)

        except Exception as exc:
            self.root.after(0, messagebox.showerror, "Error", str(exc))
            self.root.after(0, lambda: self.btn.config(state='normal'))

    def _success(self, exe_path):
        messagebox.showinfo(
            "Installation Complete",
            f"{APP_NAME} has been installed!\n\n"
            "• Start Menu shortcut created\n"
            "• Find it in Settings → Apps to uninstall\n\n"
            "Click OK to launch.",
        )
        try:
            subprocess.Popen([exe_path])
        except Exception:
            pass
        self.root.destroy()


def main():
    root = tk.Tk()
    InstallerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
