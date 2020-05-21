"""
Takes employment records in different formats, converts them into a neat person-period (e.g. person-years)
table, and output this table as as csv.

NB: the base data files were EXTENSIVELY cleaned (by hand) to fix format, typo, etc. issues.
The functions in this module WILL NOT WORK with freshly scraped (dirty) output from scrape_csm_old.py, or from
the other data archives.
"""

import os
import csv
import numpy as np
import pandas as pd
import re
import textract
import camelot
from collector.converter import prosec_helpers
from collector.converter import judge_helpers
from collector.converter import cleaners


# TODO make it work from just memory so you don't have to unzip anything


def make_pp_table(profession):
    """
    Go through employment rolls, extract person-period data, put it into a table, and save as csv.
    :param profession: string, "judges", "prosecutors", "notaries" or "executori".
    :return None
    """
    # get the directories where the base data files live, and the root of the path where the out-csv will go
    directories, out_path = get_paths(profession)

    # initialise a dict of person-period tables, according to the time-grain of the table
    # (i.e. person-year vs person-month)
    ppts = {'year': ([], '_year.csv'), 'month': ([], '_month.csv')}
    counter = 0

    for d in directories:
        # if int(re.search(r'([1-2][0-9]{3})', d).group(1)) < 2005:  # to use only pre-2005 data
        for subdir, dirs, files in os.walk(d):
            for file in files:
                counter += 1
                if counter < 100000:
                    file_path = subdir + os.sep + file
                    print(file_path)
                    print(counter)
                    people_periods_dict = triage(file_path, profession)
                    [ppts[k][0].extend(v) for k, v in people_periods_dict.items() if v]

    # write to csv
    head = ["nume", "prenume", "instanță/parchet", "an", "lună"]
    for k, v in ppts.items():
        if v[0]:
            unique_row_table = cleaners.deduplicate_list_of_lists(v[0])
            with open(out_path + v[1], 'w') as outfile:
                writer = csv.writer(outfile, delimiter=',')
                writer.writerow(head)
                for row in unique_row_table:
                    writer.writerow(row)


def get_paths(profession):
    """
    Return paths for directories where the in-files live, and partial path where the out-file should go.
    :param profession: string, "judges", "prosecutors", "notaries" or "executori".
    :return: tuple, ([list of directories], partial path)
    """
    in_directories, outfile_path = [], ''
    if profession == 'judges':
        in_directories = ['collector/converter/input/judges_12.2005-04.2020',
                          'collector/converter/input/judges_1988-2005']
        outfile_path = 'collector/converter/output/judges/judges'
    if profession == 'prosecutors':
        in_directories = ['collector/converter/input/prosecutors_12.2005-12.2019',
                          'collector/converter/input/prosecutors_1988-2005']
        outfile_path = 'collector/converter/output/prosecutors/prosecutors'

    if in_directories and outfile_path:
        return in_directories, outfile_path
    else:
        print('NO INPUT PROVIDED')


def triage(in_file_path, profession):
    """
    Invoke text extraction and processing tools depending on file type.

    .xlsx files come from a research assistant who has hand-cleaned all data, typically from historical
    archives (e.g. pictures of employment rolls from the 1980's).
    NB: .xlsx files may refer to ANY profession, and may contain data at BOTH the year AND the month level

    .pdf files contain employment rolls of prosecutors from 2017 (inclusive) onward; found at csm1909.ro
    NB: .pdf files refer ONLY to prosecutors, and contain ONLY month-level data

    .doc files contain employment rolls for magistrates 2005-2019; data from scrape_csm_old.py and freedom of
    information requests
    NB: .doc files refer ONLY to prosecutors and magistrates, and contain ONLY month-level data

    :param in_file_path: string, path to the file holding employment information
    :param profession: string, "judges", "prosecutors", "notaries" or "executori".
    :return dict with key =  time-grains (i.e. year, month) and value = person-period table
    """
    pps = {'year': [], 'month': []}

    if in_file_path[-4:] == 'xlsx':
        people_periods_dict = get_xlsx_people_periods(in_file_path, profession)
        [pps[k].extend(v) for k, v in people_periods_dict.items() if v]

    if in_file_path[-3:] == 'pdf':
        year, month = get_year_month(in_file_path)
        if "PMCMA" not in in_file_path:  # military prosecutors, skip for now
            pps['month'].extend(get_pdf_people_periods(in_file_path, year, month))

    if in_file_path[-3:] == 'doc':
        year, month = get_year_month(in_file_path)
        doc_people_periods = get_doc_people_periods(in_file_path, year, month, profession)
        if doc_people_periods:
            pps['month'].extend(doc_people_periods)

    return pps


def get_year_month(filepath):
    """
    Get the year and month from the file path.
    :param filepath: string, path to the file
    :return tuple of (year, month)
    """
    year_month = re.search(r'/([0-9].+)/', filepath).group(1)
    year, month = year_month.split('/')[0], year_month.split('/')[1]
    return year, month


def get_xlsx_people_periods(in_file_path, profession):
    """
    Extract all people people-periods (e.g. person-month) from employment rolls in .xlsx format,
    dumps them in tables (as lists of lists), and puts the tables in a dict
    :param in_file_path: string, path to the file holding employment information
    :param profession: string, "judges", "prosecutors", "notaries" or "executori"
    :return dict with key =  time-grains (i.e. year, month) and value = person-period table
    """
    df = pd.read_excel(in_file_path)
    table = xlsx_df_cleaners(df).values.tolist()  # not all dfs have same shape, turn to list of lists

    person_years = []
    person_months = []
    for row in table:
        row = list(filter(None, row))
        # too much fidelity, even wrote in an unusual "former/other employee" value; just ignore these for now
        # TODO need to get back to this and figure out how to not throw out these data
        if 'ANGAJAŢI' not in row[2]:
            unit = None  # easy to trace problem

            if profession == 'judges':
                unit = judge_helpers.court_name_cleaner(row[2])
                surnames, given_names = judge_helpers.judge_name_clean(row[0], row[1])

            if profession == 'prosecutors':
                unit = prosec_helpers.parquet_name_cleaner(row[2])
                surnames, given_names = prosec_helpers.prosec_name_clean(row[0], row[1])

            # month data in the fifth column; if no month data, mark as missing
            if len(row) == 4:
                person_years.append([surnames, given_names, unit, str(row[3])])  # year = row[3]
            else:
                person_months.append([surnames, given_names, unit, str(row[3]), str(int(row[4]))])
        else:
            print(row)
    return {"year": person_years, "month": person_months}


def xlsx_df_cleaners(df):
    """
    Run a pandas df through a bunch of (mostly text) cleaners.
    :return a pandas df
    """
    df = df.drop(df.columns[0], axis=1)  # drop ID column
    df = df.applymap(lambda s: s.upper() if type(s) == str else s)  # everything uppercase
    df = df.applymap(lambda s: s.replace('Ț', 'Ţ') if type(s) == str else s)  # deal with non-standard
    df = df.applymap(lambda s: s.replace('Ș', 'Ş') if type(s) == str else s)  # diacritics
    df = df.applymap(lambda s: s.replace('-', ' ') if type(s) == str else s)  # remove hyphens
    df = df.replace(np.nan, '', regex=True)  # swap nan's for empty string
    return df


def get_pdf_people_periods(in_file_path, year, month):
    # TODO 'post rezervat' (snuck in there, find it)
    """
    Extract all people people-periods (e.g. person-month) from employment rolls in .pdf format,
    dumps them in tables (as lists of lists)
    NB: this function ignores the internal hierarchy and/or territorial division of PICCJ, DIICOT and DNA
    :param in_file_path: string, path to the file holding employment information
    :param year: string of year, e.g. "1990"
    :param month: string of two-digit month, e.g. "04", or "12"
    :return person-period table, as list of lists
    """
    person_periods = []
    tables = camelot.read_pdf(in_file_path, pages='1-end')
    tables = camelot_parser(in_file_path, tables)

    special_parquet = prosec_helpers.pdf_get_special_parquets(in_file_path)
    if tables:
        for t in tables:
            table_as_list = t.df.values.tolist()

            # sometimes the first row is the header
            if table_as_list[0][0].strip() == 'NUME PERSONAL PARCHETE' or table_as_list[0][-1] == 'P.J.':
                table_as_list = table_as_list[1:]

            for row in table_as_list:
                parquet = special_parquet if special_parquet else prosec_helpers.pdf_get_parquet(row)
                parquet = cleaners.space_name_replacer(parquet, cleaners.parquet_sectors_buc)
                parquet = cleaners.space_name_replacer(parquet, cleaners.parquet_names)

                # for now, avoid military parquets
                if parquet != 'SPM':

                    # avoid junk input, e.g. fullname = "A1" in 2017-09-PCA_Timisoara.pdf
                    # also "Post rezervat" in 2018-02-PCA_Cluj.pdf
                    if len(row[0]) > 3 or " rezervat" in row[0]:  # row[0] = fullname
                        surnames, given_names = prosec_helpers.get_prosecutor_names(row[0])
                        # words that sneak in due to improper formatting
                        given_names = given_names.replace("execuţie", '').replace('conducere', '')
                        # some double maiden names are separated by a comma
                        surnames = surnames.replace(',', ' ')
                        surnames, given_names = prosec_helpers.problem_name_handler(surnames, given_names)
                        person_periods.append([surnames, given_names, parquet, year, month])
                    else:
                        print(row[0])
    else:
        return
    return person_periods


def camelot_parser(in_file_path, tables):
    """
    Try and get the most accurately parsed pdf table from camelot; if accuracy is problematic, skip and let us know.

    if lattice parsing accuracy < 90% try stream parsing
        if stream parsing accuracy > 90%, return stream-parsed tables
        else print file_path (to inspect that pdf) and return None (skip the inaccurate file)

    :param in_file_path: string, path to the file holding employment information
    :param tables: iterable of camelot tables
    :return tables if accuracy is acceptable, None otherwise
    """
    accuracies = [t.parsing_report['accuracy'] for t in tables]
    if min(accuracies) < 90:
        print("------------------------ USED STREAM ------------------------")
        tables = camelot.read_pdf(in_file_path, pages='1-end', flavor='stream')
        # if accuracy still low, print filepath so I can inspect the pdf
        if min([t.parsing_report['accuracy'] for t in tables]) < 90:
            print(in_file_path)
            return None
        return tables
    else:
        return tables


def get_doc_people_periods(in_file_path, year, month, profession):
    """
    Extract all people people-periods (e.g. person-month) from employment rolls in .doc format,
    dumps them in tables (as lists of lists)
    :param in_file_path: string, path to the file holding employment information
    :param year: string of year, e.g. "1990"
    :param month: string of two-digit month, e.g. "04", or "12"
    :param profession: string, "judges", "prosecutors", "notaries" or "executori"
    :return person-period table, as list of lists
    """
    prosecs = True if profession == 'prosecutors' else False
    # extract text, capitalise, and pre-clean
    text = cleaners.pre_clean(textract.process(in_file_path).decode('utf-8').upper(), prosecs)
    if get_doc_military_data(text):
        return
    people_periods = []
    split_mark = 'PARCHETUL ' if prosecs else 'JUDECĂTORIA |JUDECATORIA |TRIBUNALUL |CURTEA DE APEL'
    # splits the text into chunks, each chunk is the employment roll for one unit, e.g. a court of parquet
    units = re.split(split_mark, text)
    for u in units:
        # turns the text lines (usually each line is an employee) into a list, basically a list of employees
        unit_lines = list(filter(None, u.splitlines()))
        if len(unit_lines) > 1:
            if prosecs:
                prosec_helpers.update_prosec_people_periods(people_periods, unit_lines, split_mark, year, month)
            else:
                judge_helpers.update_judge_people_periods(people_periods, unit_lines, text, year, month)
    people_periods = cleaners.multiline_name_contractor(people_periods)
    if prosecs:
        people_periods = prosec_helpers.prosec_multiline_name_catcher(people_periods)
    return people_periods


def get_doc_military_data(text):
    """
    As it stands, lets us know whether the file refers to military courts or parquets,
    :param text: text (parsed by textract) of the whole .doc file
    :return: bool, True if the file refers to military courts or parquets, False otherwise
    """
    # TODO write this function to actually get person-periods from military court/parquet employment rolls
    #  the military courts/parquets have their own, separate territorial structure, which takes work to untangle
    # detect if it's data from the miliitary courts/parquets
    military = (re.search(r'PARCHETELOR MILITARE|PARCHETELE MILITARE|PARCHETUL MILITAR', text)
                is not None) or (re.search(r'CURTEA MILITAR|TRIBUNALUL MILITAR', text) is not None)
    return military
