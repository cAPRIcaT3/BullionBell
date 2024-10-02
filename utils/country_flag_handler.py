from collections import OrderedDict
import os
import json
import requests
from io import BytesIO
import wx

class CountryFlagHandler:
    def __init__(self, cache_size=100):
        # Load the JSON file that maps currency codes to flag URLs
        with open("db/currency_to_emoji.json", "r") as file:
            self.currency_flags = json.load(file)

        # LRU Cache for flag images with a size limit
        self.flag_cache = OrderedDict()
        self.cache_size = cache_size

    def fetch_flag_image(self, currency_code):
        """
        Fetch the flag image for the given currency code from the URL or use a local image for EUR.
        Caches the image after the first load.
        """
        # Return from cache if available
        if currency_code in self.flag_cache:
            return self.flag_cache[currency_code]

        # Special case for EUR to use a local file
        if currency_code.upper() == "EUR":
            local_eu_flag_path = "resources/icons/flags/EU_icon.png"
            if os.path.exists(local_eu_flag_path):
                try:
                    flag_image = wx.Image(local_eu_flag_path).Scale(16, 16, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
                    self.flag_cache[currency_code] = flag_image
                    return flag_image
                except Exception as e:
                    print(f"Error loading local flag for EUR: {e}")
                    return None
            else:
                print(f"Local flag image for EUR not found at: {local_eu_flag_path}")
                return None

        # For all other currency codes, continue fetching from URL
        flag_url = self.currency_flags.get(currency_code.upper())
        if flag_url:
            try:
                # Fetch the flag image from the URL
                response = requests.get(flag_url)
                if response.status_code == 200:
                    image_stream = BytesIO(response.content)
                    flag_image = wx.Image(image_stream).Scale(16, 16, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
                    self.flag_cache[currency_code] = flag_image  # Store in cache
                    return flag_image
                else:
                    print(f"Error fetching flag for {currency_code}: {response.status_code}")
                    return None
            except Exception as e:
                print(f"Error fetching flag for {currency_code}: {e}")
                return None

        return None

        return None  # Return None if flag URL or file not found

    def _add_to_cache(self, currency_code, flag_image):
        """
        Add a new flag image to the cache. If the cache exceeds the size limit, remove the oldest item.
        """
        if len(self.flag_cache) >= self.cache_size:
            # Remove the oldest item (first item) in the cache
            self.flag_cache.popitem(last=False)
        # Add the new item to the cache
        self.flag_cache[currency_code] = flag_image
