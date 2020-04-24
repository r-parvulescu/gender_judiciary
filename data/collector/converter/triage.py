"""
This code process (cleaned) files containing the monthly employment rolls of all judges and prosecutors
in all Romanian courts and prosecutors' offices (a.k.a. "parquets") and spits out a csv (on each for
judges and prosecutors) of person-periods, here person-months. The columns are surnamaes, given names,
court/parquet, year, and month. All files are in the legacy .doc (1997-2003) format.
NB: the data that came from scrape_csm_old.py were extensively cleaned (by hand and ad hoc) before
being passed here, because of a number of problems with the underlying data itself, often input
problems. These scripts WILL NOT work with the raw data files from scrape_csm_old.py.
Author of Python Code:
    Pârvulescu, Radu Andrei (2020)
    rap348@cornell.edu
"""

import textract
import re
from collector.converter.get_prosecs import update_prosec_people_periods, prosec_multiline_name_catcher
from collector.converter.get_judges import update_judge_people_periods
from collector.converter import cleaners


# TODO make it work from just memory so you don't have to unzip anything


def triage(filepath, parquet):
    """depending on the file-type invoke different processing tools; return cleaner text, year, and month"""
    year, month = get_year_month(filepath)
    print(year, month)
    # extract text, capitalise, and pre-clean
    cleaner_text = cleaners.pre_clean(textract.process(filepath).decode('utf-8').upper(), parquet)
    # treat files of military units separately, have different structure
    if get_military_data(cleaner_text):  # handle military courts/parquets separately
        return None, None, None
    if get_prosec_pdf_data(filepath):
        return None, None, None
    return cleaner_text, year, month


def get_doc_data(text, year, month, prosecs=False):
    """return a tuple with unit name (viz. Court X), surname, and given names"""
    split_mark = 'PARCHETUL ' if prosecs else 'JUDECĂTORIA |JUDECATORIA |TRIBUNALUL |CURTEA DE APEL'
    people_periods = []
    units = re.split(split_mark, text)
    for u in units:
        unit_lines = list(filter(None, u.splitlines()))
        if len(unit_lines) > 1:
            if prosecs:
                update_prosec_people_periods(people_periods, unit_lines, split_mark, year, month)
            else:
                update_judge_people_periods(people_periods, unit_lines, text, year, month)
    people_periods = cleaners.multiline_name_contractor(people_periods)
    if prosecs:
        people_periods = prosec_multiline_name_catcher(people_periods)
    return people_periods


# TODO write function to get data from military court/parquet employment rolls
def get_military_data(text):
    # detect if it's data from the miliitary courts/parquets
    military = (re.search(r'PARCHETELOR MILITARE|PARCHETELE MILITARE|PARCHETUL MILITAR', text)
                is not None) or (re.search(r'CURTEA MILITAR|TRIBUNALUL MILITAR', text) is not None)
    return military


# TODO write function to get prosecutor data from pdf files
def get_prosec_pdf_data(filepath):
    # detect if it's data from a pdf file
    return True if filepath[-3] == 'pdf' else False


def get_year_month(filepath):
    """"return the year and month from a filepath"""
    year_month = re.search(r'/([0-9].+)/', filepath).group(1)
    year, month = year_month.split('/')[0], year_month.split('/')[1]
    return year, month
