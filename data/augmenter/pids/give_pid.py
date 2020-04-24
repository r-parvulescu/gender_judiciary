"""
Functions for assigning unique IDs to each person.
"""

import csv
from augmenter.pids import row_helpers
from augmenter.pids import iter_helpers
from augmenter.pids import deduplicators


def set_unique_pid(table):
    """
    associate each person-month with a person-level unique ID
    """
    # set initial person-IDs
    table = set_person_id(table)
    # clean IDs with regard to name order in long names
    table = deduplicators.merge_id_over_name_order(table)
    # deal with IDs that count people in two places at the same time
    table = deduplicators.remove_double_count_tenures(table)
    table = deduplicators.split_coinciding_sequences(table)
    return table


def set_person_id(table):
    """for each unique fullname add an ID"""
    unique_fullnames = iter_helpers.collect_of_row_results(table, "set", row_helpers.make_fullname)
    name_ids = {ufn: idx for idx, ufn in enumerate(unique_fullnames)}
    return [[name_ids[row_helpers.make_fullname(row)]] + row for row in table]

# TODO deal with known maiden names, i.e. those surnames in brackets

# TODO deal with unique names that occur at the same place, at the same time
# down to five of these IDs, still a bit of work to check things are behaving properly

# TODO not sure the deduplicators and ID mergers are updating the table properly, need to check more

# TODO update to use operator.itemgetter instead of lambda where possible, and use list.sort instead of
# sorted so there's less remaking things to put in memory

# TODO use literal constructors (e.g. on sets) wherever possible
