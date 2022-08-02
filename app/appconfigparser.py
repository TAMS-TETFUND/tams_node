import configparser
import os
from pathlib import Path


class AppConfigParser(configparser.ConfigParser):
    """An extension of the standard library's ConfigParser class for
    the project.
    """

    CONFIG_FILE = os.path.join(
        Path(os.path.abspath(__file__)).parent,
        ("config.ini" if os.name != "posix" else ".config.ini"),
    )

    def __init__(self, file_path=None):
        super(AppConfigParser, self).__init__()
        self.config_file = file_path or self.CONFIG_FILE
        self.read(self.config_file)

    def __setitem__(self, key: str, value) -> None:
        super().__setitem__(key, value)
        self.save()

    def remove_section(self, section: str) -> bool:
        result = super().remove_section(section)
        self.save()
        return result

    def save(self):
        with open(self.config_file, "w") as configfile:
            self.write(configfile)

    def section_dict(self, section, no_default_section=True):
        """Convert a section of the ConfigParser object to a
        dict."""
        section_dictionary = dict(self[section])
        if no_default_section:
            for key in self["DEFAULT"].keys():
                del section_dictionary[key]

        return section_dictionary

    @staticmethod
    def dict_vals_to_str(input_dict: dict):
        return {k: str(v) for k, v in input_dict.items()}
