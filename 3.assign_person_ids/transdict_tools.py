"""
Helper functions for handling translation dictionaries.
"""

import re
import json
import iter_helpers
import row_helpers


def multi_transdict_table_updater(table, make_td=False):
    """update table with all three name transdicts, return updated table"""

    table = iter_helpers.collect_of_row_results(table, "list", lambda x: x)
    order = ["fullnames", "surnames", "given_names"]
    for o in order:
        if make_td:
            transdict_maker(table, o)
        o_transdict = "transdicts/" + o + "_transdict.txt"
        table = single_transdict_table_updater(table, o_transdict, o)
    return table


def single_transdict_table_updater(table, trans_dict, name_type):
    """update a table from csv file using the translation dictionaries"""
    with open(trans_dict, 'r') as td:
        t_dict = json.load(td)
    new_table = []
    for row in table:
        if name_type == "fullnames":
            old_name = row_helpers.make_fullname(row)
        elif name_type == "surnames":
            old_name = row[0]
        else:
            old_name = row[1]
        new_name = text_replacer(old_name, t_dict)
        new_row = row_helpers.make_row(row, new_name, name_type)
        new_table.append(new_row)
    return new_table


def set_transdict_entry(transdict, name1, name2, name1_rows, name2_rows):
    """set new entry in translation dictionary, preferring fullname with bigger row count; never overwrite"""
    if name1_rows >= name2_rows:
        if name2 not in transdict:
            transdict[name2] = name1
    else:
        if name1 not in transdict:
            transdict[name1] = name2


def transdict_maker(table, name_type):
    """make translation dictionary"""
    names_by_other_names = {}
    if name_type == "fullnames":
        unique_names = iter_helpers.collect_of_row_results(table, "set", row_helpers.make_fullname)
    elif name_type == "surnames":
        unique_names = iter_helpers.collect_of_row_results(table, "set", lambda x: x[0])
        names_by_other_names = iter_helpers.name_by_othername_count(table, 1000, name_type)
    else:
        unique_names = iter_helpers.collect_of_row_results(table, "set", lambda x: x[1])
        names_by_other_names = iter_helpers.name_by_othername_count(table, 1000, name_type)

    rows_per_name = iter_helpers.name_by_row_count(table, name_type)
    name_pairs = iter_helpers.string_tuple_by_ldist(unique_names, 1)

    trans_dict = {}
    for np in name_pairs:
        if name_type == "fullnames":
            surname_diacritic_chooser(trans_dict, np)
            rare_fullname_chooser(trans_dict, rows_per_name, np)
        else:
            rare_name_chooser(trans_dict, np, names_by_other_names, rows_per_name)

    td_file_name = "transdicts/" + name_type + "_transdict.txt"
    with open(td_file_name, 'w') as td:
        json.dump(trans_dict, td)


def surname_diacritic_chooser(trans_dict, fullname_pair):
    """if two fullnames differ in surname diacritics, use fullname with more surname diacritics"""
    fullname1 = fullname_pair[0]
    surname1 = fullname1.split(' | ')[0]

    fullname2 = fullname_pair[1]
    surname2 = fullname2.split(' | ')[0]

    if len(re.findall("Ş|Ţ|Ă|Â", surname1)) != len(re.findall("Ş|Ţ|Ă|Â", surname2)):
        if len(re.findall("Ş|Ţ|Ă|Â", surname1)) >= len(re.findall("Ş|Ţ|Ă|Â", surname2)):
            if fullname2 not in trans_dict:
                trans_dict[fullname2] = fullname1
        else:
            if fullname1 not in trans_dict:
                trans_dict[fullname1] = fullname2


def rare_fullname_chooser(trans_dict, rows_per_fullname, fullname_pair):
    """
    if one fullname in a pair is rare (less that six associated rows, i.e., less than six months)
    then use fullname with more rows
    """
    fullname1 = fullname_pair[0]
    fullname2 = fullname_pair[1]
    fn1_rows = rows_per_fullname[fullname1]
    fn2_rows = rows_per_fullname[fullname2]
    if fn1_rows < 6 or fn2_rows < 6:
        set_transdict_entry(trans_dict, fullname1, fullname2, fn1_rows, fn2_rows)


def rare_name_chooser(trans_dict, name_pair, name_by_other_name, rows_per_name):
    """
    if one name in pair is very rare (i.e. one associated other name AND less than six associated rows)
    then use name with more rows
    """
    name1 = name_pair[0]
    name2 = name_pair[1]
    n1_by_other_names = name_by_other_name[name1]
    n2_by_other_names = name_by_other_name[name2]
    n1_rows = rows_per_name[name1]
    n2_rows = rows_per_name[name2]
    if n1_by_other_names == 1 and n1_rows < 6:
        if n1_rows <= n2_rows:
            if name1 not in trans_dict:
                trans_dict[name1] = name2
    if n2_by_other_names == 1 and n2_rows < 6:
        if n2_rows <= n1_rows:
            if name2 not in trans_dict:
                trans_dict[name2] = name1


def text_replacer(name, trans_dict):
    """if name in transdict, return what it maps to, else return original"""
    if name in trans_dict:
        return trans_dict[name]
    else:
        return name


def visual_name_comparer(fullname_transdict, surname_transdict, surnames_by_gn_count, surname1, surname2,
                         fullname1, fullname2, fullname1_rows, fullname2_rows):
    """
    presents you with surname and fullnames to help you decide whether to include
    them in the transdict, which name to map to the other, and updates the transdict
    """

    print("%s, %s given name" % (surname1, surnames_by_gn_count[surname1]))
    print("  %s, %s given name(s)" % (surname2, surnames_by_gn_count[surname2]))
    print("%s, has %s rows" % (fullname1, fullname1_rows))
    print("  %s, has %s rows" % (fullname2, fullname2_rows))

    answer = input("Add to SURNAME translation dictionary? y/n ")
    if not ((answer == 'y') or (answer == 'n')):
        answer = input("    Incorrect format, please, add to SURNAME translation dictionary? y/n ")
    if answer == 'y':
        print("LEFT: %s -- RIGHT: %s" % (surname1, surname2))
        answer = input("in dict, do you want to change LEFT name or RIGHT name? l/r ")
        if not ((answer == 'l') or (answer == 'r')):
            answer = input("    Incorrect format, please, do you want to change LEFT name or RIGHT name? l/r ")
        if answer == "l":
            if surname1 not in surname_transdict:
                surname_transdict[surname1] = surname2
        else:
            if surname2 not in surname_transdict:
                surname_transdict[surname2] = surname1
        print("------------------------------------------------------------")
        return

    else:
        answer = input("Add to FULLNAME translation dictionary? y/n ")
        if not ((answer == 'y') or (answer == 'n')):
            answer = input("    Incorrect format, please, add to FULLNAME translation dictionary? y/n ")
        if answer == 'y':
            print("LEFT: %s -- RIGHT: %s" % (fullname1, fullname2))
            answer = input("in dict, do you want to change LEFT name or RIGHT name? l/r ")
            if not ((answer == 'l') or (answer == 'r')):
                answer = input(
                    "    Incorrect format, please, in dict, do want to change LEFT name or RIGHT name?? l/r ")
            if answer == "l":
                if fullname1 not in fullname_transdict:
                    fullname_transdict[fullname1] = surname2
            else:
                if fullname2 not in fullname_transdict:
                    fullname_transdict[fullname2] = surname1
            print("------------------------------------------------------------")
            return
    print("---------------------------------------------------------")
    return
