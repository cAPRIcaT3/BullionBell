import wx
from wx.adv import TaskBarIcon  # Import TaskBarIcon from wx.adv

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

# Ensure this script runs properly if called directly
if __name__ == '__main__':
    app = wx.App(False)
    frame = wx.Frame(None, wx.ID_ANY, "Test")
    tbicon = TaskBarIcon(frame)
    frame.Show()
    app.MainLoop()
