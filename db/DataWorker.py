import investpy
import wx
import threading
from wx.lib.newevent import NewEvent

# Create a new custom event to pass data between threads
DataFetchedEvent, EVT_DATA_FETCHED = NewEvent()

class DataWorker(threading.Thread):  # Use threading.Thread instead of wx.Thread
    def __init__(self, from_date, to_date, parent):
        super().__init__()
        self.from_date = from_date
        self.to_date = to_date
        self.parent = parent  # Store the parent to post events back to UI

    def run(self):
        try:
            # Perform the data fetching operation
            data = investpy.economic_calendar(from_date=self.from_date, to_date=self.to_date)
            # Use CallAfter to post an event to the UI thread
            wx.CallAfter(wx.PostEvent, self.parent, DataFetchedEvent(data=data))
        except Exception as e:
            # Post an event with data set to None in case of error
            wx.CallAfter(wx.PostEvent, self.parent, DataFetchedEvent(data=None))
