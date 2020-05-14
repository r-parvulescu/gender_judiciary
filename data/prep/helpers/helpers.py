"""
Handy helpers.
"""

import pandas as pd
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


def pairwise_ldist(strings_iter, lev_dist, sort_key=None):
    """
    :param strings_iter: iterable (e.g. set, list) of strings
    :param lev_dist: int indicating the desired Levenshtein distance
    :param sort_key: the key for sorting the list of tuples; if None, sorts by first tuple entry
    :return list of 2-tuples of full names lev_dist apart, alphabetically sorted by first name in tuple
    NB: pairwise comparison is lower triangular, no diagonals
     """

    list_of_tuples_ldist_apart = list(filter(None, [(x, y) if 0 < Levenshtein.distance(x, y) <= lev_dist else ()
                                                    for i, x in enumerate(strings_iter)
                                                    for j, y in enumerate(strings_iter) if i > j]))

    if sort_key is None:
        return sorted(list_of_tuples_ldist_apart)
    else:
        return sorted(list_of_tuples_ldist_apart, key=sort_key)


def print_full_names_ldist_apart(csv_file_path, l_dist):
    """
    Prints out a sorted column of all full names that are ldist or more apart in terms of Levenshtein distance.
    This helps weed out typos by hand that are too subtle to leave to automated functions.
    :param csv_file_path: string, file path to a csv file
    :param l_dist: int, maximum Levenshtein/edit distance between two full names that you want to compare
    :return: None
    """
    df = pd.read_csv(csv_file_path)
    table = df.values.tolist()
    unique_full_names = {row[1] + ' | ' + row[2] for row in table}  # row[1] = surnames, row[2] = given names

    full_name_ldist = pairwise_ldist(unique_full_names, l_dist)
    [print(full_name_pair) for full_name_pair in full_name_ldist]
