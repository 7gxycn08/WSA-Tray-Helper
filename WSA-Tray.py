from PyQt6.QtWidgets import QMenu, QSystemTrayIcon, QApplication, QMessageBox
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer, QSettings, Qt
import sys
import subprocess
import ctypes
import win32com.client
import os


class SystemTrayApp:
    def __init__(self):
        super().__init__()
        self.exception_msg = None
        self.boot_tick_status = None
        self.script_path = f"{os.path.abspath(sys.argv[0])}"
        self.task_name = "WSA-Tray-Helper"
        self.process_name = "WsaClient.exe"

        self.app = QApplication(sys.argv)
        self.settings = QSettings("7gxycn08@Github", "WSA-Tray-Helper")
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setToolTip("WSA Tray Helper")
        self.tray_icon.setIcon(QIcon(r"dependancies/Resources/Icon1.ico"))
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_process)
        self.timer.start(5000)  # 5 seconds
        self.menu = QMenu()
        self.menu.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.menu.setWindowFlags(self.menu.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.start_at_boot_action = QAction('Start at Boot', self.menu)
        self.start_at_boot_action.setCheckable(True)
        self.start_at_boot_action.setChecked(self.settings.value("start_at_boot", False, type=bool))
        self.start_at_boot_action.triggered.connect(self.initiate_task)
        self.menu.addAction(self.start_at_boot_action)
        self.menu.addAction(QIcon(r"dependancies/Resources/Icon1.ico"), "Start WSA").triggered.connect(self.start_wsa)
        self.menu.addAction(QIcon(r"dependancies/Resources/stop.ico"), "Stop WSA").triggered.connect(self.stop_wsa)
        self.menu.addSeparator()
        (self.menu.addAction(QIcon(r"dependancies/Resources/folder.ico"), "WSA Files")
         .triggered.connect(lambda: self.open_wsa_files()))
        (self.menu.addAction(QIcon(r"dependancies/Resources/settings.ico"), "WSA Settings")
         .triggered.connect(lambda: self.open_wsa_settings()))
        (self.menu.addAction(QIcon(r"dependancies/Resources/android.ico"), "Android Settings")
         .triggered.connect(lambda: self.open_android_settings()))
        self.menu.addSeparator()
        self.menu.addAction(QIcon(r"dependancies/Resources/about.ico"), "About").triggered.connect(
            self.about_function)
        self.menu.addAction(QIcon(r"dependancies/Resources/exit.ico"), "Exit").triggered.connect(
            self.exit_application)
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()
        self.run_initially_at_start()
        with open('custom.css', 'r') as file:
            self.menu.setStyleSheet(file.read())
        self.app.exec()

    def exit_application(self):
        self.app.exit(0)

    def start_wsa(self):
        try:
            subprocess.Popen("WSAClient.exe /launch wsa://system",
                             shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except:
            QMessageBox.warning(parent=None, title=f"WSA Not Running or Not Installed.",
                                buttons=QMessageBox.StandardButton.Ok)

    def stop_wsa(self):
        subprocess.Popen("WSAClient.exe /shutdown", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.Popen("taskkill /F /IM vmcompute.exe", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.Popen("taskkill /F /IM WSACrashUploader.exe", shell=True,
                         creationflags=subprocess.CREATE_NO_WINDOW)

    def open_wsa_settings(self):
        subprocess.Popen("start wsa-settings://", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

    def open_wsa_files(self):
        subprocess.Popen("WSAClient.exe /launch wsa://com.android.documentsui",
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

    def open_android_settings(self):
        subprocess.Popen("WSAClient.exe /launch wsa://com.android.settings",
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

    def about_function(self):
        subprocess.Popen("start https://github.com/7gxycn08/WSA-Tray-Helper",
                         shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)

    def is_process_running(self):
        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_VM_READ = 0x0010
        try:
            processes = (ctypes.c_ulong * 2048)()
            cb = ctypes.c_ulong(ctypes.sizeof(processes))
            ctypes.windll.psapi.EnumProcesses(ctypes.byref(processes), cb, ctypes.byref(cb))

            process_count = cb.value // ctypes.sizeof(ctypes.c_ulong)
            for i in range(process_count):
                process_id = processes[i]
                process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                                                                    False,
                                                                    process_id)

                if process_handle:
                    buffer_size = 260
                    buffer = ctypes.create_unicode_buffer(buffer_size)
                    ctypes.windll.psapi.GetModuleBaseNameW(process_handle, 0, buffer, ctypes.sizeof(buffer))
                    process_name_actual = buffer.value.lower()
                    ctypes.windll.kernel32.CloseHandle(process_handle)
                    if process_name_actual == self.process_name.lower():
                        return True
            return False

        except Exception as e:
            self.exception_msg = f"An error occurred: {e}"
            self.show_msg_box()

    def check_process(self):
        checked_process = self.is_process_running()
        if checked_process:
            self.tray_icon.setIcon(QIcon(r"dependancies/Resources/Icon1.ico"))
            self.tray_icon.setToolTip("WSA Running")
        else:
            self.tray_icon.setIcon(QIcon(r"dependancies/Resources/stop.ico"))
            self.tray_icon.setToolTip("WSA Not Running")

    def toggle_start_at_boot(self):
        checked = self.start_at_boot_action.isChecked()
        self.settings.setValue("start_at_boot", checked)

    def is_task_installed(self):
        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()

            root_folder = scheduler.GetFolder('\\')

            try:
                task = root_folder.GetTask(self.task_name)
                return True
            except Exception:
                return False
        except Exception as e:
            self.exception_msg = f"Task installation failed: {e}"
            self.show_msg_box()

    def register_as_task(self):
        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()

            rootFolder = scheduler.GetFolder('\\')

            taskDef = scheduler.NewTask(0)
            taskDef.RegistrationInfo.Description = 'Start WSA-Tray-Helper at Boot'

            trigger = taskDef.Triggers.Create(9)
            trigger.Id = 'LogonTriggerId'

            execAction = taskDef.Actions.Create(0)
            execAction.Path = self.script_path
            execAction.WorkingDirectory = os.getcwd()

            principal = taskDef.Principal
            principal.UserId = os.getlogin()
            principal.RunLevel = 1
            principal.LogonType = 3

            taskDef.Settings.ExecutionTimeLimit = 'PT0S'

            rootFolder.RegisterTaskDefinition(
                self.task_name,
                taskDef,
                6,
                None,
                None,
                3
            )
            self.start_at_boot_action.setChecked(True)
            self.toggle_start_at_boot()
            self.boot_tick_status = True
        except Exception as e:
            self.exception_msg = f"Task installation failed: {e}"
            self.show_msg_box()

    def remove_task(self):
        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            root_folder = scheduler.GetFolder('\\')
            try:
                task = root_folder.GetTask(self.task_name)
                root_folder.DeleteTask(self.task_name, 0)
                self.start_at_boot_action.setChecked(False)
                self.toggle_start_at_boot()
                self.boot_tick_status = False

            except Exception as e:
                self.exception_msg = f"Error removing task: {self.task_name} {e}"
                self.show_msg_box()

        except Exception as e:
            self.exception_msg = f"Error connecting to Task Scheduler: {self.task_name} {e}"
            self.show_msg_box()

    def run_initially_at_start(self):
        try:
            if self.is_task_installed() == True:
                self.start_at_boot_action.setChecked(True)
                self.toggle_start_at_boot()
                self.boot_tick_status = True
            else:
                self.start_at_boot_action.setChecked(False)
                self.toggle_start_at_boot()
                self.boot_tick_status = False
        except Exception as e:
            self.exception_msg = f"run_initially {e}"
            self.show_msg_box()

    def initiate_task(self):
        try:
            if self.boot_tick_status:
                self.remove_task()
                self.start_at_boot_action.setChecked(False)
                self.toggle_start_at_boot()
            else:
                self.register_as_task()
                self.start_at_boot_action.setChecked(True)
                self.toggle_start_at_boot()
        except Exception as e:
            self.exception_msg = f"initiate_task {e}"
            self.show_msg_box()

    def show_msg_box(self):
        warning_message_box = QMessageBox()
        warning_message_box.setWindowTitle("WSA-Tray Error")
        warning_message_box.setWindowIcon(QIcon(r"dependancies/Resources/Icon1.ico"))
        warning_message_box.setFixedSize(400, 200)
        warning_message_box.setIcon(QMessageBox.Icon.Critical)
        warning_message_box.setText(f"{self.exception_msg}")
        warning_message_box.exec()


if __name__ == '__main__':
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    app = QApplication(sys.argv)
    tray_app = SystemTrayApp()
    sys.exit(tray_app.exit_application())
