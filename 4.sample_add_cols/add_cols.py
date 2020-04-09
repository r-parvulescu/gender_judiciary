"""
Functions for adding a column markaing whether there a person-year featured inter-unit occupational mobility.
"""

import csv
import operator
from itertools import groupby


def add_mobility_column(person_year_table):
    """
    ads a column indicating if the person-year (row) featured inter-unit occupational mobility
    NB: even though mobility is determined by comparing two years, by convention I attribute mobility to the former
        year
    """
    person_year_table.sort(key=operator.itemgetter(0, 5))
    person_bins = [g for k, [*g] in groupby(person_year_table, key=operator.itemgetter(0))]
    table_with_mobility = []
    for person in person_bins:
        for idx, year in enumerate(person):
            moved = 0
            if idx < len(person) - 1:
                if person[idx][4] != person[idx + 1][4]:
                    moved = 1
            table_with_mobility.append(person[idx][:5] + [moved] + person[idx][5:])
    return table_with_mobility


def add_level_column(person_year_table):
    """
    return a table with a column for court level: J = judecătorie (lowest level, one); TB = tribunal (second level);
     CA = curte de apel (third level); ICCJ = înalta curte de casaţie şi justiţie (High Court, highest level)
    """
    for idx, row in enumerate(person_year_table):
        if row[-1] != '-88':
            level = 'J'
        elif row[-2] != '-88':
            level = 'TB'
        elif row[-3] != '-88':
            level = 'CA'
        else:
            level = 'ICCJ'
        person_year_table[idx] = person_year_table[idx] + [level]
    return person_year_table
