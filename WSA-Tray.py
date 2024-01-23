from PyQt5.QtWidgets import QMenu, QSystemTrayIcon, QApplication, QMessageBox, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, QSettings
import sys
import subprocess
import ctypes
import win32com.client
from datetime import datetime, timedelta
import os

class SystemTrayApp():
    def __init__(self):
        super().__init__()
        self.boot_tick_status = None
        self.script_path = f"{os.path.abspath(sys.argv[0])}"
        self.task_name = "WSA-Tray-Helper"
        self.process_name = "WsaClient.exe"

        self.app = QApplication(sys.argv)
        self.settings = QSettings("7gxycn08@Github", "WSA-Tray-Helper")
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setToolTip("WSA Tray Helper")
        self.tray_icon.setIcon(QIcon(f"dependancies\\Resources\\Icon1.ico"))
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_process)
        self.timer.start(5000)  # 5 seconds
        self.menu = QMenu()
        self.start_at_boot_action = QAction('Start at Boot', self.menu)
        self.start_at_boot_action.setCheckable(True)
        self.start_at_boot_action.setChecked(self.settings.value("start_at_boot", False, type=bool))
        self.start_at_boot_action.triggered.connect(self.initiate_task)
        self.menu.addAction(self.start_at_boot_action)
        self.menu.addAction(QIcon(f"dependancies\\Resources\\Icon1.ico"),"Start WSA").triggered.connect(self.startwsa)
        self.menu.addAction(QIcon(f"dependancies\\Resources\\stop.ico"),"Stop WSA").triggered.connect(self.stopwsa)
        self.menu.addSeparator()
        (self.menu.addAction(QIcon(f"dependancies\\Resources\\folder.ico"), "WSA Files")
         .triggered.connect(lambda: self.open_wsafiles()))
        (self.menu.addAction(QIcon(f"dependancies\\Resources\\settings.ico"), "WSA Settings")
         .triggered.connect(lambda: self.open_wsasettings()))
        (self.menu.addAction(QIcon(f"dependancies\\Resources\\android.ico"), "Android Settings")
         .triggered.connect(lambda: self.open_androidsettings()))
        self.menu.addSeparator()
        self.menu.addAction(QIcon(f"dependancies\\Resources\\about.ico"), "About").triggered.connect(
            self.about_function)
        self.menu.addAction(QIcon(f"dependancies\\Resources\\exit.ico"),"Exit").triggered.connect(
            self.exit_application)
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()
        self.run_initially_at_start()
        self.app.exec_()

    def exit_application(self):
        self.app.exit(0)
    def startwsa(self):
        try:
            subprocess.Popen("WSAClient.exe /launch wsa://system",
                             shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except:
            QMessageBox.warning(parent=None, title=f"WSA Not Running or Not Installed.", buttons=QMessageBox.Ok)

    def stopwsa(self):
        subprocess.Popen("WSAClient.exe /shutdown", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.Popen("taskkill /F /IM vmcompute.exe", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.Popen("taskkill /F /IM WSACrashUploader.exe", shell=True,
                         creationflags=subprocess.CREATE_NO_WINDOW)

    def open_wsasettings(self):
        subprocess.Popen("start wsa-settings://", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

    def open_wsafiles(self):
        subprocess.Popen("WSAClient.exe /launch wsa://com.android.documentsui",
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

    def open_androidsettings(self):
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
            QMessageBox.warning(parent=None, title="Error", text=f"An error occurred: {str(e)}", buttons=QMessageBox.Ok)

    def check_process(self):
        try:
            checked_process = self.is_process_running()
            if checked_process:
                self.tray_icon.setIcon(QIcon(f"dependancies\\Resources\\Icon1.ico"))
                self.tray_icon.setToolTip("WSA Running")
            else:
                self.tray_icon.setIcon(QIcon(f"dependancies\\Resources\\stop.ico"))
                self.tray_icon.setToolTip("WSA Not Running")
        except:
            QMessageBox.warning(parent=None, title="Error",
                                text=f"Error occurred while checking the process {self.process_name}.",
                                buttons=QMessageBox.Ok)

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
            QMessageBox.warning(parent=None, title="Error", text=f"Task installation failed: {e}", buttons=QMessageBox.Ok)

    def register_as_task(self):
        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()

            rootFolder = scheduler.GetFolder('\\')

            taskDef = scheduler.NewTask(0)
            taskDef.RegistrationInfo.Description = 'Start WSA-Tray-Helper at Boot'

            trigger = taskDef.Triggers.Create(1)
            trigger.Id = 'LogonTriggerId'

            start_time = datetime.now() + timedelta(minutes=1)
            trigger.StartBoundary = start_time.isoformat()

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
            QMessageBox.warning(parent=None,title="Error", text=f"Task installation failed: {e}", buttons=QMessageBox.Ok)

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
                QMessageBox.warning(parent=None,
                                    title="Error", text=f'Error removing task "{self.task_name}": {str(e)}',
                                    buttons=QMessageBox.Ok)

        except Exception as e:
            QMessageBox.warning(parent=None, title="Error", text=f'Error connecting to Task Scheduler: {str(e)}',
                                buttons=QMessageBox.Ok)

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
            QMessageBox.warning(parent=None,title="Error", text=f"Exception in run_initially {e}",
                                buttons=QMessageBox.Ok)

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
            QMessageBox.warning(parent=None,title="Error", text=f"An exception occurred: {e}", buttons=QMessageBox.Ok)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    tray_app = SystemTrayApp()
    sys.exit(tray_app.exit_application())