import json
import os
from datetime import datetime


class CacheHandler:
    def __init__(self, cache_file='cache.json', cache_size=None):
        """
        Initialize the CacheHandler with the specified cache file and optional cache size.
        cache_size: The maximum number of records to keep in the cache (None for unlimited).
        """
        self.cache_file = os.path.join(os.path.dirname(__file__), cache_file)
        self.cache_size = cache_size  # Maximum number of items in the cache (None for no limit)
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
        """
        Retrieve cached data within the specified date range.
        start_date, end_date: datetime objects representing the date range.
        Returns a list of cached records within the date range.
        """
        cached_data = []
        for record in self.cache.get("data", []):
            try:
                # Ensure date format consistency in cache
                record_date = datetime.strptime(record['date'], '%d/%m/%Y')
                if start_date <= record_date <= end_date:
                    cached_data.append(record)
            except ValueError as e:
                pass  # Ignore records with invalid date formats
        return cached_data

    def add_to_cache(self, new_data):
        """
        Add new data to the cache, avoiding duplicates based on 'id'.
        If the cache size is set and exceeds the limit, older records are discarded.
        """
        existing_ids = {record['id'] for record in self.cache.get("data", [])}
        self.cache.setdefault("data", [])

        for record in new_data:
            if record['id'] not in existing_ids:
                self.cache['data'].append(record)

        # If cache size is limited, discard older records
        if self.cache_size and len(self.cache['data']) > self.cache_size:
            # Retain only the most recent `cache_size` records
            self.cache['data'] = self.cache['data'][-self.cache_size:]

        self.save_cache()

    def clear_cache(self):
        """Clear the cache data."""
        self.cache = {"data": []}
        self.save_cache()
