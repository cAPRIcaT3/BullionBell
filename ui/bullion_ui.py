import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTableView
from PyQt5.QtCore import Qt, QAbstractTableModel
import investpy
from pynput import keyboard

class EconomicDataModel(QAbstractTableModel):
    def __init__(self, data):
        super(EconomicDataModel, self).__init__()
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._data.columns)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.overlay_active = False
        self.initUI()
        self.init_keyboard_listener()

    def initUI(self):
        self.setWindowTitle('Bullion Bell - Forex Economic Calendar')
        self.setGeometry(300, 300, 600, 400)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
        self.setWindowOpacity(0.8)

        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        self.tableView = QTableView()
        layout.addWidget(self.tableView)

        self.getDataButton = QPushButton('Get Economic Calendar')
        self.getDataButton.clicked.connect(self.get_economic_data)
        layout.addWidget(self.getDataButton)

        self.toggleButton = QPushButton('Toggle Overlay')
        self.toggleButton.clicked.connect(self.toggle_overlay)
        layout.addWidget(self.toggleButton)

    def get_economic_data(self):
        data = investpy.economic_calendar(from_date='20/09/2024', to_date='27/09/2024')
        model = EconomicDataModel(data)
        self.tableView.setModel(model)

    def toggle_overlay(self):
        self.overlay_active = not self.overlay_active
        self.update_window_flags()

    def update_window_flags(self):
        if self.overlay_active:
            self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
            self.setWindowOpacity(0.1)
        else:
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.setWindowOpacity(0.8)
        self.show()  # Apply the new window flags

    def init_keyboard_listener(self):
        listener = keyboard.GlobalHotKeys({
            '<alt>+<shift>+a': self.toggle_overlay
        })
        listener.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainApp()
    ex.show()
    sys.exit(app.exec_())
