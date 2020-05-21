"""
Functions for augmenting  person-period table with extra columns.
infile headers: nume, prenume, instanță/parchet, an, lună
"""

import os
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
    combined table, assign every person-year a row ID gender, institution profile, and unique (row) ID, and finally
     assign each row a person-level unique ID. Write the combined, cleaned, and augmented person-year table to disk.

    :param profession: string, "judges", "prosecutors", "notaries" or "executori".
    :return: None
    """

    ppts = {'year': [[], '_year.csv'], 'month': [[], '_month.csv']}
    infile_directory = 'collector/converter/output/' + profession

    # load csv's into tables, per time granularity
    for subdir, dirs, files in os.walk(infile_directory):
        for f in files:
            file_path = subdir + os.sep + f
            period = 'month' if 'month' in file_path else 'year'
            table_as_list = pd.read_csv(file_path).values.tolist()
            ppts[period][0] = table_as_list

    # initialise the dictionary in which we keep track of changes
    change_dict = {'overview': []}

    # sample one month from the person-month data to get year-level data,
    # then combine the sample with the original year data
    # NB: the sampler drops the month column -- this is necessary for row deduplication to work properly
    sm = sample.get_sampling_month(profession)
    year_sampled_from_months = sample.person_years(ppts['month'][0], sm, change_dict)
    ppts['year'][0].extend(year_sampled_from_months)

    # run name standardiser on the combined table
    year_range, year = 30, True
    ppts['year'][0] = standardise.clean(ppts['year'][0], change_dict, year_range, year, profession)
    standardise.make_log_file(change_dict, profession)

    # add gender and unit info
    ppts['year'][0] = add_rowid_gender_workplace(ppts['year'][0], profession)

    # remove overlaps (i.e. when two people are in the same place at once), interpolate years (when they're missing
    # for spurious reasons) and add unique IDs
    ppts['year'][0] = pids.pids(ppts['year'][0], profession)

    # return the preprocessed table
    return ppts['year'][0]


def add_rowid_gender_workplace(person_period_table, profession):
    """
    Add columns for row ID, gender and workplace profile to the person-period table.
    :param person_period_table: a person-period table, as a list of lists
    :param profession: string, "judges", "prosecutors", "notaries" or "executori".
    :return: a person-period table (as list of lists) with new columns
    """

    # load dictionaries
    workplace_dict = units.get_unit_codes(profession)
    gender_dict = gender.get_gender_dict()

    # add columns for person gender and unit profile
    with_new_cols = []
    for idx, row in enumerate(person_period_table):
        workplace_profile = units.set_unitcode_level(row[2], workplace_dict)  # unit name = row[2]
        gend = gender.get_gender(row[1], row, gender_dict)
        new_row = [idx] + row[:2] + [gend] + row[2:] + workplace_profile
        with_new_cols.append(new_row)
    return with_new_cols
