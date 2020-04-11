"""
Functions for assigning unique IDs to each person.
"""

import csv
import operator
import row_helpers
import iter_helpers
import transdict_tools
import deduplicators


def assign_unique_person_id(csv_infile, csv_outfile):
    """
    associate each person-month with a person-level unique ID
    """
    table = iter_helpers.collect_of_row_results(csv_infile, "list", lambda x: x)
    # update names with transdicts, use existing transdicts (don't make new ones)
    table = transdict_tools.multi_transdict_table_updater(table, make_td=False)
    # set initial person-IDs
    table = set_person_id(table)
    # clean IDs with regard to name order in long names
    table = merge_id_over_name_order(table)
    # deal with IDs that count people in two places at the same time
    table = deduplicators.remove_double_count_tenures(table)
    table = deduplicators.split_coinciding_sequences(table)

    # write table with person IDs to csv
    with open(csv_outfile, 'w') as f:
        writer = csv.writer(f)
        header = ["id", "nume", "prenume", "sex", "instanță/parchet", "an", "lună",
                  "CA cod", "trib cod", "jud cod"]
        writer.writerow(header)
        for row in table:
            writer.writerow(row)


def set_person_id(table):
    """for each unique fullname add an ID"""
    unique_fullnames = iter_helpers.collect_of_row_results(table, "set", row_helpers.make_fullname)
    name_ids = {ufn: idx for idx, ufn in enumerate(unique_fullnames)}
    return [[name_ids[row_helpers.make_fullname(row)]] + row for row in table]


def merge_id_over_name_order(data_source):
    """ignores name order within given and surnames, associating IDs with names"""
    table = iter_helpers.collect_of_row_results(data_source, "list", lambda x: x)
    all_ids_names = set()
    for row in table:
        id_num = row[0]
        surnames = row[1]
        given_names = row[2]
        all_ids_names.add((id_num, surnames, given_names))
    # pairwise comparison of all names
    id_merges = list(filter(None, [(x, y) if name_order_compare(x, y) else None
                                   for i, x in enumerate(all_ids_names)
                                   for j, y in enumerate(all_ids_names) if i > j]))
    for idx, row in enumerate(table):
        for idm in id_merges:
            if idm[0] == row[0]:
                table[idx][0] = idm[1]
    return table


def name_order_compare(name_tuple1, name_tuple2):
    """if two names are sufficiently similar but for name order, give the OK to merge IDs"""
    merge = False
    surnames1, surnames2 = name_tuple1[1].split(), name_tuple2[1].split()
    given_names1, given_names2 = name_tuple1[2].split(), name_tuple2[2].split()
    # if identical multiple surnames, and a match on at least one given name, merge IDs
    if surnames1 == surnames2 and len(surnames1) > 1:
        if set(given_names1) & set(given_names2):
            merge = True
    # if identical multiple given names and a match on at least one surname, merge IDs
    if given_names1 == given_names2 and len(given_names1) > 1:
        if set(surnames1) & set(surnames2):
            merge = True
    return merge


def get_overlap_ids(ym_unit_dict):
    """
    extract ids with >1 unit per year-month (can't be in two places at once) and return dict of these
    NB: there are two IDs that have multiple identical entries for the same time period, which reflects the
        info in the base data tables; not much can be done here, leave as noise
    """
    overlap_ids = set()
    for ID in ym_unit_dict:
        for yms in ym_unit_dict[ID]:
            if len(ym_unit_dict[ID][yms]) > 1:
                overlap_ids.add(ID)
    return overlap_ids
