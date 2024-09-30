import threading
import time
from datetime import datetime
import pytz

class InternalTimer:
    def __init__(self):
        self.is_running = False
        self.current_time = None
        self.timezone = self.detect_timezone()
        self.interval = 1  # Update interval in seconds

    def detect_timezone(self):
        """Detect and return the user's current timezone."""
        # Detect the local timezone
        local_timezone = pytz.timezone('UTC')  # Default to UTC if detection fails
        try:
            local_timezone = pytz.timezone(pytz.localize(datetime.now()).tzinfo.zone)
        except Exception as e:
            print(f"Timezone detection failed. Defaulting to UTC. Error: {e}")
        return local_timezone

    def start(self):
        """Start the internal clock timer."""
        self.is_running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self):
        """Stop the internal clock timer."""
        self.is_running = False
        if self.thread.is_alive():
            self.thread.join()

    def run(self):
        """Main loop for the internal clock."""
        while self.is_running:
            self.current_time = datetime.now(self.timezone)
            print(f"Internal Time: {self.current_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")
            time.sleep(self.interval)

    def get_current_time(self):
        """Return the current time as a datetime object."""
        return self.current_time

# Example usage
if __name__ == "__main__":
    timer = InternalTimer()
    timer.start()
    time.sleep(10)  # Let it run for 10 seconds
    timer.stop()
