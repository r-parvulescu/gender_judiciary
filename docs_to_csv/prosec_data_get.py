"""
Functions for extracting data from the prosecutor employment roll .doc files.
"""

import re
from string import punctuation


def update_prosec_people_periods(people_periods, unit_lines, split_mark, year, month):
    """updates a list of people periods"""
    unit_name = get_parquet_name(unit_lines, split_mark)
    name_lines = get_parquet_name_lines(unit_lines)
    for nl in name_lines:
        name = nl[0]
        if name.upper().find('CRT') == -1:  # ignore dud lines
            full_name = get_prosecutor_names(name)
            people_periods.append([full_name[0], full_name[1], unit_name, year, month])


def get_parquet_name_lines(list_of_lines):
    """returns a list of clean-ish lines, each containing a name"""
    # a bunch of cleaning to isloate names
    clean_name_lines = []
    for line in list_of_lines[1:]:
        clean_line = list(filter(None, line.strip().replace('\xa0', '').splitlines()))
        for cl in clean_line:
            cleaner_line = list(filter(None, cl.split('|')))
            cleaner_line = list(filter(None, [clnr.strip() for clnr in cleaner_line[:-1]]))
            clean_name_lines.append(cleaner_line)
    return list(filter(None, clean_name_lines))


def get_prosecutor_names(text):
    """return a tuple with surname and given names"""
    # names in brackets are maiden names, part of surnames
    maiden_name = ''
    if re.search(r'\((.*?)\)', text):
        maiden_name = re.search(r'\((.*?)\)', text).group(0)
        text = text.replace(maiden_name, '').strip()
        maiden_name = ' ' + maiden_name.replace(' ', '')
    surnames = text[:text.find(' ') + 1].strip() + maiden_name
    given_names = text[text.find(' ') + 1:].replace('-', ' ')
    return surnames.strip(), given_names.strip().replace(' NR', '')


def get_parquet_name(lines, split_mark):
    """returns the name of the parquet"""
    # if first entries are empty, go until you hit something
    if not bool(re.match('^(?=.*[a-zA-Z])', lines[0])):
        lines = [l for l in lines if bool(re.match('^(?=.*[a-zA-Z])', l))]
    unit_name = ''
    if lines:
        if re.search(r'ANTICORUPTIE|ANTICORUPŢIE|Anticoruptie|Anticorupție|DNA', lines[0]) is not None:
            unit_name = "DIRECȚIA NAȚIONALĂ ANTICORUPȚIE"
        elif re.search(r"INVESTIGARE|Inverstigare|DIICOT", lines[0]) is not None:
            unit_name = "DIRECȚIA DE INVESTIGARE A INFRACȚIUNILOR DE CRIMINALITATE ORGANIZATĂ ȘI TERORISM"
        elif re.search(r"ÎNALTA|ICCJ", lines[0]) is not None:
            unit_name = "PARCHETUL DE PE LÂNGĂ ÎNALTA CURTE DE CASAȚIE ȘI JUSTIȚIE"
        else:
            unit_name = (split_mark + lines[0]).replace('|', '').strip()
            unit_name = unit_name.translate(str.maketrans('', '', punctuation))

    if (unit_name == "PARCHETUL DE") or \
            (unit_name == "PARCHETUL DE PE") \
            or (unit_name == "PARCHETUL DE PE LÂNGĂ") \
            or (unit_name == "PARCHETUL DE PE LÂNGĂ JUDECĂTORIA") \
            or (unit_name == "PARCHETUL DE PE LÂNGĂ TRIBUNALUL") \
            or (unit_name == "PARCHETUL DE PE LÂNGĂ CURTEA") \
            or (unit_name == "PARCHETUL DE PE LÂNGĂ CURTEA DE") \
            or (unit_name == "PARCHETUL DE PE LÂNGĂ CURTEA DE APEL"):
        unit_name = unit_name + ' ' + lines[1].replace('|', '').strip()
    return unit_name
