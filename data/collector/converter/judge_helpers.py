"""
Functions for extracting data from the judge employment roll .doc files.
"""

import re
import string
from collector.converter import cleaners


def update_judge_people_periods(people_periods, unit_lines, text, year, month):
    """
    updates a list of people periods
    :param people_periods: a list of people period
    :param unit_lines: a list of lines associated with a certain unit, e.g. a court
                       typically the first lines contain the name of the unit (e.g. Court X) and
                       subsequent lines contain the names of employees, usually one employee per line
    :param text: the full text from the .doc file
    :param year: the year of the employment roll
    :param month: the month of the employment roll
    """
    court_name = get_court_name(unit_lines)
    names = get_judges_names(unit_lines, text)
    if names is not None:
        for n in names:
            people_periods.append([n[0], n[1], court_name, year, month])


def get_judges_names(unit_lines, text):
    """
    return the names of judges
    :param unit_lines: a list of lines associated with a certain unit, e.g. a court
    :param text: the full text from the .doc file
    """
    names = []
    names_start_idx = find_name_start(unit_lines)
    if names_start_idx is not None:
        unit_lines = unit_lines[names_start_idx:]
        if '\xa0' in text:  # mark of three-column file
            three_col_name_getter(unit_lines, names)
        else:  # two-column file
            two_col_name_getter(unit_lines, names)
        for name in names:
            name[0], name[1] = judge_name_clean(name[0], name[1])
        return names


def judge_name_clean(surnames, given_names):
    """return surnames and given names that have been run through cleaners"""
    # follow current orthographic rules and replace all "Î" in middle of word with "Â
    given_names = re.sub(r'\BÎ+\B', r'Â', given_names)
    surnames = re.sub(r'\BÎ+\B', r'Â', surnames)
    surnames, given_names = maiden_name_corrector(surnames, given_names)
    surnames = cleaners.no_space_name_replacer(surnames, cleaners.judges_surname_replacers).replace('.', '')
    given_names = cleaners.space_name_replacer(given_names, cleaners.given_name_mistakes)
    given_names = cleaners.no_space_name_replacer(given_names, cleaners.given_name_diacritics).replace('.', '')
    return problem_person_name_handler(surnames, given_names)


def maiden_name_corrector(surnames, given_names):
    """if a maiden name is in a given name, moves it to the end of the surname"""
    maiden_name = ''
    # names in brackets are maiden names
    if re.search(r'\((.*?)\)', given_names):
        maiden_name = re.search(r'\((.*?)\)', given_names).group(0)  # isolate maiden name
        given_names = given_names.replace(maiden_name, '').strip()  # take maiden name out of fullname
        maiden_name = ' ' + maiden_name.replace(' ', '')  # clean up the maiden name
    # put maiden name after surname, isolate given names, eliminating hyphens
    surnames = surnames + maiden_name
    return surnames, given_names


def two_col_name_getter(list_of_lines, names):
    """
    some of the .doc files come in two (2) columns
    this function returns judge names from such two-column files
    """
    for idx, val in enumerate(list_of_lines):
        if bool(re.match('^(?=.*[a-zA-Z])', val)):
            name_line = val.split('|')
            name_line = [l for l in name_line if bool(re.match('^(?=.*[a-zA-Z])', l))]
            if len(name_line) < 2:  # name spilled over onto next line, put it to last name and skip
                if name_line[0] == 'CRT' or len(name_line[0]) < 2:
                    continue
                names[idx - 1][1] = names[idx - 1][1] + ' ' + name_line[0]
                continue
            name_line = [' '.join(n.split()).strip() for n in name_line]
            names.append(name_line)


def three_col_name_getter(list_of_lines, names):
    """
    some of the .doc files come in three (3) columns
    this function returns judge names from such three-column files
    """
    for l in list_of_lines:
        name_line = list(filter(None, l.split('|')))
        name_line = list(filter(None, [n.strip() for n in name_line]))
        name_line = [' '.join(n.split()).strip() for n in name_line]
        name_line = name_line[:2] if len(name_line) > 2 else name_line
        if len(name_line) > 1:
            names.append(name_line)


def find_name_start(list_of_lines):
    """return the index at which the person names begin"""
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
    # catch multiline court names
    if "RAZA" in court_name:
        line = [lines[0].replace('|', '').strip() + lines[1].replace('|', '').strip()]
        court_name = get_court_name(line)
    return court_name_cleaner(court_name)


def court_name_cleaner(court_name):
    """returns court name that's gone through several cleaners"""
    # deal with the commercial and specialised "courts", which are actually tribunals
    if ("COMERCIAL M" in court_name) or ("SPECIALIZAT M" in court_name):
        court_name = court_name.replace("JUDECĂTORIA", "TRIBUNALUL")
    court_name = court_name.translate(str.maketrans('', '', string.punctuation))
    court_name = ' '.join(court_name.split()).strip()  # reduces whitespace to one space
    court_name = cleaners.space_name_replacer(court_name, cleaners.court_sectors_buc)
    court_name = cleaners.space_name_replacer(court_name, cleaners.court_names)
    # catch this non-standard name which slips through every other filter (very frustrating)
    if court_name == 'JUDECĂTORIA RM VÂLCEA':
        court_name = "JUDECĂTORIA RÂMNICU VÂLCEA"
    return court_name


def problem_person_name_handler(surnames, given_names):
    """
    some names mess things up and slip through every other filter
    this function catches them and return the proper variant
    """
    if "AND ONE" in surnames:
        surnames = "ANDONE"
    if "FOSTĂ" in surnames:
        surnames = surnames.replace("( FOSTĂ ", '(')
        surnames = surnames.replace("(FOSTĂ ", '(')
    if 'FOSTA' in surnames:
        surnames = surnames.replace('( FOSTA ', '(')
    return surnames.strip(), given_names.strip()
