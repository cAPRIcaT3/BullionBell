import wx
import wx.grid
from db.DataWorker import DataWorker, EVT_DATA_FETCHED_BINDER
from datetime import datetime, timedelta


class EconomicCalendarScreen(wx.Panel):
    def __init__(self, parent, app):
        super(EconomicCalendarScreen, self).__init__(parent)
        self.app = app  # Store the MainApp instance
        self.columns_visibility = {  # Keep track of visible columns
            'ID': True, 'Date': True, 'Time': True, 'Zone': True,
            'Currency': True, 'Importance': True, 'Event': True,
            'Actual': True, 'Forecast': True, 'Previous': True
        }
        self.fixed_height = 450  # Adjust fixed height as needed to account for the toolbar
        self.initUI()

    def initUI(self):
        # Create a vertical box sizer for the main layout
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Create a toolbar with a 'Select Columns' button
        toolbar = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.NO_BORDER)
        select_columns_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle columns', wx.ArtProvider.GetBitmap(wx.ART_LIST_VIEW))
        toolbar.AddControl(wx.StaticText(toolbar, label=" Toggle columns"))  # Add static text next to the icon
        toolbar.Realize()
        self.Bind(wx.EVT_TOOL, self.open_settings_dialog, select_columns_tool)
        vbox.Add(toolbar, 0, wx.EXPAND)

        # Create a table (grid) view for displaying economic calendar data
        self.tableView = wx.grid.Grid(self)
        self.tableView.CreateGrid(0, 10)

        # Set column labels based on required fields
        columns = ["ID", "Date", "Time", "Zone", "Currency", "Importance", "Event", "Actual", "Forecast", "Previous"]
        for col_index, col_label in enumerate(columns):
            self.tableView.SetColLabelValue(col_index, col_label)

        # Adjust column sizes
        for col in range(10):
            self.tableView.SetColSize(col, 100)

        # Hide default row labels to eliminate empty space
        self.tableView.SetRowLabelSize(0)

        # Add the grid to the layout
        vbox.Add(self.tableView, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(vbox)

        # Bind the custom data fetched event
        self.Bind(EVT_DATA_FETCHED_BINDER, self.handle_data_fetched)

    def open_settings_dialog(self, event):
        """Open a dialog to toggle fields on and off."""
        dialog = wx.Dialog(self, title="Select Columns", size=(300, 400))
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Add checkboxes for each column
        self.checkboxes = {}
        for column, visible in self.columns_visibility.items():
            checkbox = wx.CheckBox(dialog, label=column, style=wx.ALIGN_LEFT)
            checkbox.SetValue(visible)
            checkbox.Bind(wx.EVT_CHECKBOX, self.on_checkbox_toggle)
            vbox.Add(checkbox, 0, wx.ALL, 5)
            self.checkboxes[column] = checkbox

        # Add an OK button to apply changes and close the dialog
        ok_button = wx.Button(dialog, wx.ID_OK, label="Apply")
        ok_button.Bind(wx.EVT_BUTTON, lambda event: self.apply_column_visibility(event, dialog))
        vbox.Add(ok_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        dialog.SetSizer(vbox)
        dialog.Bind(wx.EVT_CLOSE, lambda event: dialog.Destroy())  # Ensure dialog is destroyed on close
        dialog.ShowModal()
        dialog.Destroy()

    def on_checkbox_toggle(self, event):
        checkbox = event.GetEventObject()
        label = checkbox.GetLabel()
        self.columns_visibility[label] = checkbox.GetValue()

    def apply_column_visibility(self, event, dialog):
        """Update the grid based on the checkbox selection and close dialog."""
        for col_index, (column, visible) in enumerate(self.columns_visibility.items()):
            if visible:
                self.tableView.SetColSize(col_index, 100)  # Set size to default
            else:
                self.tableView.SetColSize(col_index, 0)  # Hide column by setting size to 0

        self.tableView.ForceRefresh()
        self.resize_window_to_fit()  # Resize window after updating visibility
        dialog.EndModal(wx.ID_OK)  # Close the dialog
        dialog.Destroy()

    def resize_window_to_fit(self):
        """Resize window to the smallest possible width while maintaining a fixed height."""
        total_width = 0
        for col_index in range(self.tableView.GetNumberCols()):
            if self.columns_visibility[self.tableView.GetColLabelValue(col_index)]:
                total_width += self.tableView.GetColSize(col_index)

        # Calculate necessary width only
        required_width = total_width + 50  # Add some padding

        # Set the frame size with fixed height
        self.app.SetSize(wx.Size(required_width, self.fixed_height))

        # Force the layout to update and fit contents
        self.Layout()
        self.Fit()
        self.app.Centre()

    def start_data_fetch(self):
        """Start data fetch when the screen is switched to."""
        self.app.logger.info("Fetching economic calendar data...")

        # Automatically set the date range based on current date
        current_date = datetime.now()
        start_date = current_date - timedelta(days=3)  # Start date is 3 days before current date
        end_date = current_date + timedelta(days=7)  # End date is 7 days after current date

        # Format the dates as required by the investpy API (DD/MM/YYYY)
        formatted_start_date = start_date.strftime('%d/%m/%Y')
        formatted_end_date = end_date.strftime('%d/%m/%Y')

        self.app.logger.info(f"Fetching data from {formatted_start_date} to {formatted_end_date}")
        self.worker = DataWorker(formatted_start_date, formatted_end_date, self)
        self.worker.start()

    def handle_data_fetched(self, event):
        data = event.data
        if data is not None and isinstance(data, list):
            self.app.logger.info(f"Data received: {data}")
            self.update_table(data)
        else:
            self.app.logger.error("Failed to fetch data or data format is incorrect")

    def update_table(self, data):
        # Clear existing data and reset grid
        self.tableView.ClearGrid()
        if self.tableView.GetNumberRows() > 0:
            self.tableView.DeleteRows(0, self.tableView.GetNumberRows(), True)

        # Set number of rows based on data
        num_rows = len(data)
        if num_rows > 0:
            self.tableView.AppendRows(num_rows)

        # Populate grid with data
        for row_index, row in enumerate(data):
            if isinstance(row, dict) and all(k in row for k in
                                             ['id', 'date', 'time', 'zone', 'currency', 'importance', 'event', 'actual',
                                              'forecast', 'previous']):
                self.tableView.SetCellValue(row_index, 0, str(row['id']))
                self.tableView.SetCellValue(row_index, 1, row['date'])
                self.tableView.SetCellValue(row_index, 2, row['time'] or 'N/A')
                self.tableView.SetCellValue(row_index, 3, row['zone'] or 'N/A')
                self.tableView.SetCellValue(row_index, 4, row['currency'] or 'N/A')
                self.tableView.SetCellValue(row_index, 5, row['importance'] or 'N/A')
                self.tableView.SetCellValue(row_index, 6, row['event'] or 'N/A')
                self.tableView.SetCellValue(row_index, 7, str(row['actual']) if row['actual'] else 'N/A')
                self.tableView.SetCellValue(row_index, 8, str(row['forecast']) if row['forecast'] else 'N/A')
                self.tableView.SetCellValue(row_index, 9, str(row['previous']) if row['previous'] else 'N/A')
            else:
                self.app.logger.error(f"Unexpected row type or missing keys: {type(row)}. Content: {row}")

        # Refresh the grid display to make sure everything is updated
        self.tableView.ForceRefresh()
        wx.CallLater(100, self.Refresh)  # Ensure a full UI refresh after grid update

        # Resize columns to fit content
        self.tableView.AutoSizeColumns()
        self.resize_window_to_fit()  # Resize window to fit content after updating data
        self.app.logger.info("Table update complete.")
