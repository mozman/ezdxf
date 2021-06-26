# Copyright (c) 2011-2021, Manfred Moitzi
# License: MIT License
from typing import TextIO, List
import os
import sys
from pathlib import Path
from configparser import ConfigParser

# The MATPLOTLIB global shows that Matplotlib is installed:
try:
    import matplotlib

    MATPLOTLIB = True
except ImportError:
    MATPLOTLIB = False

TRUE_STATE = {"True", "true", "On", "on", "1"}
CORE = "CORE"
DXF_STRUCTURE_BROWSER = "DXF STRUCTURE BROWSER"


def default_config() -> ConfigParser:
    config = ConfigParser()
    config[CORE] = {
        "TEST_FILES": "",
        "FONT_CACHE_DIRECTORY": "",
        "AUTO_LOAD_FONTS": "true",
        "LOAD_PROXY_GRAPHICS": "true",
        "STORE_PROXY_GRAPHICS": "true",
        "LOG_UNPROCESSED_TAGS": "true",
        "FILTER_INVALID_XDATA_GROUP_CODES": "true",
        "WRITE_FIXED_META_DATA_FOR_TESTING": "false",
        "DEFAULT_TEXT_STYLE": "OpenSans",
        "DEFAULT_DIMENSION_TEXT_STYLE": "OpenSansCondensed-Light",
    }
    config[DXF_STRUCTURE_BROWSER] = {
        "TEXT_EDITOR": r"C:\Program Files\Notepad++\notepad++.exe",
        "GOTO_LINE_ARGUMENT": "-n{num}",  # .format(num=line_number)
    }
    return config


def config_files(name: str = "ezdxf.ini") -> List[Path]:
    # Priority
    # 1. config file in EZDXF_CONFIG_FILE
    # 2. "ezdxf.ini" current working directory
    # 3. "ezdxf.ini" in home directory "~/.ezdxf"
    names = [
        Path(f"~/.ezdxf/{name}").expanduser(),
        Path(f"./{name}"),
    ]
    env_cfg = os.getenv("EZDXF_CONFIG_FILE", "")
    if env_cfg:
        names.append(Path(env_cfg))
    return names


def load_config_files(name: str = "ezdxf.ini") -> ConfigParser:
    config = default_config()
    config.read(config_files(name), encoding="utf8")

    # environment variables override config files
    for name, env_name in [("TEST_FILES", "EZDXF_TEST_FILES")]:
        value = os.environ.get(env_name, "")
        if value:
            config[CORE][name] = value
    return config


class Options:
    CONFIG_VARS = [
        "EZDXF_DISABLE_C_EXT",
        "EZDXF_TEST_FILES",
        "EZDXF_CONFIG_FILE",
    ]

    def __init__(self):
        self.config = load_config_files()
        # needs fast access:
        self.log_unprocessed_tags = self.config.getboolean(
            CORE, "LOG_UNPROCESSED_TAGS", fallback=True
        )

        # Activate/deactivate Matplotlib support (e.g. for testing)
        self._use_matplotlib = MATPLOTLIB

    @property
    def filter_invalid_xdata_group_codes(self):
        return self.config.getboolean(
            CORE, "FILTER_INVALID_XDATA_GROUP_CODES", fallback=True
        )

    @property
    def default_text_style(self):
        return self.config.get(CORE, "DEFAULT_TEXT_STYLE", fallback="OpenSans")

    @property
    def default_dimension_text_style(self):
        # Set path to an external font cache directory: e.g. "~/ezdxf", see
        # docs for ezdxf.options for an example how to create your own
        # external font cache:
        return self.config.get(
            CORE,
            "DEFAULT_DIMENSION_TEXT_STYLE",
            fallback="OpenSansCondensed-Light",
        )

    @property
    def font_cache_directory(self):
        return self.config.get(CORE, "FONT_CACHE_DIRECTORY", fallback="")

    @property
    def test_files(self):
        return self.config.get(CORE, "TEST_FILES", fallback="")

    @property
    def load_proxy_graphics(self):
        return self.config.getboolean(
            CORE, "LOAD_PROXY_GRAPHICS", fallback=True
        )

    @property
    def store_proxy_graphics(self):
        return self.config.getboolean(
            CORE, "STORE_PROXY_GRAPHICS", fallback=True
        )

    @property
    def write_fixed_meta_data_for_testing(self):
        # Enable this option to always create same meta data for testing
        # scenarios, e.g. to use a diff like tool to compare DXF documents.
        return self.config.getboolean(
            CORE, "WRITE_FIXED_META_DATA_FOR_TESTING", fallback=False
        )

    @property
    def auto_load_fonts(self):
        # Set "AUTO_LOAD_FONTS=false" to deactivate auto font loading,
        # if this this procedure slows down your startup time and font measuring is not
        # important to you. Fonts can always loaded manually: ezdxf.fonts.load()
        return self.config.getboolean(
            CORE, "AUTO_LOAD_FONTS", fallback=True
        )

    @property
    def use_matplotlib(self) -> bool:
        """Activate/deactivate Matplotlib support e.g. for testing"""
        return self._use_matplotlib

    @use_matplotlib.setter
    def use_matplotlib(self, state: bool) -> None:
        if MATPLOTLIB:
            self._use_matplotlib = state
        else:  # Matplotlib is not installed
            self._use_matplotlib = False

    def preserve_proxy_graphics(self, state: bool = True) -> None:
        """Enable/disable proxy graphic load/store support."""
        value = "true" if state else "false"
        self.config.set(CORE, "LOAD_PROXY_GRAPHICS", value)
        self.config.set(CORE, "STORE_PROXY_GRAPHICS", value)

    def write(self, fp: TextIO) -> None:
        """Write current configuration into given file object, the file object
        must be a writeable text file with 'utf8' encoding.
        """
        self.config.write(fp)

    def print(self):
        """Print current configuration to `stdout`. """
        self.config.write(sys.stdout)

    def write_home_config(self):
        """Write current configuration into file "~/.ezdxf/ezdxf.ini". """
        p = Path("~/.ezdxf").expanduser()
        if not p.exists():
            p.mkdir()

        with open(p / "ezdxf.ini", "wt", encoding="utf8") as fp:
            self.write(fp)
        print(f'ezdxf configuration written to file: "{fp.name}"')


# Global Options
options = Options()
