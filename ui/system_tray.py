from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon

def setup_system_tray(app, window):
    trayIcon = QSystemTrayIcon(QIcon("path/to/icon.png"), app)  # Ensure you have an icon
    trayIcon.setToolTip("Bullion Bell Running")

    trayMenu = QMenu()
    openAction = QAction("Open", trayMenu)
    openAction.triggered.connect(window.show)
    trayMenu.addAction(openAction)

    exitAction = QAction("Exit", trayMenu)
    exitAction.triggered.connect(app.quit)
    trayMenu.addAction(exitAction)

    trayIcon.setContextMenu(trayMenu)
    trayIcon.show()
    return trayIcon  # Return to keep a reference
