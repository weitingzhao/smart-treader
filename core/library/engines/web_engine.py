import requests
from src import Config
from src.engines.base_engine import BaseEngine


class WebEngine(BaseEngine):
    def __init__(
            self,
            config: Config,
            url: str):
        super().__init__(config)
        self.url = url

    def request(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            return response.text
        else:
            self._logger.error(f"Error fetching data: {response.status_code}")
            return None
