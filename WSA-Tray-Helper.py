from PySide6.QtWidgets import QMenu, QSystemTrayIcon, QApplication, QMessageBox
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QTimer, QSettings, Qt, Signal, QObject, QCoreApplication
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
    finished = Signal()
    exception_signal = Signal()
    check_signal = Signal()

    def __init__(self):
        super().__init__()
        self.backup_path = configparser.ConfigParser()
        self.backup_path.read(r"dependencies\Backup_path.ini")
        self.custom_path = self.backup_path['BACKUP_PATH']['custom_path']
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
        self.tray_icon.setIcon(QIcon(r"dependencies\Resources\Icon1.ico"))
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_signal)
        self.timer.start(5000)
        self.check_signal.connect(self.check_process, Qt.ConnectionType.QueuedConnection)
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

        self.menu.addAction(QIcon(r"dependencies\Resources\Icon1.ico"), "Start WSA").triggered.connect(self.start_wsa)
        self.menu.addAction(QIcon(r"dependencies\Resources\stop.ico"), "Stop WSA").triggered.connect(self.stop_wsa)
        self.menu.addSeparator()
        (self.menu.addAction(QIcon(r"dependencies\Resources\folder.ico"), "WSA Files")
         .triggered.connect(lambda: self.open_wsa_files()))
        (self.menu.addAction(QIcon(r"dependencies\Resources\settings.ico"), "WSA Settings")
         .triggered.connect(lambda: self.open_wsa_settings()))
        (self.menu.addAction(QIcon(r"dependencies\Resources\android.ico"), "Android Settings")
         .triggered.connect(lambda: self.open_android_settings()))
        self.menu.addSeparator()
        self.menu.addAction(QIcon(r"dependencies\Resources\backup.ico"), "Backup WSA").triggered.connect(
            lambda: Thread(target=self.wsa_backup, daemon=True).start())
        self.menu.addAction(QIcon(r"dependencies\Resources\restore.ico"), "Restore WSA").triggered.connect(
            lambda: Thread(target=self.wsa_restore, daemon=True).start())
        self.menu.addSeparator()
        self.menu.addAction(QIcon(r"dependencies\Resources\command.ico"), "Open Commands Config").triggered.connect(
            self.open_commands_file)
        self.menu.addAction(QIcon(r"dependencies\Resources\about.ico"), "About").triggered.connect(
            self.about_function)
        self.menu.addAction(QIcon(r"dependencies\Resources\exit.ico"), "Exit").triggered.connect(
            self.exit_application)
        self.tray_icon.setContextMenu(self.menu)
        self.run_initially_at_start()
        with open(r'dependencies\Resources\custom.css', 'r') as file:
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
        message_box.setWindowIcon(QIcon(r"dependencies\Resources\Icon1.ico"))
        message_box.setFixedSize(400, 200)
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setText(f"{self.thread_msg}")
        winsound.MessageBeep()
        message_box.exec()

    def wsa_backup(self):
        checked_process = self.is_process_running("WsaClient.exe")

        if checked_process:
            self.stop_wsa()
        try:
            destination_dir = os.getcwd() + r"\Backup\LocalCache"
            source_dir = (fr"C:\Users\{self.current_user}\AppData\Local\Packages" +
                          r"\MicrosoftCorporationII.WindowsSubsystemForAndroid_8wekyb3d8bbwe\LocalCache")
            shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
            destination_dir = os.getcwd() + r"\Backup\LocalState"
            source_dir = (fr"C:\Users\{self.current_user}\AppData\Local\Packages" +
                          r"\MicrosoftCorporationII.WindowsSubsystemForAndroid_8wekyb3d8bbwe\LocalState")
            shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
            self.thread_msg = f"WSA Backup Done."
            self.finished.emit()
        except Exception as e:
            self.exception_msg = f"Backup Error: {e}"
            self.exception_signal.emit()

    def wsa_restore(self):
        checked_process = self.is_process_running("WsaClient.exe")

        if checked_process:
            self.stop_wsa()
        try:
            source_dir = os.getcwd() + r"\Backup\LocalCache"
            destination_dir = (fr"C:\Users\{self.current_user}\AppData\Local\Packages" +
                               r"\MicrosoftCorporationII.WindowsSubsystemForAndroid_8wekyb3d8bbwe\LocalCache")
            shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
            source_dir = os.getcwd() + r"\Backup\LocalState"
            destination_dir = (fr"C:\Users\{self.current_user}\AppData\Local\Packages" +
                               r"\MicrosoftCorporationII.WindowsSubsystemForAndroid_8wekyb3d8bbwe\LocalState")
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

    @staticmethod
    def exit_application():
        QCoreApplication.instance().quit()

    def start_wsa(self):
        try:
            subprocess.Popen("WSAClient.exe /launch wsa://system",
                             shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            self.exception_msg = f"start_wsa {e}"
            self.show_msg_box()

    @staticmethod
    def stop_wsa():
        # Will Shut down WSA.
        subprocess.Popen("WSAClient.exe /shutdown", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        # Will close vmcompute.
        subprocess.Popen("taskkill /F /IM vmcompute.exe", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        # Will stop CrashUploader from running in the background.
        subprocess.Popen("taskkill /F /IM WSACrashUploader.exe", shell=True,
                         creationflags=subprocess.CREATE_NO_WINDOW)
        # Will stop extra vmwp from running.
        subprocess.Popen("taskkill /F /IM vmwp.exe", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

    @staticmethod
    def open_wsa_settings():
        subprocess.Popen("start wsa-settings://", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

    @staticmethod
    def open_wsa_files():
        subprocess.Popen("WSAClient.exe /launch wsa://com.android.documentsui",
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

    @staticmethod
    def open_android_settings():
        subprocess.Popen("WSAClient.exe /launch wsa://com.android.settings",
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

    @staticmethod
    def about_function():
        subprocess.Popen("start https://github.com/7gxycn08/WSA-Tray-Helper",
                         shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)

    def is_process_running(self, process_name):
        process_query_limited_information = 0x1000

        try:
            processes = (ctypes.c_ulong * 2048)()
            cb = ctypes.c_ulong(ctypes.sizeof(processes))
            ctypes.windll.psapi.EnumProcesses(ctypes.byref(processes), cb, ctypes.byref(cb))

            process_count = cb.value // ctypes.sizeof(ctypes.c_ulong)
            for i in range(process_count):
                process_id = processes[i]
                process_handle = ctypes.windll.kernel32.OpenProcess(process_query_limited_information, False,
                                                                    process_id)

                if process_handle:
                    buffer_size = 260
                    buffer = ctypes.create_unicode_buffer(buffer_size)
                    success = ctypes.windll.kernel32.QueryFullProcessImageNameW(process_handle, 0, buffer,
                                                                                ctypes.byref(
                                                                                    ctypes.c_ulong(buffer_size)))
                    ctypes.windll.kernel32.CloseHandle(process_handle)

                    if success:
                        process_name_actual = os.path.basename(buffer.value)
                        if process_name_actual == process_name:
                            return True
            return False

        except Exception as e:
            self.exception_msg = f"is_process_running {e}"
            self.finished.emit()
            return False

    def process_commands(self):
        if len(self.commands_list) == 0:
            return
        elif self.command_at_runtime_action.isEnabled():
            self.ran_command = False
            for command in self.commands_list:
                subprocess.call(command, creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(3)

    def check_process(self):
        checked_process = self.is_process_running("WsaClient.exe")
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

            root_folder.GetTask(self.task_name)
            return True

        except Exception as e:
            self.exception_msg = f"Task installation failed: {e}"
            self.show_msg_box()
            return False

    def register_as_task(self):
        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()

            root_folder = scheduler.GetFolder('\\')

            task_def = scheduler.NewTask(0)
            task_def.RegistrationInfo.Description = 'Start WSA-Tray-Helper at Boot'

            trigger = task_def.Triggers.Create(9)
            trigger.Id = 'LogonTriggerId'

            exec_action = task_def.Actions.Create(0)
            exec_action.Path = self.script_path
            exec_action.WorkingDirectory = os.getcwd()

            principal = task_def.Principal
            principal.UserId = os.getlogin()
            principal.RunLevel = 1
            principal.LogonType = 3

            task_def.Settings.ExecutionTimeLimit = 'PT0S'

            root_folder.RegisterTaskDefinition(
                self.task_name,
                task_def,
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
                root_folder.GetTask(self.task_name)
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
