import wx
from wx.adv import TaskBarIcon  # Import TaskBarIcon from wx.adv

class MyTaskBarIcon(TaskBarIcon):
    def __init__(self, frame):
        super(MyTaskBarIcon, self).__init__()
        self.frame = frame

        # Set up the icon
        icon = wx.Icon("resources/icons/App/icon.png", wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon, "Bullion Bell Running")

        # Bind event for left-click
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_UP, self.on_left_click)

    def on_left_click(self, event):
        # Show or hide the frame on left click
        if self.frame.IsShown():
            self.frame.Hide()
        else:
            self.frame.Show()

    def CreatePopupMenu(self):
        # Create a right-click context menu
        menu = wx.Menu()
        open_menu = menu.Append(wx.ID_OPEN, 'Open')
        exit_menu = menu.Append(wx.ID_EXIT, 'Exit')

        self.Bind(wx.EVT_MENU, self.on_open, open_menu)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_menu)

        return menu

    def on_open(self, event):
        self.frame.Show()

    def on_exit(self, event):
        wx.CallAfter(self.frame.Close)

# Ensure this script runs properly if called directly
if __name__ == '__main__':
    app = wx.App(False)
    frame = wx.Frame(None, wx.ID_ANY, "Test")
    tbicon = MyTaskBarIcon(frame)
    frame.Show()
    app.MainLoop()
