import sys
import os
import logging
import investpy
import wx
import wx.grid
from pynput import keyboard
from db.DataWorker import DataWorker, EVT_DATA_FETCHED_BINDER  # Use the custom event binder
from wx.adv import TaskBarIcon
import datetime


def handle_data_fetched(self, event):
    data = event.data
    if data is not None and isinstance(data, list):
        print("Data received:", data)  # Debugging statement to see received data
        self.update_table(data)
    else:
        self.logger.error("Failed to fetch data or data format is incorrect")
        print("Error: Data received is not in the expected format.")


# TaskBar Icon Implementation
class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame, icon_path):
        wx.adv.TaskBarIcon.__init__(self)
        self.frame = frame
        self.set_icon(icon_path)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_click)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        exit_menu_item = wx.MenuItem(menu, wx.ID_EXIT, 'Exit')
        menu.Append(exit_menu_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_menu_item)
        return menu

    def set_icon(self, path):
        # Use a different method to set the taskbar icon for compatibility
        icon = wx.Icon(wx.Bitmap(path))
        self.SetIcon(icon, 'Bullion Bell Running')

    def on_left_click(self, event):
        if self.frame.IsShown():
            self.frame.Hide()
        else:
            self.frame.Show()

    def on_exit(self, event):
        wx.CallAfter(self.frame.Close)


class MainApp(wx.Frame):
    def __init__(self, parent, title):
        super(MainApp, self).__init__(parent, title=title)
        self.logger = logging.getLogger('BullionBell')
        self.logger.info('Initializing MainApp UI')
        self.overlay_active = False
        self.columns_visibility = {  # Keep track of visible columns
            'ID': True, 'Date': True, 'Time': True, 'Zone': True,
            'Currency': True, 'Importance': True, 'Event': True,
            'Actual': True, 'Forecast': True, 'Previous': True
        }
        self.initUI()
        self.init_keyboard_listener()

        # Bind custom event to handle data fetched event
        self.Bind(EVT_DATA_FETCHED_BINDER, self.handle_data_fetched)  # Correct binding

    def initUI(self):
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        # Create a table (grid) view for displaying data
        self.tableView = wx.grid.Grid(panel)
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

        # Set a fixed height for the grid
        self.fixed_height = 400  # Adjust fixed height as needed
        self.tableView.SetMinSize((1000, self.fixed_height))

        # Add the grid to the layout
        vbox.Add(self.tableView, 1, wx.EXPAND | wx.ALL, 5)

        # Create a settings button with an icon
        settings_icon = wx.ArtProvider.GetBitmap(wx.ART_HELP_SETTINGS, wx.ART_TOOLBAR, (16, 16))
        self.settingsButton = wx.BitmapButton(panel, id=wx.ID_ANY, bitmap=settings_icon, size=(32, 32))
        self.settingsButton.Bind(wx.EVT_BUTTON, self.open_settings_dialog)
        vbox.Add(self.settingsButton, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        # Create other buttons
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
        self.resize_window_to_fit()  # Initial resize based on visibility

        # Set the icon for the application window
        icon_path = os.path.join('resources', 'icons', 'App', 'icon.png')  # Path to your icon file
        if os.path.exists(icon_path):
            # Load the .png icon and set it to the frame
            icon = wx.Icon(wx.Bitmap(icon_path))
            self.SetIcon(icon)
        else:
            self.logger.error(f"Icon file not found at path: {icon_path}")

        # Setup TaskBar Icon
        self.taskbar_icon = TaskBarIcon(self, icon_path)

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
        self.SetSize(wx.Size(required_width, self.fixed_height))

        # Force the layout to update and fit contents
        self.Layout()
        self.Fit()
        self.Centre()

    import datetime

    def start_data_fetch(self, event):
        # Calculate current date and a range for data retrieval
        today = datetime.date.today()
        from_date = (today - datetime.timedelta(days=1)).strftime('%d/%m/%Y')  # 1 day before today
        to_date = (today + datetime.timedelta(days=7)).strftime('%d/%m/%Y')  # 7 days after today

        print(f"Fetching economic calendar from {from_date} to {to_date}")  # Debug statement

        # Create and start the data fetching thread with the detected date range
        self.worker = DataWorker(from_date, to_date, self)
        self.worker.start()

    def handle_data_fetched(self, event):
        data = event.data
        if data is not None and isinstance(data, list):
            print("Data received:", data)  # Debugging statement
            self.update_table(data)
        else:
            self.logger.error("Failed to fetch data or data format is incorrect")

    def update_table(self, data):
        # Clear existing data and reset grid
        current_rows = self.tableView.GetNumberRows()
        print(f"Current number of rows in the table: {current_rows}")

        # Only delete rows if there are rows to delete
        if current_rows > 0:
            self.tableView.DeleteRows(0, current_rows, True)

        # Log number of rows and columns
        print(f"Number of rows to add: {len(data)}, Columns: {self.tableView.GetNumberCols()}")

        # Set number of rows based on data
        num_rows = len(data)
        if num_rows > 0:
            self.tableView.AppendRows(num_rows)

        # Check if data is being processed and set cell values
        for row_index, row in enumerate(data):
            print(f"Processing Row {row_index}: {row}")  # Debugging statement

            # Ensure row is a dictionary and contains all necessary keys
            if isinstance(row, dict) and all(k in row for k in
                                             ['id', 'date', 'time', 'zone', 'currency', 'importance', 'event', 'actual',
                                              'forecast', 'previous']):
                # Fill each cell with data, ensuring values are strings
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
                # Log an error message if row is not of expected type or missing keys
                self.logger.error(f"Unexpected row type or missing keys: {type(row)}. Content: {row}")

        # Refresh the grid display to make sure everything is updated
        self.tableView.ForceRefresh()
        wx.CallLater(100, self.Refresh)  # Ensure a full UI refresh after grid update

        # Resize columns to fit content
        self.tableView.AutoSizeColumns()
        self.resize_window_to_fit()  # Resize window to fit content after updating data
        print("Table update complete.")

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
