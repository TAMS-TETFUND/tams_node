import configparser
import os
from pathlib import Path
from typing import Any, Dict, Mapping, Optional
from typing_extensions import reveal_type


class AppConfigParser:
    """Implementation of a singleton to maintain the state of the
    parser across entire application.
    """
    __instance: Optional["AppConfigParser"] = None
    __initialized: bool = False

    def __new__(cls) -> "AppConfigParser":
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        if type(self).__initialized:
            return
        type(self).__initialized = True
        self.cp = ModifiedConfigParser()


class ModifiedConfigParser(configparser.ConfigParser):
    """An extension of the standard library's ConfigParser class."""
    CONFIG_FILE: str = os.path.join(
        Path(os.path.abspath(__file__)).parent,
        ("config.ini" if os.name != "posix" else ".config.ini"),
    )

    def __init__(self, file_path: Optional[str] = None):
        super(ModifiedConfigParser, self).__init__()
        self.config_file = file_path or self.CONFIG_FILE
        self.read(self.config_file)

    def __setitem__(self, key: str, value: Mapping[str, str]) -> None:
        """Set the value of an option in the configparser."""
        super().__setitem__(key, value)
        self.save()

    def remove_section(self, section: str) -> bool:
        """Delete a section of the configparser."""
        self[section] = {}
        self.save()
        return True

    def save(self) -> None:
        """Save configparser to config file."""
        with open(self.config_file, "w") as configfile:
            self.write(configfile)

    def section_dict(
        self, section: Any, no_default_section: bool = True
    ) -> Dict[str, str]:
        """Convert a section of the ConfigParser object to a dict."""
        section_dictionary = dict(self[section])
        if no_default_section:
            for key in self["DEFAULT"].keys():
                del section_dictionary[key]

        return section_dictionary

    @staticmethod
    def dict_vals_to_str(input_dict: Dict[str, Any]) -> Dict[str, str]:
        """Convert all values of a dictionary mapping to string.

        The configparser only supports str as valid values.
        """
        return {k: str(v) for k, v in input_dict.items()}
