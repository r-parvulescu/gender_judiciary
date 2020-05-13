"""
Functions for cleaning up irregularities in the data.
"""

import csv
import json
import itertools
from operator import itemgetter
import Levenshtein
from datetime import datetime


def clean(ppt, change_dict, range_years, year):
    """
    Applies cleaners to a person-period table it until there's nothing left to clean

    The optimal order in which to run the cleaners is unclear (but see comments for some constraints on order).
    Consequently, I keep running the cleaner until it stop changing anything, i.e. until it has converged
    on some maximal name cleanliness.

    :param ppt: a person-period table (e.g. person-years) as a list of lists
    :param change_dict: a dict where we record before (key) and after (value) state changes
    :param range_years: int, how many years our data covers
    :param year: bool, True if it's a person-year table, False if it's a person-month table
    :return cleaned person-period table
    """

    # let us know if we're working on a year or month table
    print('  CLEANING YEAR TABLE') if year else print('CLEANING MONTH TABLE')
    print('    TABLE LENGTH AT BEGINNING: ', len(ppt))

    # indicate each function run by the time it begins
    time = datetime.now().time().strftime('%P-%I-%M-%S')

    # add new value for the time of the run
    change_dict[time] = {}

    # start state, unique number of full names
    preclean_num_fullnames = len({row[0] + ' ' + row[1] for row in ppt})

    # run cleaners

    # "move_surname" assumes we have original name order from the data collector, which the next function
    # ("name_order") explicitly undoes. So, "move_surname" must always go first.
    print('      RUNNING: MOVE SURNAME')
    ppt = move_surname(ppt, change_dict, time)

    # It's probably more efficient for 'name_order' to run immediately after "move_surname", so that all
    # subsequent cleaners work with order-standardised names.
    print('      RUNNING: NAME ORDER')
    ppt = name_order(ppt)

    print('      RUNNING: LENGTHEN SURNAME')
    ppt = lengthen_name(ppt, change_dict, time, range_years, surname=True, year=year)

    print('      RUNNING: LENGTHEN GIVEN NAME')
    ppt = lengthen_name(ppt, change_dict, time, range_years, surname=False, year=year)

    # cleans up 1-character differences in long names
    print('      RUNNING: STANDARDISE LONG FULL NAMES')
    ppt = standardise_long_full_names(ppt, change_dict, time)

    # this thrives on long names, best put after name lengtheners and long name standardiser
    print('      RUNNING: MANY NAME SHARE')
    ppt = many_name_share(ppt, change_dict, time)

    # end state, unique number of full names
    postclean_num_fullnames = len({row[0] + ' ' + row[1] for row in ppt})

    # show what this run has accomplished
    print("    NUMBER OF FULL NAMES STANDARDISED: ", (preclean_num_fullnames - postclean_num_fullnames))
    print("    TABLE LENGTH AT END: ", len(ppt))

    # keep running the cleaners until we are no longer standardising names
    if postclean_num_fullnames == preclean_num_fullnames:
        return sorted(ppt, key=itemgetter(0, 1, 3)) if year else sorted(ppt, key=itemgetter(0, 1, 3, 4))
    else:
        print('-------------NAME CLEANER RECURSED-------------')
        return clean(ppt, change_dict, range_years, year=year)  # recurse


def make_log_file(change_dict, out_path):
    """
    Makes a log file (as csv) of before and after states, so we can see what our cleaners did.
    :param change_dict: a three level dict binning before-after changes by the function that did the
            changes and the run of 'clean' in which they took place.
            e.g. {
                  'time_of_run_1' : {'func1' : {'before1' : 'after1', 'before2' : 'after2'},
                  'time_of_run_2' : {'func2' : {'before1' : 'after1', 'before2' : 'after2'}
                   }
    :param out_path: where the log file will live
    :return: None
    """

    with open(out_path, 'w') as out_p:
        writer = csv.writer(out_p)
        writer.writerow(['time', 'function', 'before', 'after'])
        for time, funcs in change_dict.items():  # run-level, key = time of run
            for function, transforms in funcs.items():  # function level, key = e.g. "move surname"
                for before, after in transforms.items():  # transform level, key = what we changed
                    writer.writerow([time, function, before, after])


def move_surname(person_period_table, change_dict, time):
    """
    A surname may be incorrectly marked as a given name, from an error in the data or in the function
    that collects the data into a csv. If we have the format SURNAME | GIVEN NAME we may see

    (A) surname before the given name, e.g. ŞESTACOVSCHI | MOANGĂ SIMONA

    (B) surname at the end of the given name, e.g. CORNOIU | VICTOR JITĂRAŞU

    (C) maiden name (in brackets) at the end of given names, e.g. MUNTEANU RETEVOESCU | ANA MARIA (DUMBRAVĂ)

    (D) whole name tacked at the end of given names, e.g. HERP DERP | BOB JOE SMITHERS MARK

    This function corrects these mistakes, moving the surname in the correct field for (A), (B), and (C),
    and moving the fullname in (D) to a new person-period row.

    NB: whether a name is a surname can be read from ro_gender_dict.txt
    NB: since parentheses give no more useful information after moving the surname, remove them at the end

    :param person_period_table: a table of person-periods (e.g. person-years) as a list of lists
    :param change_dict: a dict in which we mark before (key) and after (value) states
    :param time: time string that stamps in which run of the clean function the changes below occurred
    :return a person-period table with surnames/fullnames in the appropriate places
    """

    func = 'move_surname'
    change_dict[time][func] = {}
    corrected_data_table = []

    with open('prep/gender/ro_gender_dict.txt') as gd:
        gender_dict = json.load(gd)
        for row in person_period_table:
            names = list(filter(None, row[1].split(' ')))
            misplaced_surname = ''
            for name in names:
                try:
                    if gender_dict[name] == 'surname':
                        misplaced_surname = misplaced_surname + name
                except KeyError:
                    print('        THIS NAME NOT IN GENDER DICTIONARY: ', name)

            if misplaced_surname:

                # (A) surname at beginning of given names, e.g. ŞESTACOVSCHI | MOANGĂ SIMONA
                # solution: correct original row
                if misplaced_surname[:3] == row[1][:3]:
                    surname = str(row[0] + ' ' + misplaced_surname).replace('(', '').replace(')', '')
                    given_name = row[1].replace(misplaced_surname, '').strip()
                    new_row = [surname, given_name] + row[2:]
                    corrected_data_table.append(new_row)
                    # log fullname change
                    change_dict[time][func][row[0] + ' | ' + row[1]] = surname + ' | ' + given_name

                # (B) surname at end of given names, e.g. CORNOIU | VICTOR JITĂRAŞU
                # solution: correct original row
                elif misplaced_surname[-3:] == row[1][-3:]:
                    surname = str(row[0] + ' ' + row[1].split()[-1]).replace('(', '').replace(')', '')
                    given_name = row[1].replace(misplaced_surname, '').strip()
                    new_row = [surname, given_name] + row[2:]
                    corrected_data_table.append(new_row)
                    # log fullname change
                    change_dict[time][func][row[0] + ' | ' + row[1]] = surname + ' | ' + given_name

                # (C) maiden name (in parentheses) tacked after given names,
                # e.g. MUNTEANU RETEVOESCU | ANA MARIA (DUMBRAVĂ)
                # solution: correct original row
                elif misplaced_surname[0] == '(':
                    surname = str(row[0] + misplaced_surname).replace('(', '').replace(')', '')
                    given_name = row[1].replace(misplaced_surname, '').strip()
                    new_row = [surname, given_name] + row[2:]
                    corrected_data_table.append(new_row)
                    # log fullname change
                    change_dict[time][func][row[0] + ' | ' + row[1]] = surname + ' | ' + given_name

                # (D) fullname (of other person) at end of given names
                # e.g. VĂCARU | CLAUDIA IULIANA VÂJLOI ANDREEA ILEANA
                # solution: correct original row, make new row for extra fullname
                else:
                    start_other_fullname = row[1].find(misplaced_surname)
                    other_fullname = row[1][start_other_fullname:].strip().split(' ')
                    other_surname = other_fullname[0].replace('(', '').replace(')', '')
                    other_given_name = ' '.join(other_fullname[1:])

                    own_surname = row[0].replace('(', '').replace(')', '')
                    own_given_name = row[1].replace(row[1][start_other_fullname:], '').strip()

                    old_row = [own_surname] + [own_given_name] + row[2:]
                    new_row = [other_surname, other_given_name] + row[2:]

                    corrected_data_table.append(old_row)
                    corrected_data_table.append(new_row)

                    # log fullname changes
                    change_dict[time][func][row[0] + ' | ' + row[1]] = (own_surname + ' | ' + own_given_name,
                                                                        other_surname + ' | ' + other_given_name)
            else:
                # eliminate parentheses in all other surnames too
                surname = row[0].replace('(', '').replace(')', '')
                corrected_data_table.append([surname] + row[1:])
    return deduplicate_list_of_lists(corrected_data_table)


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

    NB: this sorting is a bit unnatural since it puts all diacritic letters after Z, (e;g; the order is
    [SARDU, ZUH, ŞERBAN], not [SARDU, ŞERBAN ZUH] but this doesn't matter so long as it's consistent.

    :param person_period_table: a table of person-periods (e.g. person-years) as a list of lists
    :return a person period-table with one standardised name that ignores within-surname and
            within-given name order
    """

    name_sorted_table = []
    for row in person_period_table:
        sorted_surnames = ' '.join(sorted(row[0].split()))
        sorted_given_names = ' '.join(sorted(row[1].split()))
        name_sorted_table.append([sorted_surnames, sorted_given_names] + row[2:])
    return deduplicate_list_of_lists(name_sorted_table)


def lengthen_name(person_period_table, change_dict, time, range_years, surname=True, year=False):
    """
    for reasons of real change or data input inconsistency, a person's name may change over time.
    For example, marriage leads to surname change, or you change employer and your new workplace
    does not record your middle name.

    Thus we have cases like the following:

    (A)                                         (B)

    SURNAME    GIVEN NAME    MONTH/YEAR         SURNAME    GIVEN NAME    MONTH/YEAR

    DERP       BOB JOE       03/2012            DERP       BOB           03/2012
    DERP       BOB JOE       04/2012            DERP       BOB           04/2012
    DERP HERP  BOB JOE       05/2012            DERP       BOB JOE       05/2012
    DERP HERP  BOB JOE       06/2012            DERP       BOB JOE       06/2012
    HERP       BOB J         07/2012
    HERP       BOB JOE       08/2012


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

    NB: this function assumes that rows are unique, grouped by person-year, and consecutive in time

    NB: this function will NOT find name changes from single-name surnames to other
    single-name versions. So it WON'T catch DERP BOB JOE --> HERP BOB JOE; it likewise won't catch
    "DERP BOB" to "DERP JOE". This is intentional: those shorter names are common enough that you risk
    false positives, i.e. actually different people.

    NB: ensure the names have different numbers of components, so you don't end up with DERP BOB JOE --> DERP BOB MOE

    KNOWN BUG: when run on the post-2005 month data this function increases the number of rows by ~300 BEFORE
    deduplication. After deduplication we have less rows than we came in, again on the order of several hundred.
    Whatever duplication this function mightt therefore do in the step, the second seems to undo. Even if this is
    pure error, the degree of change in table size (several hundred out of ~700,000 rows) is on the order of
    0.05 of a percent.

    :param person_period_table: a table of person-periods (e.g. person-years) as a list of lists
    :param range_years: int, how many years our data covers
    :param change_dict: a dict in which we mark before (key) and after (value) states
    :param time: time string that stamps in which run of the clean function the changes below occurred
    :param surname: bool, True if we're lengthening surnames, False for given names
    :param year: bool, True if it's a person-year table, False if it's a person-month table
    :return a person-period table with maximal surnames
    """

    # if year-data, sort by surname (row[0]), year (row[3])
    # if month-data, sort also by given name (row[1]) and month (row[4])
    person_period_table.sort(key=itemgetter(0, 1, 3)) if year \
        else person_period_table.sort(key=itemgetter(0, 1, 3, 4))

    func = 'lengthen_name-surname' if surname else 'lengthen_name-given_name'
    change_dict[time][func] = {}
    long_name_table = []

    # switch for whether we're lengthening surnames or given names
    name_idx = 0 if surname else 1

    # search person-period table for too-short names and where possible lengthen them
    start_search = 0
    while start_search < len(person_period_table) - 1:

        # get index of first row with multiple names
        # if you hit end of table before finding, default to last entry
        first_multi_name_row = next((row for row in person_period_table[start_search:]
                                     if len(row[name_idx].split()) > 1),
                                    person_period_table[len(person_period_table) - 1])

        # get bounds of person-level sequence (viz. which looks like that in the docstring example)
        # that is centered on first_multi_name_row
        low_bound, high_bound = get_sequence_bounds(person_period_table, first_multi_name_row,
                                                    range_years, surname=surname, year=year)

        # find longest name in the sequence
        # NB: if several names are equally long, this code always uses the first name we hit -- this decision is
        # arbitrary, and inconsequential so long as it is consistently applied
        longest_n = ''
        for row in person_period_table[low_bound: high_bound]:
            if len(row[name_idx]) > len(longest_n):
                longest_n = row[name_idx]

        # reintroduce skipped rows
        long_name_table.extend(person_period_table[start_search: low_bound])

        # keep track of the names we're changing
        changed_names = set()

        # reintroduce sequence rows, updated with maximised surname
        for row in person_period_table[low_bound: high_bound]:
            # avoid mistakes like
            # ANDREI | LAURA VALI --> ANDREI | LAURA MARINA
            # yes the second name is longer, but these are actually different people
            # the trick is to avoid changing names which have the same number of components: in the example above,
            # both names have three components, so we don't change -- recall, we want to lengthen, not swap
            if len(longest_n.split()) != len(row[name_idx].split()):
                long_name_table.append([longest_n] + row[1:]) if surname \
                    else long_name_table.append([row[0]] + [longest_n] + row[2:])
                changed_names.add(row[0] + ' | ' + row[1])

            else:
                long_name_table.append(row)

        # update the change log
        for cn in changed_names:
            if surname:
                change_dict[time][func][cn] = longest_n + ' | ' + cn.split(' | ')[1]
            else:
                change_dict[time][func][cn] = cn.split(' | ')[0] + ' | ' + longest_n

        # move up the index from whence we'll start the next search
        start_search = high_bound

    return deduplicate_list_of_lists(long_name_table)


def get_sequence_bounds(pers_per_tab, ref_row, range_years, surname=False, year=False):
    """
    Find the first and last index of a (sub)list of time-consecutive person-period rows,
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
        ffd_idx += 1

    return bfd_idx, ffd_idx


def standardise_long_full_names(person_period_table, change_dict, time):
    """
    some names are off by one character, due to inconsistent diacritic use for faulty input. For instance,

    SURNAME    GIVEN NAME    MONTH/YEAR

    DERP HERP  BOB ŞERBAN    03/2012
    ERP HERP   BOB ŞERBAN    04/2012
    HERP DERP  BOB SERBAN    05/2012
    HERP DERP  BO  SERBAN    06/2012

    It's quite obvious that all these variants refer to the same person. On the other hand, we know that
    some differences are real: DERP HERP JOEL is probably somebody else. We're more confident in our
    assumption that several names refer to the same person when the names, though long, differ by only a
    few characters.

    We code in this assumptions by only equating names that feature 3+ components or 20+ characters AND they differ
    by only one character.

    :param person_period_table: a table of person-periods (e.g. person-years) as a list of lists
    :param change_dict: a dict in which we mark before (key) and after (value) states
    :param time: time string that stamps in which run of the clean function the changes below occurred
    :return a cleaned person-period table, with fewer fullname variation / more standard fullnames
    """

    change_dict[time]['standardise_long_full_names'] = {}
    standardised_names_table = []

    # get list (with duplicates) of full names that feature 3+ names or are 20+ characters long
    full_names = sorted([(row[0] + ' | ' + row[1]) for row in person_period_table
                         if (len(row[0].split()) + len(row[1].split()) >= 3)
                         or len(row[0] + row[1]) >= 20])
    # get each fullname's frequency in terms of associated rows
    fullname_freqs = {k: len(g) for k, [*g] in itertools.groupby(sorted(full_names))}

    # initialise the translation dictionary that we'll use for name updating
    trans_dict = {}

    # if full names differ by 1 character and at least one surname has 4+ letters (avoids MOS --> POP situations),
    # use the version that appears more often
    fns_1apart = pairwise_ldist(set(full_names), 1)
    for fn_pair in fns_1apart:
        if len(fn_pair[0].split(' | ')[0]) > 3:
            if fullname_freqs[fn_pair[0]] >= fullname_freqs[fn_pair[1]]:
                trans_dict[fn_pair[1]] = fn_pair[0]
            else:
                trans_dict[fn_pair[0]] = fn_pair[1]

    # apply the translation dictionary
    for row in person_period_table:
        if (row[0] + ' | ' + row[1]) in trans_dict:
            fullname_split = trans_dict[(row[0] + ' | ' + row[1])].split(' | ')
            new_surname = fullname_split[0]
            new_given_name = fullname_split[1]
            standardised_names_table.append([new_surname, new_given_name] + row[2:])
        else:
            standardised_names_table.append(row)
    # add the translation dictionary to the change log
    for k, v in trans_dict.items():
        change_dict[time]['standardise_long_full_names'][k] = v

    # TODO put example in the test csv to test this function; I feel like there's an example missing here...

    return deduplicate_list_of_lists(standardised_names_table)


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


def many_name_share(person_period_table, change_dict, time):
    """
    Some names share many components. For instance, "HERP | ION IOSIF" and "DERP HERP | ION IOSIF" have
    three name components in common. I assume that if two names share three or more components they refer
    to the same person, regardless of any other information. This function turns the shorter into the longer
    version: e.g. "HERP | ION IOSIF" --> "DERP HERP | ION IOSIF".

    NB: this function uses sets so identical components in one name will be collapsed. For instance,
    SCOTT | PAUL SCOTT (unusual for surname and given name to share a component, but not unheard of) becomes
    {SCOTT, PAUL} -- recall, sets have no order. This tends to shorten names and makes it less likely for them
    to hit the 3+ name-count floor above which we make comparisons. So we risk more false negative than
    positive, which is fine since there are more deduplicators after this one.

    :param person_period_table: a table of person-periods (e.g. person-years) as a list of lists
    :param change_dict: a dict in which we mark before (key) and after (value) states
    :param time: time string that stamps in which run of the clean function the changes below occurred
    :return: a person-period table with the longest version of the names with 3+ component overlaps.
    """

    change_dict[time]['many_name_share'] = {}
    longest_names_table = []

    # initialise the translation dictionary that we'll use for name updating
    trans_dict = {}

    # make list of tuples where 'tuple[0] = full name' and 'tuple[1] = bag of (unique) name components'
    full_name_bags = []
    for row in person_period_table:
        full_name_string = row[0] + ' | ' + row[1]
        name_components = set(row[0].split()) | set(row[1].split())
        # no duplicates in list, only names with 3+ components
        if len(name_components) >= 3 and (full_name_string, name_components) not in full_name_bags:
            full_name_bags.append((full_name_string, name_components))

    # pairwise compare all fullname bags (lower triangular, no diagonal)
    for i, x in enumerate(full_name_bags):
        for j, y in enumerate(full_name_bags):
            if i > j:
                # if names share at least three components, and have different number of components
                if len(x[1] & y[1]) >= 3 and len(x[1]) != len(y[1]):
                    # go with longer name
                    if len(x[1]) >= len(y[1]):
                        trans_dict[y[0]] = x[0]
                    else:
                        trans_dict[x[0]] = y[0]

    # apply the translation dictionary
    for row in person_period_table:
        if (row[0] + ' | ' + row[1]) in trans_dict:
            fullname_split = trans_dict[(row[0] + ' | ' + row[1])].split(' | ')
            new_surname = fullname_split[0]
            new_given_name = fullname_split[1]
            longest_names_table.append([new_surname, new_given_name] + row[2:])
        else:
            longest_names_table.append(row)

    # add the translation dictionary to the change log
    for k, v in trans_dict.items():
        change_dict[time]['many_name_share'][k] = v

    return deduplicate_list_of_lists(longest_names_table)


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


'''
import pandas as pd
if __name__ == '__main__':
    person_p_table = pd.read_csv('test/test_years_table.csv').values.tolist()
    c_dict = {}
    clean_table = clean(person_p_table, c_dict, 30, year=False)
    #[print(row) for row in clean_table]
'''