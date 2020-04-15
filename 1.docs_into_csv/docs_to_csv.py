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

import os
import textract
import csv
import re
from judges_data_get import update_judge_people_periods
from prosec_data_get import update_prosec_people_periods, prosec_multiline_name_catcher
from cleaning_tools import pre_clean, multiline_name_contractor

# TODO make it work from just memory so you don't have to unzip anything


def docs_to_csv(rootdir, outfile_name, split_mark, parquet=False):
    """
    Go through doc files, extract data and put it all into a csv file.
    :return: None
    """

    head = ["nume", "prenume", "instanță/parchet", "an", "lună"]
    with open(outfile_name, 'w') as outfile:
        writer = csv.writer(outfile, delimiter=',')
        writer.writerow(head)
        counter = 0
        for subdir, dirs, files in os.walk(rootdir):
            for file in files:
                counter += 1
                if counter < 10000:
                    filepath = subdir + os.sep + file
                    print(filepath)
                    if parquet:
                        year, month = filepath[28:32], filepath[33:35]
                    else:
                        year, month = filepath[23:27], filepath[28:30]
                    # extract text, capitalise, and pre-clean
                    text = pre_clean(textract.process(filepath).decode('utf-8').upper(), parquet)
                    # treat files of military units separately, have different structure
                    if get_military_data(text):  # handle military courts/parquets separately
                        continue
                    people_periods = get_people_periods(text, split_mark, year, month, parquet)
                    for pp in people_periods:
                        writer.writerow(pp)


def get_people_periods(text, split_mark, year, month, parquet):
    """return a tuple with unit name (viz. Court X), surname, and given names"""
    people_periods = []
    units = re.split(split_mark, text)
    for u in units:
        unit_lines = list(filter(None, u.splitlines()))
        if len(unit_lines) > 1:
            if parquet:
                update_prosec_people_periods(people_periods, unit_lines, split_mark, year, month)
            else:
                update_judge_people_periods(people_periods, unit_lines, text, year, month)
    people_periods = multiline_name_contractor(people_periods)
    if parquet:
        people_periods = prosec_multiline_name_catcher(people_periods)
    return people_periods


# TODO write this function, data from military employment rolls looks different
def get_military_data(text):
    # detect if it's data from the miliitary courts/parquets
    military = (re.search(r'PARCHETELOR MILITARE|PARCHETELE MILITARE|PARCHETUL MILITAR', text)
                is not None) or (re.search(r'CURTEA MILITAR|TRIBUNALUL MILITAR', text) is not None)
    return military
