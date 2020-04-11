"""
Helper functions for handling rows and translation dictionaries.
"""


def get_given_names(row):
    """return a list of given names in row"""
    return row[1].split()


def make_fullname(row):
    """given row, concatenate surnames and given names into fullname, separated by pipe"""
    return row[0] + ' | ' + row[1]


def surname_given_name(row):
    """given row, return tuple of first two entries, surname and given name respectively"""
    return row[0], row[1]


def row_with_fullname(row):
    """returns row starting with fullname instead of surname and given name separately"""
    return [make_fullname(row)] + row[2:]


def make_row(row, name, name_type):
    """return row updated with new name"""
    if name_type == "fullnames":
        return name.split(' | ') + row[2:]
    elif name_type == "surnames":
        return [name] + row[1:]
    else:
        return [row[0]] + [name] + row[2:]
