import json
import logging


logger = logging.getLogger(__name__)


class JSONPersistence: 

    @classmethod
    def save(self, _dict, filename):
        out_file = open(f"./json_outputs/{filename}.json", "w")

        try:
            json.dump(_dict, out_file, indent=6)
            logger.info("new json file saved, .json_outputs/%s", out_file.name)
        except Exception:
            logger.exception("error while saving new json file %s", filename)
        finally:
            out_file.close()

        return True
         
