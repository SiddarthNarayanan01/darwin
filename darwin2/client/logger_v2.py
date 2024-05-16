from logging import exception
from os import path
import time
from datetime import datetime
from darwin2.evolving.samples import Sample


class Logger:
    def __init__(self, base_path: str) -> None:
        self.base_path = base_path
        self.last_save = time.time()
        self.samples_file_path = path.join(base_path, "samples.log")
        self.corrections_file_path = path.join(base_path, "corrections.log")
        self.misc_file_path = path.join(base_path, "misc.log")
        self.time_since_last_write = time.time()
        self.open_files()

    def open_files(self):
        try:
            self.samples_file = open(self.samples_file_path, "a+")
            self.corrections_file = open(self.corrections_file_path, "a+")
            self.misc_file = open(self.misc_file_path, "a+")
        except Exception as e:
            print("Could not open files")
            print(e)

    def close_files(self):
        try:
            self.samples_file.close()
            self.corrections_file.close()
            self.misc_file.close()
        except Exception as e:
            print("Could not close files")
            print(e)

    def log_misc(self, msg: str):
        if time.time() - self.time_since_last_write > 15:
            self.close_files()
            self.open_files()
            self.time_since_last_write = time.time()
            print("Closed and opened files")

        try:
            self.misc_file.write(msg + "\n")
        except Exception as e:
            print(f"Could not log: {e}")

    def log_sample(self, sample: Sample) -> None:
        # This is so ugly
        template = """
-------
CORRECTION
TIME: {}
ISLAND_ID: {}
-------
{}

############################################################

"""

        try:
            self.corrections_file.write(
                template.format(
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    sample.island_id,
                    sample.code,
                )
            )
        except Exception as e:
            print(f"Could not log: {e}")

    def scored_sample(self, sample: Sample) -> None:
        # This is so ugly
        template = """
-------
TIME: {}
SCORE: {}
ISLAND_ID: {}
-------
{}

############################################################

"""

        try:
            self.samples_file.write(
                template.format(
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    sample.score,
                    sample.island_id,
                    sample.code,
                )
            )
        except Exception as e:
            print(f"Could not log: {e}")
