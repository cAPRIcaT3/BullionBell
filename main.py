import sys
import wx
from ui.bullion_ui import MainApp  # Import the MainApp UI class
from utils.logger import setup_logging  # Import the logging setup function


def main():
    # Setup logging
    logger = setup_logging()
    logger.info("Starting application")

    try:
        # Initialize the wxPython application
        app = wx.App(False)

        # Create and show the main window
        main_window = MainApp(None, title="Bullion Bell - Forex Economic Calendar")
        main_window.Show()

        # Start the wxPython event loop
        app.MainLoop()

    except Exception as e:
        # Log any exception that occurs and raise it again
        logger.exception("An error occurred while running the application")
        raise e


if __name__ == "__main__":
    main()
