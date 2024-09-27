import sys
import wx
from ui.bullion_ui import MainApp
from ui.system_tray import MyTaskBarIcon  # Updated import for wxPython system tray
from utils.logger import setup_logging


def main():
    logger = setup_logging()
    logger.info("Starting application")

    try:
        app = wx.App(False)  # Initialize the wxPython application
        main_window = MainApp(None, title="Bullion Bell - Forex Economic Calendar")

        # Setup system tray
        tray_icon = MyTaskBarIcon(main_window)

        # Show the main window
        main_window.Show()

        # Start the wxPython event loop
        app.MainLoop()

    except Exception as e:
        logger.exception("An error occurred while running the application")
        raise e


if __name__ == "__main__":
    main()
