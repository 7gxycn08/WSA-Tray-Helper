from PyQt5.QtWidgets import QMenu, QSystemTrayIcon,QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
from tkinter import messagebox
import sys
import psutil
import subprocess
from pathlib import Path
import os
script_path = Path(__file__).parent.absolute()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

res_path = resource_path(script_path)

def Tray_Icon():
    def close_tray_icon():
        app.exit()

    def startWSA():
        try:
            subprocess.Popen("WsaClient /launch wsa://system", creationflags=subprocess.CREATE_NO_WINDOW)
        except:
            messagebox.showerror(title="Error",message="WSA Not Running or Not Installed.")

    def stopWSA():
        subprocess.Popen("taskkill /im WsaClient.exe /F", creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.Popen("taskkill /im WsaService.exe /F", creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.Popen("taskkill /im GSKServer.exe /F", creationflags=subprocess.CREATE_NO_WINDOW)
        messagebox.showinfo(title="WSA Stopped", message="WSA Processes Terminated")

    def check_process():
        process = "WsaClient.exe" in (p.name() for p in psutil.process_iter())
        if process == False:
            tray_icon.setIcon(QIcon(f"{res_path}\\Resources\\stop.ico"))
            tray_icon.setToolTip("WSA Not Running")
        if process == True:
            tray_icon.setIcon(QIcon(f"{res_path}\\Resources\\Icon1.ico"))
            tray_icon.setToolTip("WSA Running")

    app = QApplication(sys.argv)
    tray_icon = QSystemTrayIcon()
    tray_icon.setToolTip("WSA Tray Helper")
    tray_icon.setIcon(QIcon(f"{res_path}\\Resources\\Icon1.ico"))
    timer = QTimer()
    timer.timeout.connect(check_process)
    timer.start(5000)  # 5 seconds
    menu = QMenu()
    menu.addAction("Start WSA").triggered.connect(lambda: startWSA())
    menu.addAction("Stop WSA").triggered.connect(lambda: stopWSA())
    menu.addAction("Exit").triggered.connect(lambda: close_tray_icon())
    tray_icon.setContextMenu(menu)
    tray_icon.show()
    app.exec_()

if __name__ == '__main__':
    Tray_Icon()
