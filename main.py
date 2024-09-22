import sys
from PyQt5.QtWidgets import QApplication
from ui.bullion_ui import MainApp
from ui.system_tray import setup_system_tray

def main():
    app = QApplication(sys.argv)
    main_window = MainApp()
    tray_icon = setup_system_tray(app, main_window)  # Setup system tray
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
