#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable, NamedTuple, Optional, Sequence
import os
import platform
import json

from pathlib import Path
from fontTools.ttLib import TTFont
from ezdxf.tools.fonts import FontFace

WINDOWS = "Windows"
LINUX = "Linux"
MACOS = "Darwin"


WIN_SYSTEM_ROOT = os.environ.get("SystemRoot", "C:/Windows")
WIN_FONT_DIRS = [
    # AutoCAD and BricsCAD do not support fonts installed in the user directory:
    "~/AppData/Local/Microsoft/Windows/Fonts",
    f"{WIN_SYSTEM_ROOT}/Fonts",
]
LINUX_FONT_DIRS = [
    "/usr/share/fonts",
    "/usr/local/share/fonts",
    "~/.fonts",
    "~/.local/share/fonts",
    "~/.local/share/texmf/fonts",
]
MACOS_FONT_DIRS = ["/Library/Fonts/"]
FONT_DIRECTORIES = {
    WINDOWS: WIN_FONT_DIRS,
    LINUX: LINUX_FONT_DIRS,
    MACOS: MACOS_FONT_DIRS,
}

DEFAULT_FONTS = [
    "Arial.ttf",
    "DejaVuSansCondensed.ttf",  # with of glyph similar to Arial
    "DejaVuSans.ttf",
    "LiberationSans-Regular.ttf",
    "OpenSans-Regular.ttf",
]


class CacheEntry(NamedTuple):
    file_path: Path
    font_face: FontFace


class FontCache:
    def __init__(self) -> None:
        # cache key is the lowercase ttf font name without parent directories
        # e.g. "arial.ttf" for "C:\Windows\Fonts\Arial.ttf"
        self._cache: dict[str, CacheEntry] = dict()

    def __getitem__(self, item: str) -> CacheEntry:
        return self._cache[self.key(item)]

    def __len__(self):
        return len(self._cache)

    @staticmethod
    def key(font_name: str) -> str:
        return str(font_name).lower()

    def add_entry(self, font_path: Path, font_face: FontFace) -> None:
        self._cache[self.key(font_path.name)] = CacheEntry(font_path, font_face)

    def get(self, font_name: str, fallback: str) -> CacheEntry:
        try:
            return self._cache[self.key(font_name)]
        except KeyError:
            return self._cache[self.key(fallback)]

    def loads(self, s: str) -> None:
        cache: dict[str, CacheEntry] = dict()
        for entry in json.loads(s):
            font_face = FontFace(*entry)
            path = Path(font_face.ttf)
            cache[FontCache.key(path.name)] = CacheEntry(path, font_face)
        self._cache = cache

    def dumps(self) -> str:
        return json.dumps([entry.font_face for entry in self._cache.values()], indent=2)


SUPPORTED_FONT_TYPES = {".ttf", ".ttc"}
NO_FONT_FACE = FontFace()


class FontNotFoundError(Exception):
    pass


class FontManager:
    def __init__(self) -> None:
        self.platform = platform.system()
        self._font_cache: FontCache = FontCache()
        self._loaded_fonts: dict[str, TTFont] = dict()
        self._fallback_font_name = ""

    def fallback_font_name(self) -> str:
        fallback_name = self._fallback_font_name
        if fallback_name:
            return fallback_name
        fallback_name = DEFAULT_FONTS[0]
        for name in DEFAULT_FONTS:
            try:
                cache_entry = self._font_cache.get(name, fallback_name)
                fallback_name = cache_entry.file_path.name
                break
            except KeyError:
                pass
        self._fallback_font_name = fallback_name
        return fallback_name

    def get_ttf_font(self, font_name: str, font_number: int = 0) -> TTFont:
        try:
            return self._loaded_fonts[font_name]
        except KeyError:
            pass
        fallback_name = self.fallback_font_name()
        try:
            font = TTFont(
                self._font_cache.get(font_name, fallback_name).file_path,
                fontNumber=font_number,
            )
        except IOError as e:
            raise FontNotFoundError(str(e))
        self._loaded_fonts[font_name] = font
        return font

    def ttf_font_from_font_face(self, font_face: FontFace) -> TTFont:
        return self.get_ttf_font(Path(font_face.ttf).name)

    def get_font_face(self, font_name: str) -> FontFace:
        cache_entry = self._font_cache.get(font_name, self.fallback_font_name())
        return cache_entry.font_face

    def build(self, folders: Optional[Sequence[str]] = None) -> None:
        """Adds all supported font types located in the given `folders` to the font
        manager. If no directories are specified, the known font folders for Windows,
        Linux and macOS are searched by default. Searches recursively all
        subdirectories.
        """
        if folders:
            dirs = list(folders)
        else:
            dirs = FONT_DIRECTORIES.get(self.platform, LINUX_FONT_DIRS)
        self.scan_all(dirs)
        if len(self._font_cache) == 0:  # System under test
            path = Path(__file__)
            fonts = path.parent.parent.parent.parent / "fonts"
            self.scan_folder(fonts)

    def scan_all(self, folders: Iterable[str]) -> None:
        for folder in folders:
            self.scan_folder(Path(folder).expanduser())

    def scan_folder(self, folder: Path):
        if not folder.exists():
            return
        for file in folder.iterdir():
            if file.is_dir():
                self.scan_folder(file)
                return
            ext = file.suffix.lower()
            if ext in SUPPORTED_FONT_TYPES:
                font_face = get_ttf_font_face(file)
                self._font_cache.add_entry(file, font_face)

    def dumps(self) -> str:
        return self._font_cache.dumps()

    def loads(self, s: str) -> None:
        self._font_cache.loads(s)


def get_ttf_font_face(font_path: Path) -> FontFace:
    try:
        ttf = TTFont(font_path, fontNumber=0)
    except IOError:
        return FontFace(ttf=str(font_path))

    names = ttf["name"].names
    family = ""
    style = ""
    for record in names:
        if record.nameID == 1:
            family = record.string.decode(record.getEncoding())
        elif record.nameID == 2:
            style = record.string.decode(record.getEncoding())
        if family and style:
            break
    os2_table = ttf["OS/2"]
    weight = get_weight_str(os2_table.usWeightClass)
    stretch = get_stretch_str(os2_table.usWidthClass)
    return FontFace(
        ttf=str(font_path),
        family=family,
        style=style,
        stretch=stretch,
        weight=weight,
    )


def get_weight_str(weight: int) -> str:
    # Determine the stretch value based on the usWidthClass field
    if weight < 350:
        return "Thin"
    elif weight < 450:
        return "Extra Light"
    elif weight < 550:
        return "Light"
    elif weight < 650:
        return "Regular"
    elif weight < 750:
        return "Medium"
    elif weight < 850:
        return "Semi Bold"
    elif weight < 950:
        return "Bold"
    elif weight < 1050:
        return "Extra Bold"
    return "Black"


def get_stretch_str(stretch: int) -> str:
    # Determine the stretch value based on the usWidthClass field
    if stretch < 3:
        return "Ultra Condensed"
    elif stretch < 4:
        return "Extra Condensed"
    elif stretch < 5:
        return "Condensed"
    elif stretch < 6:
        return "Semi Condensed"
    elif stretch < 9:
        return "Normal"
    elif stretch < 10:
        return "Semi Expanded"
    elif stretch < 11:
        return "Expanded"
    elif stretch < 12:
        return "Extra Expanded"
    return "Ultra Expanded"
