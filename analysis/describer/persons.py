"""
Functions for getting sums (total counts) per unit and mobility type.
"""

from operator import itemgetter
import pandas as pd


def people_per_year(person_year_table, start_year, end_year):
    """returns a list of (year, count of unique people) tuples"""
    ids_per_year = {year: set() for year in range(start_year, end_year + 1)}
    [ids_per_year[int(py[6])].add(py[0]) for py in person_year_table]
    return sorted(list({k: len(val) for k, val in ids_per_year.items()}.items()))


def people_per_level_per_year(person_year_table, start_year, end_year, ratios=False):
    """
    returns a list of (year : (count J, count TB, count CA, count ICCJ)) tuples
    or if ratios=False of yearly ratios between the sizes of adjacent levels"""
    ids_per_year_per_level = {year: {1: 0, 2: 0, 3: 0, 4: 0} for year in range(start_year, end_year)}
    for py in person_year_table:
        ids_per_year_per_level[int(py[6])][int(py[-1])] += 1
    if ratios:  # get ratio of totals between level X and the level immediately below it
        ratios_per_year = {}
        for k, v in ids_per_year_per_level.items():
            cnts = sorted(list(v.items()), key=itemgetter(1))
            sorted_ratios = (round(cnts[0][1] / cnts[1][1], 2), round(cnts[1][1] / cnts[2][1], 2),
                             round(cnts[2][1] / cnts[3][1], 2))
            ratios_per_year[k] = sorted_ratios
        return sorted(list(ratios_per_year.items()))
    else:
        ids_per_year_per_level = [(k, sorted(list(v.items()), key=itemgetter(1)))
                                  for k, v in ids_per_year_per_level.items()]
        return sorted(list(ids_per_year_per_level))


def percent_female(person_year_table, levels=True):
    """returns a list of (year, percent female) tuples; if levels=True, percent per year, per level"""
    groups = ['an', 'nivel'] if levels else ['an']
    columns = ["cnp", "nume", "prenume", "sex", "instanță/parchet", "mişcat", "an", "lună",
               "ca cod", "trib cod", "jud cod", 'nivel']
    df = pd.DataFrame(person_year_table, columns=columns)
    df = pd.get_dummies(df, columns=['sex'])
    probs = df.groupby(groups)['sex_f'].mean().to_dict()
    if len(groups) < 2:  # sorted by year
        return sorted(list(probs.items()))
    else:  # sorted by level, by year
        return sorted(list(probs.items()), key=lambda x: (x[0][1], x[0][0]))
