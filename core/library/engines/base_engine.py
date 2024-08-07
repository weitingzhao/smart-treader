import json
import time
from pathlib import Path
from src.config import Config
from src.utilities import Tools


class BaseEngine:
    def __init__(self, config: Config):
        self._config = config
        self._logger = self._config.logger
        self._tools = Tools(config.logger)

    def path_exist(self, path: Path) -> Path:
        return self._config.path_exist(path)

    def logging_process_time(
            self,
            name: str,
            logging_file_path: Path,
            method_to_run, *args, **kwargs):
        # log start time
        start_time = time.time()

        # **run the provided method**
        method_to_run(*args, **kwargs)

        # log summary
        end_time = time.time()
        total_time = end_time - start_time
        total_time_hours = int(total_time // 3600)
        total_time_minutes = int((total_time % 3600) // 60)
        total_time_seconds = int(total_time % 60)
        process_result = {
            "start_process_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
            "end_process_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
            "total_process_time_seconds": f"{total_time_hours}h {total_time_minutes}m {total_time_seconds}s"
        }

        if logging_file_path.exists():
            with open(logging_file_path, 'r', encoding='utf-8') as status_file:
                existing_data = json.load(status_file)
        else:
            existing_data = {}
        if name in existing_data:
            existing_data[name].update(process_result)
        else:
            existing_data[name] = process_result
        with open(logging_file_path, 'w', encoding='utf-8') as status_file:
            json.dump(existing_data, status_file, indent=4)
