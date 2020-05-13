"""
Functions for augmenting  person-period table with extra columns.
infile headers: nume, prenume, instanță/parchet, an, lună
"""

import os
import csv
import pandas as pd
from prep.standardise import standardise
from prep.sample import sample
from prep.units import units
from prep.gender import gender
from prep.pids import pids


def preprocess(profession):
    """
    Standardise data from person-period tables at different levels of time granularity (year and month levels),
    sample person-months to get person-years, combine this sample with the original year-level data, clean the
    combined table, assign every person-year a gender, institution profile, and unique (row) ID, and finally assign
    each row a person-level unique ID. Then write the combined, cleaned, and augmented person-year table to a csv.

    :param profession: string, "judges", "prosecutors", "notaries" or "executori".
    :return: None
    """
    '''
    ppts = {'year': [[], '_year.csv'], 'month': [[], '_month.csv']}
    infile_directory = 'collector/converter/output/' + profession
    outfile_directory = 'prep/standardise/' + profession

    # load csv's into tables, per time granularity
    for subdir, dirs, files in os.walk(infile_directory):
        for f in files:
            file_path = subdir + os.sep + f
            period = 'month' if 'month' in file_path else 'year'
            table_as_list = pd.read_csv(file_path).values.tolist()
            ppts[period][0] = table_as_list

    # sample one month from the person-month data to get year-level data,
    # then combine the sample with the original year data
    # NB: the sampler drops the month column -- this is necessary for row deduplication to work properly
    sm = sample.get_sampling_month(profession)
    year_sampled_from_months = sample.person_years(ppts['month'][0], sm)
    ppts['year'][0].extend(year_sampled_from_months)

    # run name standardiser on the combined table
    change_dict = {}
    year_range, year = 30, True
    ppts['year'][0] = standardise.clean(ppts['year'][0], change_dict, year_range, year)
    standardise.make_log_file(change_dict, outfile_directory + '/change_log.csv')

    # add gender and unit info
    ppts['year'][0] = add_gender_inst_profile(ppts['year'][0], profession)

    # name standardisation takes 5-15 mins, best write standardised table to disk ASAP in case something breaks after
    outfile = outfile_directory + '/' + profession + '_preprocessed.csv'
    with open(outfile, 'w') as out_file:
        writer = csv.writer(out_file)
        new_headers = ["cr", "nume", "prenume", "sex", "instituţie", "an", "ca cod", "trib cod", "jud cod", "nivel"]
        writer.writerow(new_headers)
        row_count = 0
        for row in ppts['year'][0]:
            row_count += 1
            writer.writerow([row_count] + row)
    '''

    # run dedupe to get person ids; the dedupe package only takes csv's
    pids.cluster(profession)


def add_gender_inst_profile(person_period_table, profession):
    """
    Add columns for gender and unit profile to the person-period table.
    :param person_period_table: a person-period table, as a list of lists
    :param profession: string, "judges", "prosecutors", "notaries" or "executori".
    :return: a person-period table (as list of lists) with new columns
    """

    # load dictionaries
    inst_prof_dict = units.get_unit_codes(profession)
    gender_dict = gender.get_gender_dict()

    # add columns for person gender and unit profile
    with_new_cols = []
    for row in person_period_table:
        inst_prof = units.set_unitcode_level(row[2], inst_prof_dict)  # unit name = row[2]
        gend = gender.get_gender(row[1], row, gender_dict)
        new_row = row[:2] + [gend] + row[2:] + inst_prof
        with_new_cols.append(new_row)
    return with_new_cols
