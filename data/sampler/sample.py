"""
Functions for sampling from a person-month table to generate a person-year table.
"""

import csv
import operator
import itertools


def sample_data(quarter, to_csv, prosecs=False):
    """sample the existing data table"""
    in_path = 'augmenter/prosecutors_ids.csv' if prosecs else 'augmenter/judges_ids.csv'
    sampled_data = person_year_sampler(in_path, quarter)
    with_mobility = set_interyear_mobility(sampled_data)
    if to_csv:
        outfile = 'sampler/prosecutors_personyears.csv' if prosecs else 'sampler/judges_personyears.csv'
        with open(outfile, 'w') as out_file:
            writer = csv.writer(out_file)
            new_headers = ["cnp", "nume", "prenume", "sex", "instanță/parchet", "mişcat", "an", "lună",
                           "ca cod", "trib cod", "jud cod", 'nivel']
            writer.writerow(new_headers)
            for row in with_mobility:
                writer.writerow(row)
    return with_mobility


def person_year_sampler(person_month_inpath, quarter):
    """
    sample the specified quarter and return the person-year table;
    if that quarter is unavailable, skips that person-year
    NB: "quarter" is int: 1,2,3,4
    """
    # sample by quarter
    quarter_months = {1: {'01', '02', '03'}, 2: {'04', '05', '06'}, 3: {'07', '08', '09'}, 4: {'10', '11', '12'}}
    person_quarter_table = person_quarter_sampler(person_month_inpath)
    # sort table by ID and year and bin person-quarters into years
    person_quarter_table.sort(key=operator.itemgetter(0, 5))
    quarter_by_year = [g for k, [*g] in itertools.groupby(person_quarter_table, key=operator.itemgetter(0, 5))]
    person_years = []
    for person_quarters in quarter_by_year:
        for person_month in person_quarters:
            if person_month[6] in quarter_months[quarter]:
                person_years.append(person_month)
    return person_years


def person_quarter_sampler(person_month_inpath):
    """
    sample first available month each quarter: this ensures that a one-month blip doesn't mess up the sample;
    assumes we need a full quarter absence before saying that someone wasn't there
    """
    with open(person_month_inpath, 'r') as pmi:
        reader = csv.reader(pmi)
        person_month_table = list(reader)
    quarters = [{'01', '02', '03'}, {'04', '05', '06'}, {'07', '08', '09'}, {'10', '11', '12'}]
    # sort table by unique id, year, and month, then bin person-months into quarters
    person_month_table.sort(key=operator.itemgetter(0, 5, 6))
    person_months_by_quarters = [bin_person_months_into_quarters(person_month_table, qrtr) for qrtr in quarters]
    # sample the first available person-month in the quarter (assuming the person-quarter exists)
    person_quarters = []
    for quarter_group in person_months_by_quarters:
        for id_year_quarter_group in quarter_group:
            person_quarters.append(id_year_quarter_group[0])
    return person_quarters


def bin_person_months_into_quarters(person_month_table, quarter):
    """bin person-months in quarters"""
    return list(filter(None, [[row for row in g if row[6] in quarter]
                              for k, [*g] in itertools.groupby(person_month_table,
                                                               key=operator.itemgetter(0, 5))]))


def set_interyear_mobility(person_year_table):
    """
    ads a column indicating if the person-year (row) featured inter-unit occupational mobility
    NB: even though mobility is determined by comparing two years, by convention I attribute mobility to the former
        year
    """
    person_year_table.sort(key=operator.itemgetter(0, 5))
    person_bins = [g for k, [*g] in itertools.groupby(person_year_table, key=operator.itemgetter(0))]
    table_with_mobility = []
    for person in person_bins:
        if len(person) == 1:  # only one year per person, can't determine mobility
            table_with_mobility.append(person[0][:5] + ['NA'] + person[0][5:])
            continue
        for idx, year in enumerate(person):
            if idx < len(person) - 1:
                if person[idx][4] != person[idx + 1][4]:  # if tomorrow's unit is different from today
                    if person[idx][-1] < person[idx + 1][-1]:  # if tomorrow's unit level is higher
                        moved = 'up'
                    elif person[idx][-1] == person[idx + 1][-1]:  # if tomorrow's unit level is the same
                        moved = 'across'
                    else:  # if tomorrow's unit level is lower
                        moved = 'down'
                else:  # if tomorrow's unit is the same as today
                    moved = '0'
            else:  # end of person sequence, i.e. retirement
                moved = "out"
            table_with_mobility.append(person[idx][:5] + [moved] + person[idx][5:])
    return table_with_mobility
