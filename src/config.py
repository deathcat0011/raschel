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
    """
    A class representing a configuration.

    Attributes:
    - `vault_path (PathLike[str] | None)`: Optional path to the configuration vault.
    - `backup_from_patterns (list[str] | None)`: Optional list of glob patterns for files and directories to be backed up.
    - `last_backup (datetime.datetime | str | None)`: Optional timestamp or string representation of a timestamp for the last successful backup.

    Methods:
    - `__init__(self, vault_path: PathLike[str] | None = None, backup_from_patterns: (list[str] | None) = None, last_backup: datetime.datetime | str | None = None) -> None:` Initializes a Config object with the given attributes.
    - `__setstate__(self, state: dict):` Updates the state of the Config object.

    """

    def __init__(
        self,
        vault_path: PathLike[str] | None = None,
        backup_from_patterns: (
            list[str] | None
        ) = None,  # glob patterns for files and dirs
        last_backup: datetime.datetime | str | None = None,
    ) -> None:
        """
        Parameters:
        - `vault_path`: Optional path to the configuration vault (`str` or `PathLike[str]`)
        - `backup_from_patterns`: Optional list of glob patterns for files and directories to be backed up (`list[str]` or `None`)
        - `last_backup`: Optional timestamp or string representation of a timestamp for the last successful backup (`datetime.datetime`, `str`, or `None`)

        Raises `FileNotFoundError` if vault_path does not exist.
        Sets default values for `last_backup` and initializes `self.__dict__` from state dictionary during unpickling.
        """
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


# Load and parse configuration from JSON file or create new one if it does not exist.
def load_config() -> Config | None:
    """
    Opens a file named "config.json". If the file exists,
    it reads the content and decodes it into a Config object. If the file does not exist,
    it creates a new Config object with default values and writes it to the file.
    """
    CONFIG_PATH = "config.json"
    if path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as file:
                data: str = file.read()
                try:
                    ret = Config(**json.decode(data, classes=[Config, datetime.datetime], safe=True, on_missing="error"))  # type: ignore
                    logging.info(f"Loaded config from '{path.abspath(CONFIG_PATH)}'")
                    return ret
                except Exception as e:
                    logging.error(f"Error decoding Config: {e}")
        except Exception as e:
            logging.error(f"Error reading config file: {e}")
        else:
            logging.info(f"Creating new config in '{path.abspath(CONFIG_PATH)}'")
            with open(CONFIG_PATH, "w") as file:
                file.write(json.encode(Config(), unpicklable=False, indent=4))  # type: ignore
