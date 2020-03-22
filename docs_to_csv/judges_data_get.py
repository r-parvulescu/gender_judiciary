"""
Functions for extracting data from the judge employment roll .doc files.
"""

import re


def update_judge_people_periods(people_periods, unit_lines, text, year, month):
    """updates a list of people periods"""
    court_name = get_court_name(unit_lines)
    names = get_judges_names(unit_lines, text)
    if names is not None:
        for n in names:
            people_periods.append([n[0], n[1], court_name, year, month])


def get_judges_names(list_of_lines, text):
    """return the names of judges"""
    names = []
    names_start_idx = find_name_start(list_of_lines)
    if names_start_idx is not None:
        list_of_lines = list_of_lines[names_start_idx:]
        if '\xa0' in text:  # mark of three-column file
            three_col_name_getter(list_of_lines, names)
        else:  # two-column file
            two_col_name_getter(list_of_lines, names)
        return names


def two_col_name_getter(list_of_lines, names):
    """returns judge names from two-column data files"""
    for idx, val in enumerate(list_of_lines):
        if bool(re.match('^(?=.*[a-zA-Z])', val)):
            name_line = val.split('|')
            name_line = [l for l in name_line if bool(re.match('^(?=.*[a-zA-Z])', l))]
            name_line = [l.replace(' - ', ' ').replace(' -', ' ').replace('-', ' ').strip() for l in name_line]
            if len(name_line) < 2:  # name spilled over onto next line, put it to last name and skip
                if name_line[0] == 'CRT':
                    continue
                if len(name_line[0]) < 2:
                    continue
                names[idx - 1][1] = names[idx - 1][1] + ' ' + name_line[0]
                continue
            names.append(name_line)


def three_col_name_getter(list_of_lines, names):
    """returns judge names from three-column data files"""
    for l in list_of_lines:
        name_line = list(filter(None, l.split('|')))
        name_line = list(filter(None, [n.strip() for n in name_line]))
        name_line = name_line[:2] if len(name_line) > 2 else name_line
        if len(name_line) > 1:
            names.append(name_line)


def find_name_start(list_of_lines):
    """return the index of the list of lines at which the first name starts"""
    if bool(re.match('^(?=.*[a-zA-Z])', ''.join(list_of_lines))):  # ignore empties
        try:  # names proper usually  start after "CRT"
            names_start_idx = (next((idx for idx, val in enumerate(list_of_lines) if "CRT" in val))) + 1
        except StopIteration:  # or after first entry, which is name of court
            names_start_idx = (next((idx for idx, val in enumerate(list_of_lines)
                                     if bool(re.match('^(?=.*[a-zA-Z])', val))))) + 1
        return names_start_idx


def get_court_name(lines):
    """return the name of the court"""
    in_line_split = '(' if '(' in lines[0] else 'DIN'
    if ("CURŢII" in lines[0]) or ("CURTII" in lines[0]):
        court_name = "TRIBUNALUL " + lines[0][:lines[0].find(in_line_split)]
    elif ("TRIBUNALULUI" in lines[0]) or ("TRIBUNALUI" in lines[0]):
        court_name = "JUDECĂTORIA " + lines[0][:lines[0].find(in_line_split)]
    elif ("ÎNALTA" in lines[0]) or ("INALTA" in lines[0]):
        court_name = 'ÎNALTA CURTE DE CASAŢIE ŞI JUSTIŢIE'
    else:
        court_name = "CURTEA DE APEL " + lines[0].replace('|', '').strip()

    # catch multiline names
    if "RAZA" in court_name:
        line = [lines[0].replace('|', '').strip() + lines[1].replace('|', '').strip()]
        court_name = get_court_name(line)

    return court_name.replace('  ', ' ')
