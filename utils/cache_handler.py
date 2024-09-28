import json
import os
from datetime import datetime


class CacheHandler:
    def __init__(self, cache_file='cache.json'):
        """Initialize the CacheHandler with the specified cache file."""
        self.cache_file = os.path.join(os.path.dirname(__file__), cache_file)
        self.cache = self.load_cache()

    def load_cache(self):
        """Load cached data from the cache file."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {"data": []}
        return {"data": []}

    def save_cache(self):
        """Save the current cache data to the cache file."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=4)

    def get_cached_data(self, start_date, end_date):
        """Retrieve cached data within the specified date range."""
        cached_data = []
        for record in self.cache.get("data", []):
            record_date = datetime.strptime(record['date'], '%d/%m/%Y')
            if start_date <= record_date <= end_date:
                cached_data.append(record)
        return cached_data

    def add_to_cache(self, new_data):
        """Add new data to the cache, avoiding duplicates."""
        existing_ids = {record['id'] for record in self.cache.get("data", [])}
        self.cache.setdefault("data", [])
        for record in new_data:
            if record['id'] not in existing_ids:
                self.cache['data'].append(record)
        self.save_cache()

    def clear_cache(self):
        """Clear the cache data."""
        self.cache = {"data": []}
        self.save_cache()

# Example usage
if __name__ == "__main__":
    # Create a CacheHandler instance
    cache_handler = CacheHandler()

    # Add some sample data to the cache
    sample_data = [
        {"id": 1, "date": "01/01/2024", "event": "New Year Event"},
        {"id": 2, "date": "15/01/2024", "event": "Mid-January Event"}
    ]
    cache_handler.add_to_cache(sample_data)

    # Retrieve cached data for a specific date range
    start_date = datetime.strptime("01/01/2024", '%d/%m/%Y')
    end_date = datetime.strptime("31/01/2024", '%d/%m/%Y')
    cached_data = cache_handler.get_cached_data(start_date, end_date)
    print(f"Cached Data: {cached_data}")

    # Clear cache
    cache_handler.clear_cache()
    print(f"Cache after clearing: {cache_handler.cache}")
