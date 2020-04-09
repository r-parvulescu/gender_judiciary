"""
Functions for calculating the quantity of entries and exits.
"""

from operator import itemgetter
from itertools import groupby


def entries_per_year_per_level(person_year_table, start_year, end_year, year_sum=False):
    """counts the number of entries or exits per year"""
    year_level_counters = {year: {1: 0, 2: 0, 3: 0, 4: 0} for year in range(start_year, end_year)}
    person_year_table.sort(key=itemgetter(0, 6))
    person_sequences = [g for k, [*g] in groupby(person_year_table, key=itemgetter(0))]
    for seq in person_sequences:
        if len(seq) > 1:  # ignore sequences one long, marking as entry or exit would double-count
            year_level_counters[int(seq[0][6])][int(seq[0][-1])] += 1  # first sequence element marks entry point
    if year_sum:  # get sum of mobility across levels
        year_level_counters = [(k, sum(v.values())) for k, v in year_level_counters.items()]
    else:
        year_level_counters = [(k, sorted(list(v.items()), key=itemgetter(1)))
                               for k, v in year_level_counters.items()]
    return sorted(list(year_level_counters))[1:-1]


def mobility_per_year_per_level(person_year_table, start_year, end_year, mobility_type, year_sum=False):
    """
    counts the number of retirements/exits per year, per level
    NB: recall hierarchical levels, 1 = judecătorie; 2 = tribunal; 3 = curte de apel; 4 = iccj
    NB: recall mobility types: 'up', 'across', 'down', 'out'
    """
    year_level_counters = {year: {1: 0, 2: 0, 3: 0, 4: 0} for year in range(start_year, end_year)}
    for py in person_year_table:
        if py[5] == mobility_type:
            year_level_counters[int(py[6])][int(py[-1])] += 1
    if year_sum:  # get sum of mobility across levels
        year_level_counters = [(k, sum(v.values())) for k, v in year_level_counters.items()]
    else:
        year_level_counters = [(k, sorted(list(v.items()), key=itemgetter(1)))
                               for k, v in year_level_counters.items()]
    return sorted(list(year_level_counters))[1:-1]
