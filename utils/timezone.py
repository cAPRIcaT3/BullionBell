import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTableView, QLabel
from PyQt5.QtCore import Qt, QTimer
from utils.timezone import get_current_date_time  # Ensure this path is correct
import investpy

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

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[section]
        return None

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowOpacity(0.8)

        self.tableView = QTableView(self)
        self.refreshButton = QPushButton('Refresh Data', self)
        self.refreshButton.clicked.connect(self.get_economic_data)

        self.clockLabel = QLabel(self)
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)  # Timer updates every second

        layout = QVBoxLayout(self)
        layout.addWidget(self.tableView)
        layout.addWidget(self.refreshButton)
        layout.addWidget(self.clockLabel)
        self.setLayout(layout)
        self.setWindowTitle('Forex Economic Calendar')
        self.show()
        self.update_clock()  # Initial clock update

    def get_economic_data(self):
        data = investpy.economic_calendar(from_date='20/09/2024', to_date='27/09/2024')
        model = EconomicDataModel(data)
        self.tableView.setModel(model)

    def update_clock(self):
        _, current_time = get_current_date_time()
        self.clockLabel.setText("Current Time: " + current_time)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
