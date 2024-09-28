import sys
import os
import logging
import wx
from pynput import keyboard
from wx.adv import TaskBarIcon
from ui.main_screen import MainScreen
from ui.economic_calendar_screen import EconomicCalendarScreen
from db.DataWorker import DataWorker, EVT_DATA_FETCHED_BINDER


class CustomTaskBarIcon(TaskBarIcon):
    def __init__(self, frame, icon_path):
        super(CustomTaskBarIcon, self).__init__()
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
        self.current_screen = None
        self.initUI()
        self.init_keyboard_listener()

    def initUI(self):
        panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create a container panel for switching screens
        self.screen_panel = wx.Panel(panel)
        self.screen_sizer = wx.BoxSizer(wx.VERTICAL)
        self.screen_panel.SetSizer(self.screen_sizer)

        # Add screen_panel to the main sizer
        self.main_sizer.Add(self.screen_panel, 1, wx.EXPAND | wx.ALL, 5)

        # Set main sizer
        panel.SetSizer(self.main_sizer)

        # Show the default screen (Main Screen)
        self.switch_screen(MainScreen)

        self.Centre()
        self.Show()

        # Set the icon for the application window
        icon_path = os.path.join('resources', 'icons', 'App', 'icon.png')
        if os.path.exists(icon_path):
            icon = wx.Icon(wx.Bitmap(icon_path))
            self.SetIcon(icon)
        else:
            self.logger.error(f"Icon file not found at path: {icon_path}")

        # Setup TaskBar Icon
        self.taskbar_icon = CustomTaskBarIcon(self, icon_path)

    def switch_screen(self, screen_class):
        """Switches the current screen to the given screen class."""
        if self.current_screen:
            self.current_screen.Destroy()

        # Create an instance of the screen class and add it to the sizer
        self.current_screen = screen_class(self.screen_panel, self)  # Pass the MainApp instance
        self.screen_sizer.Add(self.current_screen, 1, wx.EXPAND | wx.ALL, 5)
        self.screen_panel.Layout()

    def switch_to_calendar_screen(self):
        """Switch to Economic Calendar screen and trigger data retrieval."""
        self.switch_screen(EconomicCalendarScreen)
        # Trigger data retrieval for the economic calendar screen
        self.current_screen.start_data_fetch()

    def init_keyboard_listener(self):
        listener = keyboard.GlobalHotKeys({
            '<alt>+<shift>+a': lambda: self.toggle_overlay()
        })
        listener.start()

    def toggle_overlay(self):
        """Toggle the transparency of the window."""
        self.overlay_active = not self.overlay_active
        self.SetTransparent(25 if self.overlay_active else 255)
        self.Refresh()


if __name__ == '__main__':
    app = wx.App(False)
    ex = MainApp(None, title='Bullion Bell - Forex Economic Calendar')
    app.MainLoop()
