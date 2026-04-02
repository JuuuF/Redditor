# Python module imports
import pickle
from pathlib import Path
from typing import Self, Any


# Class template to store and load the class state, as defined by its member variables
class ConfigLoadable:
    """
    Class template to store and load class instances, as defined by its member variables.
    """

    def __init__(self: Self, /, **kwargs: dict[str, Any]) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)

    def from_config(config_path: Path | str) -> Self:
        """
        Initialize an instance using a config file path.
        """
        with open(config_path, "rb") as f:
            configs = pickle.load(f)
        return ConfigLoadable(**configs)

    def get_config(self: Self) -> dict:
        """
        Get the configuration of the class instance.
        """
        return self.__dict__

    def save_config(self: Self, config_filepath: Path | str) -> None:
        """
        Save the config of the class instance to a file.
        """
        with open(config_filepath, "wb") as f:
            pickle.dump(self.get_config(), f)
