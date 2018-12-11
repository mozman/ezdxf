# Purpose: constant values
# Created: 10.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License

codepage_to_encoding = {
    '874': 'cp874',  # Thai,
    '932': 'cp932',  # Japanese
    '936': 'gbk',  # UnifiedChinese
    '949': 'cp949',  # Korean
    '950': 'cp950',  # TradChinese
    '1250': 'cp1250',  # CentralEurope
    '1251': 'cp1251',  # Cyrillic
    '1252': 'cp1252',  # WesternEurope
    '1253': 'cp1253',  # Greek
    '1254': 'cp1254',  # Turkish
    '1255': 'cp1255',  # Hebrew
    '1256': 'cp1256',  # Arabic
    '1257': 'cp1257',  # Baltic
    '1258': 'cp1258',  # Vietnam
}

encoding_to_codepage = {
    codec: ansi for ansi, codec in codepage_to_encoding.items()
    }


def is_supported_encoding(encoding: str='cp1252') -> bool:
    return encoding in encoding_to_codepage


def toencoding(dxfcodepage: str) -> str:
    for codepage, encoding in codepage_to_encoding.items():
        if dxfcodepage.endswith(codepage):
            return encoding
    return 'cp1252'


def tocodepage(encoding: str) -> str:
    return 'ANSI_' + encoding_to_codepage.get(encoding, '1252')

