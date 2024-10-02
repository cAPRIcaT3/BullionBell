import os
import json
import wx
import wx.grid
from datetime import datetime, timedelta
from db.DataWorker import DataWorker, EVT_DATA_FETCHED_BINDER
from ui.main_screen import MainScreen
from utils.cache_handler import CacheHandler
from utils.country_flag_handler import CountryFlagHandler

class FlagCellRenderer(wx.grid.GridCellRenderer):
    def __init__(self, flag_bitmap, currency_code):
        wx.grid.GridCellRenderer.__init__(self)
        self.flag_bitmap = flag_bitmap
        self.currency_code = currency_code

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        """
        Draw the flag image and currency code with adjusted spacing.
        """
        dc.SetClippingRegion(rect.x, rect.y, rect.width, rect.height)

        padding = 5  # Padding between the flag and text

        # Calculate the position for the flag and text
        image_x = rect.x + 5  # Padding from the left side of the cell
        image_y = rect.y + (rect.height - self.flag_bitmap.GetHeight()) // 2  # Center the image vertically

        # Draw the flag image
        if self.flag_bitmap:
            dc.DrawBitmap(self.flag_bitmap, image_x, image_y, True)

        # Calculate the position for the text
        text_x = image_x + self.flag_bitmap.GetWidth() + padding  # Place text after the image
        text_y = rect.y + (rect.height - dc.GetTextExtent(self.currency_code)[1]) // 2  # Center the text vertically

        # Draw the currency code text
        dc.DrawText(self.currency_code, text_x, text_y)

        dc.DestroyClippingRegion()

    def GetBestSize(self, grid, attr, dc, row, col):
        """
        Return the size of the cell required to fit the image and text with adjusted spacing.
        """
        padding = 5  # Same padding used in the Draw method
        width = self.flag_bitmap.GetWidth() + dc.GetTextExtent(self.currency_code)[0] + padding + 10  # Adjust width
        height = max(self.flag_bitmap.GetHeight(), dc.GetTextExtent(self.currency_code)[1]) + padding  # Adjust height
        return wx.Size(width, height)

    def Clone(self):
        """
        Create a new instance of the renderer.
        """
        return FlagCellRenderer(self.flag_bitmap, self.currency_code)

class EconomicCalendarScreen(wx.Panel):
    def __init__(self, parent, app):
        super(EconomicCalendarScreen, self).__init__(parent)
        self.app = app  # Store the MainApp instance
        self.columns_visibility = {
            'Date': True, 'Time': True, 'Zone': True, 'Currency': True,
            'Importance': True, 'Event': True, 'Actual': True, 'Forecast': True, 'Previous': True
        }
        self.cache_handler = CacheHandler()
        self.data_fetched = False  # Flag to prevent duplicate rendering
        self.flag_handler = CountryFlagHandler()
        self.all_data = []  # To store all fetched data
        self.initial_data = []  # To store only the initial 50 records
        self.records_displayed = 50  # Initially display only 50 records

        # Initialize the UI
        self.initUI()
        self.fixed_height = 450  # Adjust fixed height as needed to account for the toolbar

    def initUI(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Create a toolbar sizer with horizontal alignment
        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Home Button
        home_icon = wx.ArtProvider.GetBitmap(wx.ART_GO_HOME, wx.ART_TOOLBAR, (16, 16))
        home_text = wx.StaticText(self, label="Back to Main")
        homeButton = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=home_icon, size=(32, 32))
        homeButton.Bind(wx.EVT_BUTTON, self.on_back_to_home)

        # Add Home Button and text
        home_sizer = wx.BoxSizer(wx.HORIZONTAL)
        home_sizer.Add(homeButton, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        home_sizer.Add(home_text, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        toolbar_sizer.Add(home_sizer, 0, wx.ALL, 5)

        # Spacer to create a gap between buttons
        toolbar_sizer.Add((20, 0), 0, wx.EXPAND)

        # Toggle Columns Button
        toggle_icon = wx.ArtProvider.GetBitmap(wx.ART_LIST_VIEW, wx.ART_TOOLBAR, (16, 16))
        toggle_text = wx.StaticText(self, label="Toggle columns")
        toggleButton = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=toggle_icon, size=(32, 32))
        toggleButton.Bind(wx.EVT_BUTTON, self.open_settings_dialog)

        # Add Toggle Button and text
        toggle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        toggle_sizer.Add(toggleButton, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        toggle_sizer.Add(toggle_text, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        toolbar_sizer.Add(toggle_sizer, 0, wx.ALL, 5)

        # Add a flexible spacer to push items to the left if needed
        toolbar_sizer.AddStretchSpacer()

        # Add the toolbar sizer to the main vertical sizer
        vbox.Add(toolbar_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Create a table (grid) view for displaying economic calendar data
        self.tableView = wx.grid.Grid(self)
        self.tableView.CreateGrid(0, 9)  # Adjust the number of columns

        # Set column labels
        columns = ["Date", "Time", "Zone", "Currency", "Importance", "Event", "Actual", "Forecast", "Previous"]
        for col_index, col_label in enumerate(columns):
            self.tableView.SetColLabelValue(col_index, col_label)

        # Adjust column sizes
        for col in range(9):
            self.tableView.SetColSize(col, 100)

        # Add the grid to the layout
        vbox.Add(self.tableView, 1, wx.EXPAND | wx.ALL, 5)

        # Add the "Load Rest" button at the bottom
        self.load_rest_button = wx.Button(self, label="Load Rest")
        self.load_rest_button.Bind(wx.EVT_BUTTON, self.on_load_rest)
        vbox.Add(self.load_rest_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.SetSizer(vbox)

        # Bind the custom data fetched event
        self.Bind(EVT_DATA_FETCHED_BINDER, self.handle_data_fetched)

    def on_back_to_home(self, event):
        """Navigate back to the main screen."""
        self.app.switch_screen(MainScreen)

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
        """Resize window to fit table contents and maintain a fixed height."""
        total_width = sum([self.tableView.GetColSize(col) for col in range(self.tableView.GetNumberCols())])
        total_height = self.tableView.GetNumberRows() * self.tableView.GetRowSize(0) + 100  # Add some padding

        required_width = total_width + 50  # Add some padding for width
        max_initial_height = 450  # Set the maximum height for the initial window
        required_height = min(max_initial_height, total_height)  # Restrict the initial height

        # Resize the app window based on content
        self.app.SetSize(wx.Size(required_width, required_height))
        self.app.Fit()  # Ensure everything fits properly
        self.app.Centre()  # Center the window on the screen

    def start_data_fetch(self):
        """Start data fetch when the screen is switched to."""
        self.app.logger.info("Fetching economic calendar data...")

        # Automatically set the date range based on current date
        current_date = datetime.now()
        start_date = current_date - timedelta(days=1)  # Start date is 1 day before current date
        end_date = current_date + timedelta(days=7)  # End date is 7 days after current date

        # Load cached data within the desired date range
        cached_data = self.cache_handler.get_cached_data(start_date, end_date)
        if cached_data:
            self.app.logger.info(f"Loaded {len(cached_data)} records from cache.")
            self.update_table(cached_data)

        # Format the dates as required by the investpy API (DD/MM/YYYY)
        formatted_start_date = start_date.strftime('%d/%m/%Y')
        formatted_end_date = end_date.strftime('%d/%m/%Y')

        # Fetch data from the API for the desired range and merge with cache
        self.app.logger.info(f"Fetching data from {formatted_start_date} to {formatted_end_date}")
        self.worker = DataWorker(formatted_start_date, formatted_end_date, self)
        self.worker.start()

    def handle_data_fetched(self, event):
        data = event.data
        if data is not None and isinstance(data, list):
            self.app.logger.info(f"Data received: {data}")
            self.all_data = data
            self.initial_data = data[:self.records_displayed]  # Only the first 50 records initially
            self.cache_handler.add_to_cache(data)  # Save fetched data to cache
            self.update_table(self.initial_data)
        else:
            self.app.logger.error("Failed to fetch data or data format is incorrect")

    def update_table(self, data):
        """
        Update the table with the entire data and insert flag images in the currency column.
        """
        # Freeze grid updates to avoid rendering issues while updating the grid
        self.tableView.Freeze()

        # Clear existing data and reset grid
        self.tableView.ClearGrid()
        self.tableView.SetRowLabelSize(0)  # Hide row labels (serial numbers)
        if self.tableView.GetNumberRows() > 0:
            self.tableView.DeleteRows(0, self.tableView.GetNumberRows(), True)

        # Set number of rows based on data
        num_rows = len(data)
        if num_rows > 0:
            self.tableView.AppendRows(num_rows)

        for row_index, row in enumerate(data):
            if isinstance(row, dict) and all(k in row for k in
                                             ['id', 'date', 'time', 'zone', 'currency', 'importance', 'event', 'actual',
                                              'forecast', 'previous']):
                # Populate the data in columns
                self.tableView.SetCellValue(row_index, 0, row['date'])
                self.tableView.SetCellValue(row_index, 1, row['time'] or 'N/A')
                self.tableView.SetCellValue(row_index, 2, row['zone'] or 'N/A')

                # Fetch and display the flag image next to the currency code
                currency_code = row.get('currency')
                if currency_code:
                    flag_bitmap = self.flag_handler.fetch_flag_image(currency_code)
                    if flag_bitmap:
                        # Set custom renderer to display flag and currency code
                        renderer = FlagCellRenderer(flag_bitmap, currency_code)
                        self.tableView.SetCellRenderer(row_index, 3, renderer)
                    else:
                        self.tableView.SetCellValue(row_index, 3, currency_code)
                else:
                    self.tableView.SetCellValue(row_index, 3, 'N/A')

                self.tableView.SetCellValue(row_index, 4, row['importance'] or 'N/A')
                self.tableView.SetCellValue(row_index, 5, row['event'] or 'N/A')
                self.tableView.SetCellValue(row_index, 6, str(row['actual']) if row['actual'] else 'N/A')
                self.tableView.SetCellValue(row_index, 7, str(row['forecast']) if row['forecast'] else 'N/A')
                self.tableView.SetCellValue(row_index, 8, str(row['previous']) if row['previous'] else 'N/A')

        # Auto-resize columns to fit the content
        self.tableView.AutoSizeColumns()

        # Resize the window to fit the content
        self.resize_window_to_fit()

        # Thaw grid updates and refresh the table to show all data at once
        self.tableView.Thaw()
        self.tableView.ForceRefresh()

        self.app.logger.info("Table update complete.")

    def on_load_rest(self, event):
        """Load the rest of the data when the 'Load Rest' button is clicked."""
        self.update_table(self.all_data)  # Load all records
        self.load_rest_button.Hide()  # Hide the button after loading the rest
        self.Layout()  # Re-layout the window to fit changes
