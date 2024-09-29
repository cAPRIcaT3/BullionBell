import time
import threading
from datetime import datetime, timedelta
from playsound import playsound  # Import playsound for sound playback

class AlertSystem:
    def __init__(self):
        self.alerts = []  # List to store alert conditions
        self.is_running = False
        self.alert_interval = 60  # Check every 60 seconds

    def add_alert(self, event_time, sound_file):
        """Add a new alert to the system."""
        alert = {
            'event_time': event_time,  # The time when the alert should trigger
            'sound_file': sound_file,  # The sound file to play
            'triggered': False         # Whether the alert has been triggered
        }
        self.alerts.append(alert)

    def start(self):
        """Start the alert system timer."""
        self.is_running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self):
        """Stop the alert system timer."""
        self.is_running = False
        if self.thread.is_alive():
            self.thread.join()

    def run(self):
        """Main loop for checking alerts."""
        while self.is_running:
            current_time = datetime.now()
            for alert in self.alerts:
                # Check if the alert time is past and it hasn't been triggered yet
                if current_time >= alert['event_time'] and not alert['triggered']:
                    self.trigger_alert(alert)
            time.sleep(self.alert_interval)

    def trigger_alert(self, alert):
        """Trigger an alert."""
        alert['triggered'] = True
        self.play_sound(alert['sound_file'])
        print(f"Alert triggered for event at {alert['event_time']}")

    def play_sound(self, sound_file):
        """Play the alert sound using playsound."""
        try:
            playsound(sound_file)
        except Exception as e:
            print(f"Error playing sound: {e}")

    def clear_alerts(self):
        """Clear all alerts from the system."""
        self.alerts = []

# Example Usage
if __name__ == "__main__":
    alert_system = AlertSystem()
    # Example alert for 1 minute in the future with a test sound file
    alert_time = datetime.now() + timedelta(minutes=1)
    alert_system.add_alert(alert_time, "alert_sound.wav")  # Make sure "alert_sound.wav" is in the current directory
    alert_system.start()
