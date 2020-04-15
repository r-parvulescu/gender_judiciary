"""
Functions for extracting data from the prosecutor employment roll .doc files.
"""

import re
from string import punctuation
from cleaning_tools import no_space_name_replacer, space_name_replacer
from transdicts import given_name_mistakes, given_name_diacritics, parquet_names, prosec_surname_replacers


def update_prosec_people_periods(people_periods, unit_lines, split_mark, year, month):
    """updates a list of people periods"""
    unit_name = get_parquet_name(unit_lines, split_mark)
    name_lines = get_parquet_name_lines(unit_lines)
    for nl in name_lines:
        name = nl[0]
        if name.upper().find('CRT') == -1:  # ignore dud lines
            full_name = get_prosecutor_names(name)
            if full_name is not None:
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
    if normal_text(text):
        # names in brackets are maiden names, part of surnames
        maiden_name = ''
        if re.search(r'\((.*?)\)', text):
            maiden_name = re.search(r'\((.*?)\)', text).group(0)
            text = text.replace(maiden_name, '').strip()
            maiden_name = ' ' + maiden_name.replace(' ', '')
        surnames = text[:text.find(' ') + 1].strip() + maiden_name
        # general clean-up
        given_names = text[text.find(' ') + 1:].replace('-', ' ').replace('NR', '')

        given_names = space_name_replacer(given_names, given_name_mistakes)
        given_names = no_space_name_replacer(given_names, given_name_diacritics)
        surnames = no_space_name_replacer(surnames, prosec_surname_replacers)
        surnames, given_names = problem_name_handler(surnames, given_names)
        if len(surnames) > 2:
            # get rid of multiple spaces
            surnames = ' '.join(surnames.split()).strip()
            given_names = ' '.join(given_names.split()).strip()
            return surnames, given_names


def prosec_multiline_name_catcher(people_periods):
    """cleans out certain known problems that slip through every other program"""
    for idx, val in enumerate(people_periods):
        if val[0][0] == '(':
            # handles this particular exception
            if val[1] == "TĂTARUOANA":
                people_periods[idx][0] = val[1][:6] + ' ' + people_periods[idx][0]
                people_periods[idx][1] = val[1][6:]
            # handles multiline name like
            # (APETROAIEI) CHINDEA
            # CODRUŢA SIMONA
            elif val[1] != '':
                people_periods[idx + 1][1] = people_periods[idx + 1][0] + ' ' + people_periods[idx + 1][1]
                people_periods[idx + 1][0] = people_periods[idx][1] + ' ' + people_periods[idx][0]
                people_periods[idx][0] = ''
            # handles multiline name like
            # DIMOFTE | RODICA MARLENA
            # (VASILE)
            else:
                people_periods[idx - 1][0] = people_periods[idx - 1][0] + ' ' + val[0]
                people_periods[idx][0] = ''
    return [i for i in people_periods if i[0] != '']


def get_parquet_name(lines, split_mark):
    """returns the name of the parquet"""
    # if first entries are empty, go until you hit something
    if not bool(re.match('^(?=.*[a-zA-Z])', lines[0])):
        lines = [l for l in lines if bool(re.match('^(?=.*[a-zA-Z])', l))]
    parquet_name = ''
    if lines:
        if re.search(r'ANTICORUPTIE|ANTICORUPŢIE', lines[0]) is not None:
            parquet_name = "DIRECŢIA NAŢIONALĂ ANTICORUPŢIE"
        elif re.search(r"INVESTIGARE", lines[0]) is not None:
            parquet_name = "DIRECŢIA DE INVESTIGARE A INFRACŢIUNILOR DE CRIMINALITATE ORGANIZATĂ ŞI TERORISM"
        elif re.search(r"ÎNALTA", lines[0]) is not None:
            parquet_name = "PARCHETUL DE PE LÂNGĂ ÎNALTA CURTE DE CASAŢIE ŞI JUSTIŢIE"
        elif "TRIBUNALUL PENTRU MINORI" in lines[0]:
            parquet_name = "PARCHETUL DE PE LÂNGĂ TRIBUNALUL PENTRU MINORI ŞI FAMILIE BRAŞOV"
        else:
            parquet_name = (split_mark + lines[0]).replace('|', '').strip()
            parquet_name = parquet_name.replace('-', ' ').translate(str.maketrans('', '', punctuation))
    parquet_name = parquet_name.replace('  ', ' ')
    if multiline_parquet_name(parquet_name):
        parquet_name = parquet_name + ' ' + lines[1].replace('|', '').strip()
    parquet_name = space_name_replacer(parquet_name, parquet_names)
    parquet_name = ' '.join(parquet_name.split()).strip()
    if parquet_name == "PARCHETUL DE PE LÂNGĂ JUDECĂTORIA ALBA":
        parquet_name = "PARCHETUL DE PE LÂNGĂ JUDECĂTORIA ALBA IULIA"
    return parquet_name


def normal_text(text):
    """returns True if common red flags are absent"""
    if (len(text) > 3) and ("LA DATA DE" not in text) and ("ÎNCEPÂND CU" not in text) \
            and ("CRIMINALITATE" not in text) and ("TÂRGU" not in text) and ("NUME" not in text) \
            and ("ORGANIZATĂ" not in text) and ("STABILITATE" not in text) and ("EXTERNE" not in text) \
            and ("CURTEA" not in text) and ("INFRACŢIUNILOR" not in text) and ("EUROPA" not in text) \
            and ("LÂNGĂ" not in text) and ("DIICOT" not in text) and ("DNA" not in text) \
            and ("PROCUROR" not in text) and ("JUDECĂTORIA" not in text) and ("CSM" not in text):
        return True
    else:
        return False


def multiline_parquet_name(parquet_name):
    """return True for common red flags that a parquet name goes across two lines"""
    if (parquet_name == "PARCHETUL DE") or \
            (parquet_name == "PARCHETUL DE PE") \
            or (parquet_name == "PARCHETUL DE PE LÂNGĂ") \
            or (parquet_name == "PARCHETUL DE PE LÂNGĂ JUDECĂTORIA") \
            or (parquet_name == "PARCHETUL DE PE LÂNGĂ TRIBUNALUL") \
            or (parquet_name == "PARCHETUL DE PE LÂNGĂ CURTEA") \
            or (parquet_name == "PARCHETUL DE PE LÂNGĂ CURTEA DE") \
            or (parquet_name == "PARCHETUL DE PE LÂNGĂ CURTEA DE APEL"):
        return True
    else:
        return False


def problem_name_handler(surnames, given_names):
    """there are some given names that mess things up; this returns usable names"""
    if given_names == "FLORESCU":
        given_names = surnames
        surnames = "FLORESCU"
    if ("HĂINEALĂ" in given_names) or ("SCHMIDT" in given_names):
        given_names = "OANA"
        surnames = "SCHMIDT HĂINEALĂ"
    if "RODRIGUES" in given_names:
        given_names = "CRISTINA"
        surnames = "MĂRINCEAN"
    if "ECEDI" in surnames:
        given_names = "STOISAVLEVICI LAURA"
    if "CANTEMIR" in given_names:
        surnames = "OPREA CANTEMIR"
        given_names = "ŞTEFĂNEL"
    if "MASSIMO" in given_names:
        given_names = "MARIO MASSIMO"
        surnames = "DEL CET"
    if "MELANOVSCHI" in given_names:
        surnames = "VARTOLOMEI MELANOVSCHI"
        given_names = "LIUDMILA"
    if "PĂCUREŢU" in given_names:
        surnames = "CANACHE PĂCUREŢU"
        given_names = "ION"
    if "ŞESTACHOVSCHI" in given_names:
        surnames = "ŞESTACHOVSCHI MOANGĂ"
        given_names = "SIMONA"
    if "EZRA" in given_names:
        surnames = "BEN EZRA"
        given_names = "CRISTINA DIANA"
    return surnames, given_names
