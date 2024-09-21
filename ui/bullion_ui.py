import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTableView
from PyQt5.QtCore import Qt, QAbstractTableModel
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
        self.button = QPushButton('Get Economic Calendar', self)
        self.button.clicked.connect(self.get_economic_data)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tableView)
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.setWindowTitle('Forex Economic Calendar')
        self.show()

    def get_economic_data(self):
        data = investpy.economic_calendar(from_date='20/09/2024', to_date='27/09/2024')
        model = EconomicDataModel(data)
        self.tableView.setModel(model)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
