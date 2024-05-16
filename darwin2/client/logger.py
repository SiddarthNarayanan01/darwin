from os import path
import time
from datetime import datetime
from darwin2.evolving.samples import Sample


class Logger:
    def __init__(self, base_path: str) -> None:
        self.base_path = base_path
        self.last_save = time.time()
        self.samples_file = path.join(base_path, "samples.log")
        self.corrections_file = path.join(base_path, "corrections.log")
        self.misc_file = path.join(base_path, "misc.log")

    def log_misc(self, msg: str):
        try:
            with open(self.misc_file, "a+") as f:
                f.write(msg + "\n")
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
            with open(self.corrections_file, "a+") as f:
                f.write(
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
            with open(self.samples_file, "a+") as f:
                f.write(
                    template.format(
                        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        sample.score,
                        sample.island_id,
                        sample.code,
                    )
                )
        except Exception as e:
            print(f"Could not log: {e}")
