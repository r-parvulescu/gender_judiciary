"""
Functions that help clean data, for both prosecutor and judge .doc files.
"""

from string import digits
from transdicts import court_sectors_buc, parquet_sectors_buc


def pre_clean(text, parquet):
    """remove some ad hoc strings causing known issues"""
    text = multi_char_replacer(text, court_sectors_buc)  # Bucharest sectors, courts
    if parquet:
        text = multi_char_replacer(text, parquet_sectors_buc)  # Bucharest sectors, parquets
    # remove digits, and some characters
    text = text.translate(str.maketrans('', '', digits))
    text = text.translate(str.maketrans({'.': ' ', '–': ' ', '-': ' ', '/': ' ', "'": '', "Ț": "Ţ", "Ș": "Ş",
                                         "Ů": "Ţ", "ﾞ": "Ţ", "’": "Ţ", ";": "Ş", "Ř": "Ţ"}))
    return text


def multiline_name_contractor(people_periods):
    """catch exceptions, find multiline names, contracts them to one line, clean, and return all names"""
    for idx, val in enumerate(people_periods):
        if (val[0] == '') and (val[1] != 'NR') and (val[1] != 'PROCURORULUI') and (val[1] != "ILFOV") \
                and (val[1] != "TERORISM"):
            people_periods[idx - 1][1] = people_periods[idx - 1][1] + ' ' + people_periods[idx][1]
    return [i for i in people_periods if i[0] != '']


def multi_char_replacer(text, dictio):
    """replaces all instances of dict key in text with corresponding dict value"""
    for key, value in dictio.items():
        if key in text:
            text = text.replace(key, value)
    return text
