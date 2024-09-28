import investpy
import threading
import wx

# Define a custom event type for data fetching
EVT_DATA_FETCHED = wx.NewEventType()
EVT_DATA_FETCHED_BINDER = wx.PyEventBinder(EVT_DATA_FETCHED, 1)

class DataWorker(threading.Thread):
    def __init__(self, from_date, to_date, parent):
        threading.Thread.__init__(self)
        self.from_date = from_date
        self.to_date = to_date
        self.parent = parent

    def run(self):
        # Fetch data from investpy (make sure investpy is installed and up to date)
        try:
            data = investpy.economic_calendar(from_date=self.from_date, to_date=self.to_date)
            print("Raw Data Fetched:", data)  # Debugging statement to see the raw fetched data

            if data is not None and not data.empty:  # Check if data is not empty
                # Convert DataFrame to a list of dictionaries for easier handling
                data_list = data.to_dict(orient='records')
                wx.CallAfter(self.send_data_to_main_thread, data_list)
            else:
                wx.CallAfter(self.send_data_to_main_thread, None)
        except Exception as e:
            print(f"Error fetching data: {e}")
            # Send None in case of error
            wx.CallAfter(self.send_data_to_main_thread, None)

    def send_data_to_main_thread(self, data):
        # Create and post an event to the main thread with fetched data
        event = wx.PyCommandEvent(EVT_DATA_FETCHED, id=self.parent.GetId())
        event.data = data
        wx.PostEvent(self.parent, event)
