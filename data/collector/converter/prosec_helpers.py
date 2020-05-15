"""
Functions for extracting data from the prosecutor employment roll .doc files.
"""

import re
import string
from collector.converter import cleaners


def update_prosec_people_periods(people_periods, unit_lines, split_mark, year, month):
    """updates a list of people periods"""
    parquet_name = get_parquet_name(unit_lines, split_mark)
    # get the clean-ish lines that actually contain peoples' names
    name_lines = get_person_name_lines(unit_lines)
    for nl in name_lines:
        name = nl[0]
        if name.upper().find('CRT') == -1:  # ignores this common dud line
            full_name = get_prosecutor_names(name)
            if full_name is not None:
                people_periods.append([full_name[0], full_name[1], parquet_name, year, month])


def get_person_name_lines(unit_lines):
    """returns a list of clean-ish lines, each containing a prosecutor's name"""
    # a bunch of cleaning to isloate names
    clean_name_lines = []
    for line in unit_lines[1:]:
        clean_line = list(filter(None, line.strip().replace('\xa0', '').splitlines()))
        for cl in clean_line:
            cleaner_line = list(filter(None, cl.split('|')))
            cleaner_line = list(filter(None, [cl.strip() for cl in cleaner_line[:-1]]))
            clean_name_lines.append(cleaner_line)
    return list(filter(None, clean_name_lines))


def get_prosecutor_names(fullname):
    """given a string with the full name, return a tuple with surname and given names"""
    if normal_text(fullname):
        surnames, given_names = maiden_name_corrector(fullname)
        return prosec_name_clean(surnames, given_names)


def prosec_name_clean(surnames, given_names):
    """
    run surnames and given names through cleaners, return neater versions
    if fullname is not an empty string
    """
    # follow current orthographic rules and replace all "Î" in middle of word with "Â
    given_names = re.sub(r'\BÎ+\B', r'Â', given_names)
    surnames = re.sub(r'\BÎ+\B', r'Â', surnames)
    # got to cedilla diacritics
    given_names = given_names.replace('Ț', 'Ţ').replace('Ș', 'Ş')
    surnames = surnames.replace('Ț', 'Ţ').replace('Ș', 'Ş')
    # the NR bit eliminates a common parsing error
    given_names = cleaners.space_name_replacer(given_names, cleaners.given_name_mistakes).replace('NR', '')
    given_names = cleaners.no_space_name_replacer(given_names, cleaners.given_name_diacritics)
    surnames = cleaners.no_space_name_replacer(surnames, cleaners.prosec_surname_replacers)
    surnames, given_names = problem_name_handler(surnames, given_names)
    if len(surnames) > 2:
        # no outside spaces, no space more than one long
        surnames = ' '.join(surnames.split()).strip()
        given_names = ' '.join(given_names.split()).strip()
        return surnames, given_names


def maiden_name_corrector(fullname):
    """
    sometimes maiden names are put in brackets and are incorrectly in the given name field
    return maiden name at end of surname, with clean given name
    """
    maiden_name = ''
    # names in brackets are maiden names
    if re.search(r'\((.*?)\)', fullname):
        maiden_name = re.search(r'\((.*?)\)', fullname).group(0)  # isolate maiden name
        fullname = fullname.replace(maiden_name, '').strip()  # take maiden name out of fullname
        maiden_name = ' ' + maiden_name.replace(' ', '')  # clean up the maiden name
    # put maiden name after surname, isolate given names, eliminating hyphens
    surnames = fullname[:fullname.find(' ') + 1].strip() + maiden_name
    given_names = fullname[fullname.find(' ') + 1:].replace('-', ' ')
    return surnames, given_names


def prosec_multiline_name_catcher(people_periods):
    """catches and handles multiline and/or type names that slip through other functions"""
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
            parquet_name = parquet_name.replace('-', ' ').translate(str.maketrans('', '', string.punctuation))
    parquet_name = parquet_name.replace('  ', ' ')
    if multiline_parquet_name(parquet_name):
        parquet_name = parquet_name + ' ' + lines[1].replace('|', '').strip()
    parquet_name = cleaners.space_name_replacer(parquet_name, cleaners.parquet_names)
    parquet_name = ' '.join(parquet_name.split()).strip()
    if parquet_name == "PARCHETUL DE PE LÂNGĂ JUDECĂTORIA ALBA":
        parquet_name = "PARCHETUL DE PE LÂNGĂ JUDECĂTORIA ALBA IULIA"
    return parquet_name


def multiline_parquet_name(parquet_name):
    """return True if red flags of multiline parquet name are present; if True, we can contract name across lines"""
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


# I don't use below in this module since it messes up order of operations, used in from_xlsx.py
def parquet_name_cleaner(parquet_name):
    """returns parquet name that's gone through several cleaners"""
    parquet_name = parquet_name.translate(str.maketrans('', '', string.punctuation))
    parquet_name = parquet_name.replace('-', ' ').replace('  ', ' ')
    parquet_name = cleaners.space_name_replacer(parquet_name, cleaners.parquet_sectors_buc)  # parquet = row[2]
    parquet_name = cleaners.space_name_replacer(parquet_name, cleaners.parquet_names)
    parquet_name = ' '.join(parquet_name.split()).strip()
    return parquet_name


def normal_text(text):
    """returns True if red flags of misprocessed name are absent; if False, we can ignore the line containing them"""
    if (len(text) > 3) and ("LA DATA DE" not in text) and ("ÎNCEPÂND CU" not in text) \
            and ("CRIMINALITATE" not in text) and ("TÂRGU" not in text) and ("NUME" not in text) \
            and ("ORGANIZATĂ" not in text) and ("STABILITATE" not in text) and ("EXTERNE" not in text) \
            and ("CURTEA" not in text) and ("INFRACŢIUNILOR" not in text) and ("EUROPA" not in text) \
            and ("LÂNGĂ" not in text) and ("DIICOT" not in text) and ("DNA" not in text) \
            and ("PROCUROR" not in text) and ("JUDECĂTORIA" not in text) and ("CSM" not in text):
        return True
    else:
        return False


def problem_name_handler(surnames, given_names):
    """some names are frequently input wrong in the base data file; this function handles them ad-hoc"""
    if given_names == "FLORESCU":
        given_names, surnames = surnames, "FLORESCU"
    if ("HĂINEALĂ" in given_names) or ("SCHMIDT" in given_names):
        given_names, surnames = "OANA", "SCHMIDT HĂINEALĂ"
    if "RODRIGUES" in given_names:
        given_names, surnames = "CRISTINA", "MĂRINCEAN"
    if "ECEDI" in surnames:
        given_names = "STOISAVLEVICI LAURA"
    if "CANTEMIR" in given_names:
        given_names, surnames = "ŞTEFĂNEL", "OPREA CANTEMIR"
    if "MASSIMO" in given_names:
        given_names, surnames = "MARIO MASSIMO", "DEL CET"
    if "MELANOVSCHI" in given_names:
        given_names, surnames = "LIUDMILA", "VARTOLOMEI MELANOVSCHI"
    if "PĂCUREŢU" in given_names:
        given_names, surnames = "ION", "CANACHE PĂCUREŢU"
    if "ŞESTACHOVSCHI" in given_names or 'ŞESTACOVSCHI' in given_names:
        given_names, surnames = "SIMONA", "ŞESTACHOVSCHI MOANGĂ"
    if "EZRA" in given_names:
        given_names, surnames = "CRISTINA DIANA", "BEN EZRA"
    if "DUMITRESCU" in surnames and "CHIŞCAN" in surnames:
        given_names, surnames = "LUMINIŢA", "NICOLESCU (DUMITRESCU CHIŞCAN)"
    if given_names == "COLŢ":
        given_names, surnames = 'MIHAI', "COLŢ"
    return surnames, given_names


def pdf_get_special_parquets(file_path):
    """
    The .pdf files have parquet name written ONLY in their file path; look there.
    DNA, PICCJ, and DIICOT are special: they're either at the top of the hierarchy, or form a semi-parallel system
    :param file_path: string, path to .pdf file containing prosecutor employment rolls
    :return string, standardised name of special parquet
    """

    if "DNA" in file_path:
        special_parquet = "DIRECŢIA NAŢIONALĂ ANTICORUPŢIE"
    elif "DIICOT" in file_path:
        special_parquet = "DIRECŢIA DE INVESTIGARE A INFRACŢIUNILOR DE CRIMINALITATE ORGANIZATĂ ŞI TERORISM"
    elif "PICCJ" in file_path:
        special_parquet = "PARCHETUL DE PE LÂNGĂ ÎNALTA CURTE DE CASAŢIE ŞI JUSTIŢIE"
    else:
        special_parquet = ''
    return special_parquet


def pdf_get_parquet(row):
    """
    The .pdf files have parquet name written ONLY in their file path; look there.
    :param row: row of person-period table, as parsed by collector.converter.convert.get_pdf_people_periods
    :return: string, standardised name of row's parquet
    """

    if row[-1] != '':
        parquet = "PARCHETUL DE PE LÂNGĂ JUDECĂTORIA " + row[-1].upper().strip()
    elif row[-2] != '':
        parquet = row[-2].upper().strip().replace("PT", "PARCHETUL DE PE LÂNGĂ TRIBUNALUL")
    elif row[-3] != '':
        parquet = row[-3].upper().strip().replace("PCA", "PARCHETUL DE PE LÂNGĂ CURTEA DE APEL")
    else:
        parquet = 'ERROR'
    return parquet
