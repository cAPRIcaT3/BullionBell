import wx

class MainScreen(wx.Panel):
    def __init__(self, parent, app):
        super(MainScreen, self).__init__(parent)
        self.app = app  # Store the MainApp instance
        self.initUI()

    def initUI(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Add welcome text
        welcome_text = wx.StaticText(self, label="Welcome to Bullion Bell")
        vbox.Add(welcome_text, 0, wx.ALIGN_CENTER | wx.TOP, 20)

        # Add a button to switch to the economic calendar screen
        switch_button = wx.Button(self, label="View Economic Calendar")
        switch_button.Bind(wx.EVT_BUTTON, self.on_switch_to_calendar)
        vbox.Add(switch_button, 0, wx.ALIGN_CENTER | wx.TOP, 20)

        self.SetSizer(vbox)

    def on_switch_to_calendar(self, event):
        # Call the switch_to_calendar_screen method from MainApp
        self.app.switch_to_calendar_screen()
