"""
Functions for cleaning up irregularities in the data.
"""

import pandas as pd
import json
from datetime import datetime
from operator import itemgetter


def clean(person_period_table, range_years, year):
    """
    applies cleaners to a person-period table it until there's nothing left to clean
    :param person_period_table: a table of person-periods (e.g. person-years) as a list of lists
    :param range_years: int, how many years our data covers
    :param year: bool, True if it's a person-year table, False if it's a person-month table
    :return cleaned person-period table
    """

    # see where we're starting from
    preclean_num_fullnames = len({row[0] + ' ' + row[1] for row in person_period_table})
    preclean_num_rows = len(person_period_table)

    # run the cleaners
    person_period_table = move_surname(person_period_table)
    person_period_table = name_order(person_period_table)
    person_period_table = lengthen_name(person_period_table, range_years, surname=True, year=year)
    person_period_table = lengthen_name(person_period_table, range_years, surname=False, year=year)
    # person_period_table = standardise_long_fullnames(person_period_table)
    # person_period_table = remove_overlaps(person_period_table)

    postclean_num_fullnames = len({row[0] + ' ' + row[1] for row in person_period_table})
    postclean_num_rows = len(person_period_table)

    # keep running the cleaners until each additional run is not adding anything
    # if nothing is being added, return the cleaned table

    if postclean_num_fullnames == preclean_num_fullnames:
        return person_period_table
    else:
        print("NUMBER OF FULLNAMES REDUCED: ", (preclean_num_fullnames - postclean_num_fullnames))
        print("NUMBER OF ROWS REDUCED: ", (preclean_num_rows - postclean_num_rows))
        print("RECURSED AT TIME: ", datetime.now().time())
        return clean(person_period_table, range_years, year=year)  # recurse


def move_surname(person_period_table):
    """
    if a surname has been incorrectly marked as a given name (which can be read from the gender dictionary)
    takes that name out of the given name string and appends it to the surname string
    retun clean table
    """
    corrected_data_table = []
    with open('gender/ro_gender_dict.txt') as gd:
        gender_dict = json.load(gd)
        for row in person_period_table:
            names = list(filter(None, row[1].split(' ')))
            misplaced_surname = ''
            for name in names:
                if gender_dict[name] == 'surname':
                    misplaced_surname = misplaced_surname + name
            if misplaced_surname:
                # surname at beginning of given names, correct row
                # e.g. ŞESTACOVSCHI | MOANGĂ SIMONA
                if misplaced_surname[:3] == row[1][:3]:
                    surname = row[0] + ' ' + misplaced_surname
                    given_name = row[1].replace(misplaced_surname, '').strip()
                    new_row = [surname, given_name] + row[2:]
                    corrected_data_table.append(new_row)
                # surname at end of given names, correct row
                # e.g. CORNOIU | VICTOR JITĂRAŞU'
                elif misplaced_surname[-3:] == row[1][-3:]:
                    surname = row[0] + ' ' + row[1].split()[-1]
                    given_name = row[1].replace(misplaced_surname, '').strip()
                    new_row = [surname, given_name] + row[2:]
                    corrected_data_table.append(new_row)
                # maiden name tacked at the end of given names, append to surnames
                # e.g. MUNTEANU RETEVOESCU | ANA MARIA (DUMBRAVĂ)
                elif misplaced_surname[0] == '(':
                    surname = row[0] + misplaced_surname
                    given_name = row[1].replace(misplaced_surname, '').strip()
                    new_row = [surname, given_name] + row[2:]
                    corrected_data_table.append(new_row)
                # whole fullname (of other person) at end of given name,
                # remove fullname from old row, make new row out of it
                else:
                    # TODO get an example of this so I can put it in the test file
                    start_name = row[1].find(misplaced_surname)
                    other_person = row[1][start_name:].strip().split(' ')
                    surname = other_person[0]
                    given_name = other_person[1]
                    new_row = [surname, given_name] + row[2:]
                    old_row = [row[0]] + [row[1].replace(row[1][start_name:], '').strip()] + row[2:]
                    corrected_data_table.append(old_row)
                    corrected_data_table.append(new_row)
            else:
                corrected_data_table.append(row)
    return corrected_data_table


def lengthen_name(person_period_table, range_years, surname=True, year=False):
    """
    for reasons of real change or data input inconsistency, a person's name may change over time.
    For example, marriage leads to surname change, or you change employer and your new workplace
    does not record your middle name.

    Thus we have cases like the following:

    (A)

    SURNAME    GIVEN NAME    MONTH/YEAR

    DERP       BOB JOE       03/2012
    DERP       BOB JOE       04/2012
    DERP HERP  BOB JOE       05/2012
    DERP HERP  BOB JOE       06/2012
    HERP       BOB JOE       07/2012
    HERP       BOB JOE       08/2012

    (B)

    SURNAME    GIVEN NAME    MONTH/YEAR

    DERP       BOB           03/2012
    DERP       BOB           04/2012
    DERP       BOB JOE       05/2012
    DERP       BOB JOE       06/2012


    In (A), our observation of BOB JOE's career features a second surname partway in, followed by the loss
    of the original surname. In other cases we may not observe a full surname transition: perhaps we just
    see DERP --> DERP HERP, or DERP HERP --> HERP. In (B), we observe a second given name appearing partway
    through the career; again, other name transitions are possible.

    In both of these cases we assume that such row sequences do not refer to different people, but to just
    one person whose record suffered name changes, This one-person assumption relies on:
        a) sequence elements being consecutive in time,
        b) at least some name overlap between consecutive sequence elements:
            "DERP" and "HERP DERP" have one component in common, as do "BOB" and "BOB JOE".

    This function finds all sequences like the one above and applies the longest name to all sequence
    elements: for (A) it's "DERP HERP BOB JOE", while for (B) it's "DERP BOB JOE". So all rows will have
    that longest name after this function runs.

    Doing this throws out information on name transition, but makes it easier to identify unique persons,
    which is the purpose of this module.

    NOTE: this function will NOT find name changes from single-name surnames to other
    single-name versions. So it WON'T catch DERP BOB JOE --> HERP BOB JOE; it likewise won't catch
    "DERP BOB" to "DERP JOE". This is intentional: those shorter names are common enough that you risk
    false positives, i.e. actually different people.

    :param person_period_table: a table of person-periods (e.g. person-years) as a list of lists
    :param range_years: int, how many years our data covers
    :param surname: bool, True if we're lengthening surnames, False for given names
    :param year: bool, True if it's a person-year table, False if it's a person-month table
    :return a person-period table with maximal surnames
    """

    # sort table by surname (row[0]), year (row[3]) and, if month-level table, month (row[4])
    person_period_table.sort(key=itemgetter(0, 3)) if year \
        else person_period_table.sort(key=itemgetter(0, 3, 4))

    # switch for whether we're lengthening surnames or given names
    name_idx = 0 if surname else 1

    # table where we'll build the person-period table with maximal long name versions
    long_name_table = []
    # go through the whole table
    start_search = 0
    while start_search < len(person_period_table) - 1:
        # get index of first row with multiple names
        # if you hit end of table before finding, default to last entry
        first_ns_row = next((row for row in person_period_table[start_search:]
                             if len(row[name_idx].split()) > 1),
                            person_period_table[len(person_period_table) - 1])

        # get bounds of person-level sequence (viz. which looks like that in the docstring example)
        # that is centered on first_ns_row
        low_bound, high_bound = get_sequence_bounds(person_period_table, first_ns_row,
                                                    range_years, surname=surname, year=year)

        # find longest name in sequence
        longest_n = ''
        for row in person_period_table[low_bound: high_bound]:
            if len(row[name_idx]) > len(longest_n):
                longest_n = row[name_idx]

        # reintroduce skipped rows
        long_name_table.extend(person_period_table[start_search: low_bound])
        # reintroduce sequence rows, updated with maximised surname
        if surname:
            long_name_table.extend([[longest_n] + row[1:]
                                    for row in person_period_table[low_bound: high_bound]])
        else:
            long_name_table.extend([[row[0]] + [longest_n] + row[2:]
                                    for row in person_period_table[low_bound: high_bound]])
        # move up the index from whence we'll start the next search
        start_search = high_bound

    if len(long_name_table) != len(person_period_table):
        raise ValueError("RETURN LIST TABLE DIFFERENT LENGHT THAN INPUT TABLE")
    else:
        return long_name_table


def get_sequence_bounds(pers_per_tab, ref_row, range_years, surname=False, year=False):
    """
    find the first and last index of a (sub)list of time-consecutive person-period rows,
    where each row shares a) at least one surname, b) identical given names

    :param pers_per_tab: a person-period table (as a list of lists) sorted by last name and time-unit
    :param ref_row: the reference row (as a list), from where we begin looking forward and backward
    :param range_years: int, how many years our data covers
    :param surname: bool, True if we're lengthening surnames, False for given names
    :param year: bool, True if it's a person-year table, False if it's a person-month table
    :return (bfd_idx, ffd_idx), tuple of the start and end of the sublist
    """
    ref_idx = pers_per_tab.index(ref_row)  # index of the reference row

    # it's not sensible to search further than the max number of years in the data set,
    # constrain search area by that number to reduce search load
    max_time = range_years if year else range_years * 12

    # recall
    # for surnames: we search until a) there are no more surnames in common  or b) given names change
    # for given names: we search until a) there are no more given names in common  or b) surnames change

    # switch for whether we're lengthening surnames or given names
    name_idxs = (0, 1) if surname else (1, 0)

    # forward search; if you don't hit conditions assume you're at table end, default to last row
    f_max_range = min(ref_idx + max_time, len(pers_per_tab) - 1)  # avoid going over table bound
    forward_search_range = pers_per_tab[ref_idx: f_max_range + 1]
    forward_first_different = next((row for row in forward_search_range
                                    if not set(ref_row[name_idxs[0]].split()) & set(row[name_idxs[0]].split())
                                    or ref_row[name_idxs[1]] != row[name_idxs[1]]),
                                   pers_per_tab[f_max_range])
    ffd_idx = pers_per_tab.index(forward_first_different)

    # backward search; if you don't hit conditions assume you're at table start, default to first row
    b_max_range = max(ref_idx - max_time, 0)  # avoid going under table bound
    backward_search_range = list(reversed(pers_per_tab[b_max_range: ref_idx]))
    backward_first_different = next((row for row in backward_search_range
                                     if not set(ref_row[name_idxs[0]].split()) & set(row[name_idxs[0]].split())
                                     or ref_row[name_idxs[1]] != row[name_idxs[1]]),
                                    pers_per_tab[b_max_range])
    bfd_idx = pers_per_tab.index(backward_first_different)

    # include edges of table, even if they aren't different from the next-closest entries,
    if bfd_idx != 0:
        bfd_idx += 1
    if ffd_idx == len(pers_per_tab) - 1:
        ffd_idx = ffd_idx + 1

    return bfd_idx, ffd_idx


def name_order(person_period_table):
    """
    ignore name order within surnames and given names and sort each alphabetically.  For example, all of:

    SURNAME    GIVEN NAME    MONTH/YEAR

    DERP HERP  BOB JOE       03/2012
    DERP HERP  JOE BOB       04/2012
    HERP DERP  BOB JOE       05/2012
    HERP DERP  JOE BOB       06/2012

    Would become "DERP HERP BOB JOE". The assumption here is that names are sufficient identifiers on
    their own and that name order adds more noise than signal. So we standardise name order to make the
    signal from the name itself come out better.

    NB: this sorting is a bit unnatural since it puts all diacritic letters after Z, but this doesn't
    matter so long as it's consistent.

    :param person_period_table: a table of person-periods (e.g. person-years) as a list of lists
    :return a person period-table with one standardised name that ignores within-surname and
            within-given name order
    """

    sorted_table = []
    for row in person_period_table:
        sorted_surnames = ' '.join(sorted(row[0].split()))
        sorted_given_names = ' '.join(sorted(row[1].split()))
        sorted_table.append([sorted_surnames, sorted_given_names] + row[2:])
    return sorted_table


def standardise_long_fullnames(person_period_table):
    """
    if a fullname (surname + given name) is long (> 3 names), do pairwise comparison of all names by
    Levenshtein distance; if L-dist <= 2, use only one version of the fullname
    return table with standardised fullnames
    """

    pass


def remove_overlaps(person_period_table):
    """
    sometimes a person who changes place of employment is double-counted, because their receiving employer
    has put them on the new payroll, but their sending employer has not removed them from the old payroll.
    This function removes such double-count rows;
    returns table without double-count rows
    """

    pass


"""
        # get all surnames in the sequence, extract the longest one
        sns = {row[0] for row in person_period_table[low_bound: high_bound + 1]}
        longest_sn = max(sns, key=len)  # NB: if 2+ strings have max_len it picks one randomly, since set is unordered
        sns.remove(longest_sn)
        
        # replace all sns in sublist with longest surname
        # find the longest surname in the sublist"""

if __name__ == '__main__':
    ppt = pd.read_csv('test_table.csv').values.tolist()
    # [print(row) for row in person_period_table]
    clean_table = clean(ppt, 30, year=False)
    [print(row) for row in clean_table]

    # TODO idea: randomness is useful, and randomness is precisely that whih we can't control or account for
    # in other words, that which arises from open systems (in the CR sense); hence one core usefulness
    # of open systems is that they give randomness
