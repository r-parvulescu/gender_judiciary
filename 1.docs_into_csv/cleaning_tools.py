"""
Functions that help clean data, for both prosecutor and judge .doc files.
"""

import re
from string import digits
from transdicts import court_sectors_buc, parquet_sectors_buc


def pre_clean(text, parquet):
    """remove some ad hoc strings causing known issues"""
    text = space_name_replacer(text, court_sectors_buc)  # Bucharest sectors, courts
    if parquet:
        text = space_name_replacer(text, parquet_sectors_buc)  # Bucharest sectors, parquets
    # # replace all "Î" in middle of word with "Â", remove digits, and problem characters
    text = re.sub(r'\BÎ+\B', r'Â', text)  # replace all "Î" in middle of word with "Â"
    text = text.translate(str.maketrans('', '', digits))
    text = text.translate(str.maketrans({'.': ' ', '–': ' ', '-': ' ', '/': ' ', "'": '', "Ț": "Ţ", "Ș": "Ş",
                                         "Ů": "Ţ", "ﾞ": "Ţ", "’": "Ţ", ";": "Ş", "Ř": "Ţ", "]": ' ', '[': ' ',
                                         '_': ' '}))
    return text


def multiline_name_contractor(people_periods):
    """catch exceptions, find multiline names, contracts them to one line, clean, and return all names"""
    for idx, val in enumerate(people_periods):
        if (val[0] == '') and (val[1] != 'NR') and (val[1] != 'PROCURORULUI') and (val[1] != "ILFOV") \
                and (val[1] != "TERORISM"):
            people_periods[idx - 1][1] = people_periods[idx - 1][1] + ' ' + people_periods[idx][1]
    return [i for i in people_periods if i[0] != '']


def space_name_replacer(text, dictio):
    """replaces all instances of dict key in text with corresponding dict value"""
    for key, value in dictio.items():
        if key in text:
            text = text.replace(key, value)
    return text


def no_space_name_replacer(text, dictio):
    """replaces all instances of dict key in text with corresponding dict value"""
    text_list = text.split()
    for t in text_list:
        if t in dictio:
            text = text.replace(t, dictio[t])
    return text
