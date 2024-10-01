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

        padding = 5  # Adjust the padding between flag and text

        if self.flag_bitmap:
            # Draw the flag image in the top left corner of the cell
            image_x = rect.x + 2  # Padding from the left
            image_y = rect.y + (rect.height - self.flag_bitmap.GetHeight()) // 2  # Center the image vertically
            dc.DrawBitmap(self.flag_bitmap, image_x, image_y, True)

            # Draw the currency code text next to the flag image with padding
            text_x = image_x + self.flag_bitmap.GetWidth() + padding  # Add space between image and text
            text_y = rect.y + (rect.height - dc.GetTextExtent(self.currency_code)[1]) // 2  # Center the text vertically
            dc.DrawText(self.currency_code, text_x, text_y)

        dc.DestroyClippingRegion()

    def GetBestSize(self, grid, attr, dc, row, col):
        """
        Return the size of the cell required to fit the image and text with adjusted spacing.
        """
        padding = 5  # Same padding used in the Draw method
        width = self.flag_bitmap.GetWidth() + dc.GetTextExtent(self.currency_code)[0] + padding + 10  # Adjust width
        height = max(self.flag_bitmap.GetHeight(), dc.GetTextExtent(self.currency_code)[1])  # Adjust height
        return wx.Size(width, height)

    def Clone(self):
        """
        Create a new instance of the renderer.
        """
        return FlagCellRenderer(self.flag_bitmap, self.currency_code)


    def GetBestSize(self, grid, attr, dc, row, col):
        """
        Return the best size for the cell.
        """
        width = 16 + dc.GetTextExtent(self.currency_code)[0] + 10  # Image width + text width + padding
        height = max(16, dc.GetTextExtent(self.currency_code)[1])  # Image height or text height
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

        # Load currency to emoji mapping from the JSON file
        self.flag_handler = CountryFlagHandler()

        # Initialize the UI
        self.initUI()
        self.fixed_height = 450  # Adjust fixed height as needed to account for the toolbar

    def load_currency_to_emoji_mapping(self):
        """Load the currency to emoji mapping from the JSON file."""
        json_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'currency_to_emoji.json')
        with open(json_path, 'r', encoding='utf-8') as file:
            return json.load(file)

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

        # Load rest button
        self.load_rest_button = wx.Button(self, label="Load Rest 🏴")
        self.load_rest_button.Bind(wx.EVT_BUTTON, self.load_rest_data)
        vbox.Add(self.load_rest_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        self.SetSizer(vbox)

        # Bind the custom data fetched event
        self.Bind(EVT_DATA_FETCHED_BINDER, self.handle_data_fetched)

    def on_back_to_home(self, event):
        """Navigate back to the main screen."""
        self.app.switch_screen(MainScreen)

    def start_data_fetch(self):
        """Start data fetch when the screen is switched to."""
        self.app.logger.info("Fetching economic calendar data...")

        # Automatically set the date range based on current date
        current_date = datetime.now()
        start_date = current_date - timedelta(days=1)  # Start date is 1 day before the current date
        end_date = current_date + timedelta(days=7)  # End date is 7 days after the current date

        # Load cached data within the desired date range
        cached_data = self.cache_handler.get_cached_data(start_date, end_date)
        if cached_data:
            self.app.logger.info(f"Loaded {len(cached_data)} records from cache.")
            self.update_table(cached_data[:50])  # Load the first 50 records initially

        # Format the dates as required by the investpy API (DD/MM/YYYY)
        formatted_start_date = start_date.strftime('%d/%m/%Y')
        formatted_end_date = end_date.strftime('%d/%m/%Y')

        # Fetch data from the API for the desired range and merge with cache
        self.app.logger.info(f"Fetching data from {formatted_start_date} to {formatted_end_date}")
        self.worker = DataWorker(formatted_start_date, formatted_end_date, self)
        self.worker.start()

    def update_table(self, data):
        """
        Update the table with the data and insert flag images in the currency column.
        """
        self.tableView.ClearGrid()
        self.tableView.SetRowLabelSize(0)
        if self.tableView.GetNumberRows() > 0:
            self.tableView.DeleteRows(0, self.tableView.GetNumberRows(), True)

        num_rows = len(data)
        if num_rows > 0:
            self.tableView.AppendRows(num_rows)

        for row_index, row in enumerate(data):
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

        self.tableView.AutoSizeColumns()
        self.resize_window_to_fit()

        self.app.logger.info("Table update complete.")

    def load_rest_data(self, event):
        """Load the remaining records when the button is pressed."""
        current_date = datetime.now()
        start_date = current_date - timedelta(days=1)
        end_date = current_date + timedelta(days=7)

        cached_data = self.cache_handler.get_cached_data(start_date, end_date)
        if cached_data:
            self.update_table(cached_data)  # Load all data
            self.load_rest_button.Hide()  # Hide the button after loading all data
            self.Layout()

    def handle_data_fetched(self, event):
        data = event.data
        if data is not None and isinstance(data, list):
            self.cache_handler.add_to_cache(data)  # Save fetched data to cache
            self.update_table(data[:50])  # Load the first 50 records initially

    def resize_window_to_fit(self):
        """Resize window to fit table contents and maintain a fixed height."""
        total_width = sum([self.tableView.GetColSize(col) for col in range(self.tableView.GetNumberCols())])
        total_height = self.tableView.GetNumberRows() * self.tableView.GetDefaultRowSize() + 100  # Add some padding

        required_width = total_width + 50  # Add some padding for width
        max_initial_height = 450  # Set the maximum height for the initial window
        required_height = min(max_initial_height, total_height)  # Restrict the initial height

        # Resize the app window based on content
        self.app.SetSize(wx.Size(required_width, required_height))
        self.app.Fit()  # Ensure everything fits properly
        self.app.Centre()  # Center the window on the screen
