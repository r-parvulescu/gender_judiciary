"""
Helper functions for handling iterators like sets, lists, and dicts.
"""

import csv
from itertools import groupby
from Levenshtein import distance
import row_helpers


def name_by_othername_count(data_source, freq, name_type):
    """
    return a dict of "one name: count of associated other names", up to a frequency limit
    NB: "name_type" must be "surnames" or "given_names"
    """

    idx = 0 if name_type == "surnames" else 1
    names = sorted(collect_of_row_results(data_source, "set", row_helpers.surname_given_name))
    return histogram_dict(names, idx, freq)


def name_by_row_count(table, name_type):
    """return a dict of names by the number of associated rows;
    NB: name_type must be "fullnames", "surnames", or "given_names" """
    if name_type == "fullnames":
        table = collect_of_row_results(table, "list", row_helpers.row_with_fullname)
    idx = 1 if name_type == "given_names" else 0
    return histogram_dict(sorted(table, key=lambda x: x[idx]), idx)


def histogram_dict(iterable, idx, freq=bool):
    """
    given an iterable of lists, group the rows by some list entry and take the frequency of those entries
    i.e. return a histogram dict, -- "row list entry": frequency; e.g. hist of first entry of rows
    NB: groupby needs a sorted iterable; this function expects pre-sorted iterable
    """
    if isinstance(freq, int):
        return {k: len(g) for k, [*g] in groupby(iterable, lambda x: x[idx]) if len(g) <= freq}
    else:
        return {k: len(g) for k, [*g] in groupby(iterable, lambda x: x[idx])}


def collect_of_row_results(data_source, collect, row_func):
    """
    given a csv, a function on rows, and an iterable collection, returns the iterable
    with row function evaluated on each row
    """
    collects = {"set": set(), "dictionary": {}, "list": []}
    iterable = collects[collect]
    if not isinstance(data_source, list):  # if it's not a list, it's a csv file
        with open(data_source) as f:
            data_source = csv.reader(f)
            next(data_source, None)
            for row in data_source:
                iterable.append(row_func(row)) if collect == "list" else iterable.add(row_func(row))
    else:
        for row in data_source:
            iterable.append(row_func(row)) if collect == "list" else iterable.add(row_func(row))
    return iterable


def string_tuple_by_ldist(strings, l_dist):
    """
    Given an iterable of strings, does pairwise Levenshtein distance between strings (lower triangular, no diagonals),
    and returns a list of pairs of strings ldist apart.
     """
    return sorted(list(filter(None, [(x, y) if distance(x, y) == l_dist else ()
                                     for i, x in enumerate(strings)
                                     for j, y in enumerate(strings) if i > j])))


def make_ym_unit_dict(table):
    """for each ID make a dict of years-months : units"""
    ids_time_units = {}
    for row in table:
        id_num = row[0]
        year_month = row[5] + '-' + row[6]
        court_code = '.'.join(row[-3:])
        if id_num not in ids_time_units:
            ids_time_units[id_num] = {}
        if year_month not in ids_time_units[id_num]:
            ids_time_units[id_num][year_month] = []
        ids_time_units[id_num][year_month].append(court_code)
    return ids_time_units
