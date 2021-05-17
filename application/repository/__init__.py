import json
import logging
import os

logger = logging.getLogger(__name__)


class JSONPersistence:

    base_path = os.path.dirname(os.path.abspath(__file__)) + "/.."

    @classmethod
    def save(cls, _dict, filename):
        with open(f"{filename}.json", "w") as out_file:

            try:
                json.dump(_dict, out_file, indent=6)
                logger.info("new json file saved, %s", out_file.name)
            except Exception:
                logger.exception("error while saving new json file %s", filename)
            finally:
                out_file.close()

            return True
