"""
Functions for sampling from a person-month table to generate a person-year table.
"""

import operator
from itertools import groupby


def person_year_sampler(person_quarter_table, quarter):
    """
    sample the specified quarter and return the person-year table;
    if that quarter is unavailable, skips that person-year
    NB: "quarter" is int: 1,2,3,4
    """
    quarter_months = {1: {'01', '02', '03'}, 2: {'04', '05', '06'}, 3: {'07', '08', '09'}, 4: {'10', '11', '12'}}
    # sort table by ID and year and bin person-quarters into years
    person_quarter_table.sort(key=operator.itemgetter(0, 5))
    quarter_by_year = [g for k, [*g] in groupby(person_quarter_table, key=operator.itemgetter(0, 5))]
    person_years = []
    for person_quarters in quarter_by_year:
        for person_month in person_quarters:
            if person_month[6] in quarter_months[quarter]:
                person_years.append(person_month)
    return person_years


def person_quarter_sampler(person_month_table):
    """
    sample first available month each quarter: this ensures that a one-month blip doesn't mess up the sample;
    assumes we need a full quarter absence before saying that someone wasn't there
    """
    quarters = [{'01', '02', '03'}, {'04', '05', '06'}, {'07', '08', '09'}, {'10', '11', '12'}]
    # sort table by unique id, year, and month, then bin person-months into quarters
    person_month_table.sort(key=operator.itemgetter(0, 5, 6))
    person_months_by_quarters = [bin_person_months_into_quarters(person_month_table, qrtr) for qrtr in quarters]
    # sample the first available person-month in the quarter (assuming the person-quarter exists)
    person_quarters = []
    id_set = set()
    for quarter_group in person_months_by_quarters:
        for id_year_quarter_group in quarter_group:
            person_quarters.append(id_year_quarter_group[0])
            # if id_year_quarter_group[0][6] == '04' or id_year_quarter_group[0][6] == '05':
            #    #print(id_year_quarter_group[0])
            #    id_set.add(id_year_quarter_group[0][0])
    print(len(id_set))
    return person_quarters


def bin_person_months_into_quarters(person_month_table, quarter):
    """bin person-months in quarters"""
    return list(filter(None, [[row for row in g if row[6] in quarter]
                              for k, [*g] in groupby(person_month_table, key=operator.itemgetter(0, 5))]))
