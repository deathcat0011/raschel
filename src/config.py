import jsonpickle as json  # type: ignore
from os import PathLike, path
import datetime
import logging


json.register(list, json.handlers.ArrayHandler)  # type: ignore
json.register(datetime.datetime, json.handlers.DatetimeHandler)  # type: ignore


class Time:
    def __init__(self, timestamp: datetime.datetime) -> None:
        self.time = timestamp

    def __repr__(self) -> str:
        return self.time.isoformat()


class Config:
    def __init__(
        self,
        vault_path: PathLike[str] | None = None,
        backup_from_patterns: (
            list[str] | None
        ) = None,  # glob patterns for files and dirs
        last_backup: datetime.datetime | str | None = None,
    ) -> None:
        self.vault_path = vault_path
        if vault_path and not path.exists(self.vault_path):  # type: ignore
            logging.error(f"Vault in {self.vault_path} does not exist")
            raise FileNotFoundError

        self.vault_path = vault_path  # TODO check wether the paths exist

        if isinstance(last_backup, datetime.datetime):
            self.last_backup = last_backup
        elif isinstance(last_backup, str):
            self.last_backup = datetime.datetime.fromisoformat(last_backup)  # type: ignore
        else:
            self.last_backup = datetime.datetime.now()

    def __setstate__(self, state: dict):  # type: ignore
        state.setdefault("vault_path")  # type: ignore
        state.setdefault("last_backup")  # type: ignore
        state.setdefault("backup_from_dirs")  # type: ignore
        self.__dict__.update(state)  # type: ignore


def load_config() -> Config | None:
    CONFIG_PATH = "config.json"

    if path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as file:
            data = file.read()
            ret = Config(**json.decode(data, classes=[Config, datetime.datetime], safe=True, on_missing="error"))  # type: ignore

            logging.info(f"Loaded Config from '{path.abspath(CONFIG_PATH)}'")
            return ret
    else:
        logging.info(f"Creating new config in '{path.abspath(CONFIG_PATH)}'")
        with open(CONFIG_PATH, "w") as file:
            file.write(json.encode(Config(), unpicklable=False, indent=4))  # type: ignore
