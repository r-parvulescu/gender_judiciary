"""
Handy helpers.
"""

import csv
import PyICU
import Levenshtein


def deduplicate_list_of_lists(list_of_lists):
    """
    Remove duplicate rows from table as list of lists quicker than list comparison: turn all rows to strings,
    put them in a set, them turn set elements to list and add them all to another list.
    NB: copy-pasted from collector.converter.cleaners, because ain't nobody got time for relative import errors


    :param list_of_lists: what it sounds list
    :return list of lists without duplicate rows (i.e. inner lists)
    """
    uniques = {'|'.join(row[:3] + [str(row[3])]) for row in list_of_lists}
    return [row.split('|') for row in uniques]


def pairwise_ldist(strings_iter, lev_dist):
    """
    :param strings_iter: iterable (e.g. set, list) of strings
    :param lev_dist: int indicating the desired Levenshtein distance
    :return list of 2-tuples of full names lev_dist apart, alphabetically sorted by first name in tuple
    NB: pairwise comparison is lower triangular, no diagonals
     """
    return sorted(list(filter(None, [(x, y) if 0 < Levenshtein.distance(x, y) <= lev_dist else ()
                                     for i, x in enumerate(strings_iter)
                                     for j, y in enumerate(strings_iter) if i > j])))


def print_uniques(csv_file, col_idx):
    """print all unique column entries, helps weed out typos, misspellings, etc. in names"""
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip head
        uniques = set()
        for row in reader:
            uniques.add(row[col_idx])

    # sort taking into account Romanian diacritics
    collator = PyICU.Collator.createInstance(PyICU.Locale('ro_RO.UTF-8'))
    uniques = [i for i in sorted(list(uniques), key=collator.getSortKey)]
    for u in sorted(list(uniques)):
        print(u)
