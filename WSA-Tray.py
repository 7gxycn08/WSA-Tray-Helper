from PyQt6.QtWidgets import QMenu, QSystemTrayIcon, QApplication, QMessageBox
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer, QSettings, Qt, pyqtSignal, QObject, QCoreApplication
from threading import Thread
import sys
import subprocess
import ctypes
import win32com.client
import os
import configparser
import time
import shutil
import winsound


class SystemTrayApp(QObject):
    finished = pyqtSignal()
    exception_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.thread_msg = None
        self.finished.connect(self.on_finished_show_msg, Qt.ConnectionType.QueuedConnection)
        self.exception_signal.connect(self.show_msg_box, Qt.ConnectionType.QueuedConnection)
        self.current_user = os.getlogin()
        self.ran_command = None
        self.exception_msg = None
        self.boot_tick_status = None
        self.script_path = f"{os.path.abspath(sys.argv[0])}"
        self.task_name = "WSA-Tray-Helper"
        self.process_name = "WsaClient.exe"

        self.settings = QSettings("7gxycn08@Github", "WSA-Tray-Helper")
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setToolTip("WSA Tray Helper")
        self.tray_icon.setIcon(QIcon(r"dependencies/Resources/Icon1.ico"))
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

        self.command_at_runtime_action = QAction('Custom Commands', self.menu)
        self.command_at_runtime_action.setCheckable(True)
        self.command_at_runtime_action.setChecked(self.settings.value("command_at_runtime", False, type=bool))
        self.command_at_runtime_action.triggered.connect(self.save_action_state)
        self.menu.addAction(self.command_at_runtime_action)

        self.menu.addAction(QIcon(r"dependencies/Resources/Icon1.ico"), "Start WSA").triggered.connect(self.start_wsa)
        self.menu.addAction(QIcon(r"dependencies/Resources/stop.ico"), "Stop WSA").triggered.connect(self.stop_wsa)
        self.menu.addSeparator()
        (self.menu.addAction(QIcon(r"dependencies/Resources/folder.ico"), "WSA Files")
         .triggered.connect(lambda: self.open_wsa_files()))
        (self.menu.addAction(QIcon(r"dependencies/Resources/settings.ico"), "WSA Settings")
         .triggered.connect(lambda: self.open_wsa_settings()))
        (self.menu.addAction(QIcon(r"dependencies/Resources/android.ico"), "Android Settings")
         .triggered.connect(lambda: self.open_android_settings()))
        self.menu.addSeparator()
        self.menu.addAction(QIcon(r"dependencies/Resources/backup.ico"), "Backup WSA").triggered.connect(
            lambda: Thread(target=self.wsa_backup, daemon=True).start())
        self.menu.addAction(QIcon(r"dependencies/Resources/restore.ico"), "Restore WSA").triggered.connect(
            lambda: Thread(target=self.wsa_restore, daemon=True).start())
        self.menu.addSeparator()
        self.menu.addAction(QIcon(r"dependencies/Resources/command.ico"), "Open Commands Config").triggered.connect(
            self.open_commands_file)
        self.menu.addAction(QIcon(r"dependencies/Resources/about.ico"), "About").triggered.connect(
            self.about_function)
        self.menu.addAction(QIcon(r"dependencies/Resources/exit.ico"), "Exit").triggered.connect(
            self.exit_application)
        self.tray_icon.setContextMenu(self.menu)
        self.run_initially_at_start()
        with open('dependencies/Resources/custom.css', 'r') as file:
            self.menu.setStyleSheet(file.read())
        self.config = configparser.ConfigParser()
        self.config.read(r'Dependencies\Commands.ini')
        self.list_str = self.config['ADB_COMMANDS']['at_start']
        self.commands_list = self.list_str.split(', ') if self.list_str else []
        self.ran_command = self.command_at_runtime_action.isEnabled()
        self.tray_icon.show()

    def on_finished_show_msg(self):
        message_box = QMessageBox()
        message_box.setWindowTitle("WSA-Tray-Helper")
        message_box.setWindowIcon(QIcon(r"dependencies/Resources/Icon1.ico"))
        message_box.setFixedSize(400, 200)
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setText(f"{self.thread_msg}")
        winsound.MessageBeep()
        message_box.exec()

    def wsa_backup(self):
        source_dir = (f"C:\\Users\\{self.current_user}\\AppData\\Local\\Packages"
                      "\\MicrosoftCorporationII.WindowsSubsystemForAndroid_8wekyb3d8bbwe\\LocalCache")
        destination_dir = os.getcwd() + "\\Backup"
        checked_process = self.is_process_running()
        if checked_process:
            self.stop_wsa()
        try:
            shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
            self.thread_msg = f"WSA Backup Done."
            self.finished.emit()
        except Exception as e:
            self.exception_msg = f"Backup Error: {e}"
            self.exception_signal.emit()

    def wsa_restore(self):
        destination_dir = (f"C:\\Users\\{self.current_user}\\AppData\\Local\\Packages"
                           "\\MicrosoftCorporationII.WindowsSubsystemForAndroid_8wekyb3d8bbwe\\LocalCache")
        source_dir = os.getcwd() + "\\Backup"
        checked_process = self.is_process_running()
        if checked_process:
            self.stop_wsa()
        try:
            shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
            self.thread_msg = f"WSA Restore Done."
            self.finished.emit()
        except Exception as e:
            self.exception_msg = f"Restore Error: {e}"
            self.exception_signal.emit()

    def open_commands_file(self):
        try:
            subprocess.Popen("Notepad dependencies/Commands.ini", creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            self.exception_msg = f"Error Opening Notepad: {e}"
            self.show_msg_box()

    def save_action_state(self):
        self.settings.setValue("command_at_runtime", self.command_at_runtime_action.isChecked())

    def exit_application(self):
        QCoreApplication.instance().quit()

    def start_wsa(self):
        try:
            subprocess.Popen("WSAClient.exe /launch wsa://system",
                             shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            self.exception_msg = f"start_wsa {e}"
            self.show_msg_box()

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

    def process_commands(self):
        if len(self.commands_list) == 0:
            return
        elif self.command_at_runtime_action.isEnabled():
            self.ran_command = False
            for command in self.commands_list:
                subprocess.call(command, creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(3)

    def check_process(self):
        checked_process = self.is_process_running()
        if checked_process:
            if self.ran_command:
                Thread(target=self.process_commands, daemon=True).start()
            self.tray_icon.setIcon(QIcon(r"dependencies/Resources/Icon1.ico"))
            self.tray_icon.setToolTip("WSA Running")
        else:
            self.tray_icon.setIcon(QIcon(r"dependencies/Resources/stop.ico"))
            self.tray_icon.setToolTip("WSA Not Running")
            if self.command_at_runtime_action.isChecked():
                self.ran_command = True
            else:
                self.ran_command = False

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
            if self.is_task_installed():
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
        warning_message_box.setWindowTitle("WSA-Tray-Helper Error")
        warning_message_box.setWindowIcon(QIcon(r"dependencies/Resources/Icon1.ico"))
        warning_message_box.setFixedSize(400, 200)
        warning_message_box.setIcon(QMessageBox.Icon.Critical)
        warning_message_box.setText(f"{self.exception_msg}")
        winsound.MessageBeep()
        warning_message_box.exec()


if __name__ == '__main__':
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    tray_app = SystemTrayApp()
    sys.exit(app.exec())
