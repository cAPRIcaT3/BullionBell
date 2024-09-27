import sys
import logging
import investpy
import wx
import wx.grid
from pynput import keyboard
from db.DataWorker import DataWorker, EVT_DATA_FETCHED


class MainApp(wx.Frame):
    def __init__(self, parent, title):
        super(MainApp, self).__init__(parent, title=title, size=(800, 600))
        self.logger = logging.getLogger('BullionBell')
        self.logger.info('Initializing MainApp UI')
        self.overlay_active = False
        self.initUI()
        self.init_keyboard_listener()

        # Bind custom event to handle data fetched event
        self.Bind(EVT_DATA_FETCHED, self.handle_data_fetched)

    def initUI(self):
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        # Create a table (grid) view for displaying data
        self.tableView = wx.grid.Grid(panel)
        self.tableView.CreateGrid(0, 5)  # Set initial size of 0 rows and 5 columns

        # Set column labels
        self.tableView.SetColLabelValue(0, "Event ID")
        self.tableView.SetColLabelValue(1, "Date")
        self.tableView.SetColLabelValue(2, "Time")
        self.tableView.SetColLabelValue(3, "Country")
        self.tableView.SetColLabelValue(4, "Impact")

        # Adjust the column widths
        for col in range(5):
            self.tableView.SetColSize(col, 120)  # Adjust the size as needed

        # Set font and style
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.tableView.SetLabelFont(font)

        # Set alternating row colors
        self.tableView.SetDefaultCellBackgroundColour(wx.Colour(240, 240, 240))
        self.tableView.SetDefaultCellTextColour(wx.Colour(0, 0, 0))

        # Add the grid to the layout
        vbox.Add(self.tableView, 1, wx.EXPAND | wx.ALL, 5)

        # Create buttons
        self.getDataButton = wx.Button(panel, label='Get Economic Calendar')
        self.getDataButton.Bind(wx.EVT_BUTTON, self.start_data_fetch)
        vbox.Add(self.getDataButton, 0, wx.EXPAND | wx.ALL, 5)

        self.toggleButton = wx.Button(panel, label='Toggle Overlay (Press ALT+SHIFT+A)')
        self.toggleButton.Bind(wx.EVT_BUTTON, self.toggle_overlay)
        vbox.Add(self.toggleButton, 0, wx.EXPAND | wx.ALL, 5)

        # Set the layout of the panel
        panel.SetSizer(vbox)

        self.Centre()
        self.Show()

    def start_data_fetch(self, event):
        # Create and start the data fetching thread
        self.worker = DataWorker('20/09/2024', '27/09/2024', self)
        self.worker.start()

    def handle_data_fetched(self, event):
        data = event.data
        if data is not None:
            self.update_table(data)
        else:
            self.logger.error("Failed to fetch data or data is None")

    def update_table(self, data):
        # Clear existing data
        self.tableView.ClearGrid()

        # Set number of rows and columns dynamically based on data
        num_rows = len(data)
        self.tableView.AppendRows(num_rows)

        # Populate the grid with data
        for row_index, row in enumerate(data.values):
            for col_index, value in enumerate(row):
                self.tableView.SetCellValue(row_index, col_index, str(value))

        # Resize columns to fit content
        self.tableView.AutoSizeColumns()

    def toggle_overlay(self, event=None):
        self.logger.debug('Toggling overlay')
        self.overlay_active = not self.overlay_active
        self.update_window_flags()

    def update_window_flags(self):
        if self.overlay_active:
            self.SetTransparent(25)
        else:
            self.SetTransparent(255)
        self.Refresh()

    def init_keyboard_listener(self):
        listener = keyboard.GlobalHotKeys({
            '<alt>+<shift>+a': lambda: self.toggle_overlay()
        })
        listener.start()


if __name__ == '__main__':
    app = wx.App(False)
    ex = MainApp(None, title='Bullion Bell - Forex Economic Calendar')
    app.MainLoop()
