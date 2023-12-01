from PyQt5.QtWidgets import QMenu, QSystemTrayIcon,QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
from tkinter import messagebox
import sys
import subprocess

def Tray_Icon():
    def close_tray_icon():
        app.exit()

    def startWSA():
        try:
            subprocess.Popen("WSAClient.exe /launch wsa://system",
                             shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except:
            messagebox.showerror(title="Error",message="WSA Not Running or Not Installed.")

    def stopWSA():
        subprocess.Popen("WSAClient.exe /shutdown", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        messagebox.showinfo(title="WSA Stopped", message="WSA Gracefully Exited.")

    def open_WSASettings():
        subprocess.Popen("start wsa-settings://", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

    def open_WSAFiles():
        subprocess.Popen("WSAClient.exe /launch wsa://com.android.documentsui",
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    def open_AndroidSettings():
        subprocess.Popen("WSAClient.exe /launch wsa://com.android.settings",
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    def about_Function():
        subprocess.Popen("start https://github.com/7gxycn08/WSA-Tray-Helper",
                         shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
    def check_process():
        process_name = "WsaClient.exe"
        try:
            result = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {process_name}'],
                                    capture_output=True, text=True,
                                    check=True,creationflags=subprocess.CREATE_NO_WINDOW)
            if process_name.lower() in result.stdout.lower():
                tray_icon.setIcon(QIcon(f"dependancies\\Resources\\Icon1.ico"))
                tray_icon.setToolTip("WSA Running")
            else:
                tray_icon.setIcon(QIcon(f"dependancies\\Resources\\stop.ico"))
                tray_icon.setToolTip("WSA Not Running")
        except subprocess.CalledProcessError:
            messagebox.showerror(title="Error",message="Error occurred while checking the process {process_name}.")

    app = QApplication(sys.argv)
    tray_icon = QSystemTrayIcon()
    tray_icon.setToolTip("WSA Tray Helper")
    tray_icon.setIcon(QIcon(f"dependancies\\Resources\\Icon1.ico"))
    timer = QTimer()
    timer.timeout.connect(check_process)
    timer.start(5000)  # 5 seconds
    menu = QMenu()
    menu.addAction(QIcon(f"dependancies\\Resources\\Icon1.ico"),"Start WSA").triggered.connect(lambda: startWSA())
    menu.addAction(QIcon(f"dependancies\\Resources\\stop.ico"),"Stop WSA").triggered.connect(lambda: stopWSA())
    menu.addSeparator()
    (menu.addAction(QIcon(f"dependancies\\Resources\\folder.ico"), "WSA Files")
     .triggered.connect(lambda: open_WSAFiles()))
    (menu.addAction(QIcon(f"dependancies\\Resources\\settings.ico"), "WSA Settings")
     .triggered.connect(lambda: open_WSASettings()))
    (menu.addAction(QIcon(f"dependancies\\Resources\\android.ico"), "Android Settings")
     .triggered.connect(lambda: open_AndroidSettings()))
    menu.addSeparator()
    menu.addAction(QIcon(f"dependancies\\Resources\\about.ico"), "About").triggered.connect(lambda: about_Function())
    menu.addAction(QIcon(f"dependancies\\Resources\\exit.ico"),"Exit").triggered.connect(lambda: close_tray_icon())
    tray_icon.setContextMenu(menu)
    tray_icon.show()
    app.exec_()

if __name__ == '__main__':
    Tray_Icon()
