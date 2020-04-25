"""
Functions for calculating counts of different mobility events, across different units.
"""

from operator import itemgetter
import itertools
import pandas as pd


def total_mobility(person_year_table, start_year, end_year):
    """return a dict of year : total mobility"""
    mobility_per_year = {year: 0 for year in range(start_year, end_year + 1)}
    for py in person_year_table:
        if py[5] != '0':
            mobility_per_year[int(py[6])] += 1
    return sorted(list(mobility_per_year.items()))[1:-1]


def entries(person_year_table, start_year, end_year, year_sum=False):
    """count the number of entries or exits per year (and if year_sum=False, per level)"""
    year_level_counters = year_level_dict(start_year, end_year)
    person_year_table.sort(key=itemgetter(0, 6))
    person_sequences = [g for k, [*g] in itertools.groupby(person_year_table, key=itemgetter(0))]
    for seq in person_sequences:
        if len(seq) > 1:  # ignore sequences one long, marking as entry or exit would double-count
            year_level_counters[int(seq[0][6])][int(seq[0][-1])] += 1  # first sequence element marks entry point
    return sorted_output(year_level_counters, 1, year_sum)[1:]  # first observation wrong due to censoring


def mob_counts(person_year_table, start_year, end_year, mobility_type, year_sum=False):
    """
    counts the number of mobility events per year (and if year_sum=False, per level)
    NB: recall hierarchical levels, 1 = judecătorie; 2 = tribunal; 3 = curte de apel; 4 = iccj
    NB: recall mobility types: 'up', 'across', 'down', 'out'
    """
    year_level_counters = year_level_dict(start_year, end_year + 1)
    for py in person_year_table:
        if py[5] == mobility_type:
            year_level_counters[int(py[6])][int(py[-1])] += 1
    return sorted_output(year_level_counters, 1, year_sum)


def mob_percent(person_year_table, mobility_type, per_unit):
    """
    percent of person_years that are of mobility type per unit (e.g. per year, per level)
    :param person_year_table: person-year table as list of lists
    :param mobility_type: str:  'up', 'out', 'across', 'down', or 'NA'
    :param per_unit: list of units as strings, e.g. ['year', 'level']
    """
    columns = ["cnp", "nume", "prenume", "sex", "instanță/parchet", "mişcat", "an", "lună",
               "ca cod", "trib cod", "jud cod", 'nivel']
    df = pd.DataFrame(person_year_table, columns=columns)
    df = pd.get_dummies(df, columns=['mişcat'])
    probs = df.groupby(per_unit)[mobility_type].mean().to_dict()
    if len(per_unit) < 2:  # sorted by year
        return sorted(list(probs.items()))
    else:  # sorted by level, by year
        return sorted(list(probs.items()), key=lambda x: (x[0][1], x[0][0]))


def mobility_per_year_per_unit(person_year_table, unit_list, start_year, end_year,
                               unit_type, mobility_type, year_sum=False):
    """
    counts the number of mobility events per year, per unit
    NB: units are either courts of appeals, tribunals, judecătorii.
    NB: mobility types: 'up', 'across', 'down', 'out'
    """

    unit_types_idx = {'1': -2, '2': -3, '3': -4}
    year_unit_counters = year_unit_dict(start_year, end_year + 1, unit_list)
    for py in person_year_table:
        if py[5] == mobility_type:
            idx = unit_types_idx[unit_type]
            if py[-1] == unit_type:
                year_unit_counters[int(py[6])][py[idx]] += 1
    return sorted_output(year_unit_counters, 1, year_sum)


def mob_cohorts(person_year_table, years_after, start_year, end_year, percent=False):
    """
    counts of mobility events per cohort, up to X years after they enter
    if percent=True return percent of cohort person-years accounted for by each mobility type
    """
    cohort_dict = {str(year): {'up': 0, 'down': 0, 'across': 0, 'out': 0, 'NA': 0, '0': 0}
                   for year in range(start_year, end_year + 1)}
    # groupby person  ID
    person_year_table.sort(key=itemgetter(0, 6))
    person_sequences = [g for k, [*g] in itertools.groupby(person_year_table, key=itemgetter(0))]
    for seq in person_sequences:
        entry_year = seq[0][6]
        yr_range = min(len(seq), years_after)
        for yr in range(yr_range):
            cohort_dict[entry_year][seq[yr][5]] += 1
    if percent:
        for cohort, mob in cohort_dict.items():
            sum_mob = sum(mob.values())
            percent_mob = {k: round(weird_division(v, sum_mob), 3) for k, v in mob.items()}
            cohort_dict[cohort] = percent_mob
    return sorted_output(cohort_dict, 0, year_sum=False)[:-years_after + 1]


def sorted_output(year_dict, sort_key, year_sum, ):
    """returns year_dict as sorted list, by year by categories, or by year summed across categories"""
    if year_sum:  # get sum of mobility across levels
        year_dict = [(k, sum(v.values())) for k, v in year_dict.items()]
    else:
        year_dict = [(k, sorted(list(v.items()), key=itemgetter(sort_key)))
                     for k, v in year_dict.items()]
    return sorted(list(year_dict))


def year_level_dict(l_yr, u_yr):
    """return a dict of dicts, of years holding levels, from lower year to upper year"""
    return {year: {1: 0, 2: 0, 3: 0, 4: 0} for year in range(l_yr, u_yr)}


def year_unit_dict(l_yr, u_yr, unit_list):
    """return a dict of dicts, of years holding units (e.g. courts of appeals), from lower year to upper year"""
    return {year: {unit: 0 for unit in unit_list} for year in range(l_yr, u_yr)}


def weird_division(n, d):
    # from https://stackoverflow.com/a/27317595/12973664
    return n / d if d else 0
