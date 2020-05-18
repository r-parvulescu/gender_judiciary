"""
Assign each person-year a unique, person-level ID.
"""

import operator
import itertools
import pandas as pd
import os
import csv
import dedupe
from unidecode import unidecode


def pids(csv_person_years, profession):
    """
    Takes a csv of person years, deduplicates it to make sure nobody is in two places at once, interpolates missing
    person-years, assigns a new column for distinct person-years, and writes the output to file.

    :param csv_person_years: a path to a csv file of with person-years
    :param profession: string, "judges", "prosecutors", "notaries" or "executori"
    :return: None
    """

    person_year_table = pd.read_csv(csv_person_years)
    person_year_table = person_year_table.values.tolist()

    # remove overlaps so no person is in 2+ places in one year
    distinct_persons = correct_overlaps(person_year_table, profession)

    # interpolate person-years that are missing for spurious reasons
    distinct_persons = interpolate_person_years(distinct_persons)

    # give each person-year a person-year ID
    distinct_persons = unique_person_ids(distinct_persons)

    distinct_persons.sort(key=operator.itemgetter(0))


def correct_overlaps(person_year_table, profession):
    """
    NB: !! this code only applies to person-year tables !! DO NOT APPLY TO PERSON MONTH TABLES

    NB: !! only do this for complete data, i.e. 2005 and later !!! WILL BE TOO GLITCHY ON INCOMPLETE DATA

    Sometimes we notice that a person is in two or more places at the same time. This can mean that

    a) two or more people share a name

    b) irregular/unusual book-keeping; common reasons for this include
        i) someone is added to the books of the new workplace BEFORE being taken off the rolls of the old workplace
        ii) being delegated from your workplace to another for a short period, so even though you work in each place
        several months, on the year level it will look like you were in two places at once

    We can distinguish between these scenarios by considering the length and the context of the overlap.

    1) if a person is in two or more places for 3+ years, it likely indicates a multiple people with shared a name,
    i.e. case a). Two years of allowable overlap might seem like a lot, but a transition mistake (as in b.i) only needs
    to get made for two calendar months (Dec and Jan), and for us to have gotten unlucky with month sampling,
    to generate a spurious two-year overlap.

    2) if the overlap is 1-2 years, and is located at the transition between workplaces, it's probably a
        book-keeping mistake as in b.i

    3) if the overlap is 1-2 years and does NOT mark a transition, it's probably a delegation period (case b.ii)

    4) if the overlap is 1-2 years and occurs at the edge of our observed sequences, it could either be situation (2)
       above (since we may not have observed the start or end state) or situation (3) above (since the delegation might
       fall at the edge of our observation period)

    All these cases are covered by the vignettes below -- I reference to these in code comments

    (A)  ONE YEAR OVERLAP, MID SEQUENCE                      (B)  TWO YEAR OVERLAP, MID SEQUENCE

    SURNAME    GIVEN NAME   INSTITUTION   YEAR               SURNAME    GIVEN NAME  INSTITUTION    YEAR

    DERP       BOB JOE      ALPHA         2012               DERP       BOB JOE     ALPHA          2012
    DERP       BOB JOE      ALPHA         2013               DERP       BOB JOE     ALPHA          2013
    DERP       BOB JOE      BETA          2013               DERP       BOB JOE     BETA           2013
    DERP       BOB JOE      BETA          2014               DERP       BOB JOE     ALPHA          2014
    DERP       BOB JOE      BETA          2015               DERP       BOB JOE     BETA           2014
    DERP       BOB JOE      BETA          2016               DERP       BOB JOE     BETA           2015

    Note that for (ii) to hold we need to observe a sending and receiving workplace. Cases (C), (D), and (E) below
    would NOT fall under the ambit of situation (ii), because we can't observe both sending and receiving workplaces.

    (C)  ONE YEAR OVERLAP, START SEQUENCE                    (D)  ONE YEAR OVERLAP, END SEQUENCE

    SURNAME    GIVEN NAME   INSTITUTION   YEAR               SURNAME    GIVEN NAME  INSTITUTION    YEAR

    DERP       BOB JOE      ALPHA         2012               DERP       BOB JOE     BETA           2012
    DERP       BOB JOE      BETA          2012               DERP       BOB JOE     BETA           2013
    DERP       BOB JOE      BETA          2013               DERP       BOB JOE     BETA           2014
    DERP       BOB JOE      BETA          2014               DERP       BOB JOE     BETA           2015
    DERP       BOB JOE      BETA          2015               DERP       BOB JOE     ALPHA          2015

    (E)  TWO YEAR OVERLAP, FULL SEQUENCE                    (F)  ONE YEAR OVERLAP, 3+ PLACES

    SURNAME    GIVEN NAME   INSTITUTION   YEAR              SURNAME    GIVEN NAME  INSTITUTION     YEAR

    DERP       BOB JOE     ALPHA          2012              DERP        BOB JOE     ALPHA           2012
    DERP       BOB JOE     BETA           2012              DERP        BOB JOE     ALPHA           2013
    DERP       BOB JOE     ALPHA          2013              DERP        BOB JOE     BETA            2013
    DERP       BOB JOE     BETA           2013              DERP        BOB JOE     GAMMA           2013
                                                            DERP        BOB JOE     BETA            2014

    (G)  THREE PLUS YEAR OVERLAP                            (H) TWO YEAR OVERLAP, NO TRANSITION

    SURNAME    GIVEN NAME   INSTITUTION   YEAR              SURNAME    GIVEN NAME  INSTITUTION     YEAR

    DERP       BOB JOE     ALPHA          2012              DERP        BOB JOE     ALPHA           2012
    DERP       BOB JOE     BETA           2012              DERP        BOB JOE     ALPHA           2013
    DERP       BOB JOE     ALPHA          2013              DERP        BOB JOE     BETA            2013
    DERP       BOB JOE     BETA           2013              DERP        BOB JOE     ALPHA           2014
    DERP       BOB JOE     ALPHA          2014              DERP        BOB JOE     BETA            2014
    DERP       BOB JOE     BETA           2014              DERP        BOB JOE     ALPHA           2015


    This function is built to remove overlaps in such a way that estimates of inter-year mobility are reduced,
    i.e. that we get conservative estimates of mobility. So when we have a choice as to which person-years to remove or
    split to remove the overlap, we go with that choice which will lead to less mobility being observed.

    :param person_year_table: a table of person-years, as a list of lists
    :param profession: string, "judges", "prosecutors", "notaries" or "executori"
    :return: a list of distinct persons, i.e. of person-sequences that feature no overlaps; this is a triple nested
             list: of person-sequences, which is made up of person-years, each of which is a list of person-year data
    """

    # sort the data by surname and given name
    person_year_table.sort(key=operator.itemgetter(1, 2, 4))  # surname = row[1], given name = row[2], year = row[4]

    # group data by surname and given name
    person_sequences = [group for k, [*group] in itertools.groupby(person_year_table, key=operator.itemgetter(1, 2))]

    # initialise a table of distinct persons; a three level list: a list of persons, each containing a list of
    # person-years (i.e. rows), and each row is a list
    distinct_persons = []

    # initialise table of person-sequences that are sufficiently strange and/or rare that we don't trust the function
    # to properly handle; later we'll inspect this table visually
    odd_person_sequences = []

    # initialise a log of changes for comparing before an after states of changed person-sequences, to visually inspect
    # what the function has done
    change_log = []

    for ps in person_sequences:

        # initialise a dict of years and the workplace(s) associated with each year
        years_and_workplaces = {row[4]: [] for row in ps}  # row[4] =  year

        # initialise a set that marks which year-workplace combinations should be removed to eliminate the overlap
        to_remove = set()

        # workplace overlap exists when there are fewer years than rows (since each row is a person-year)
        if len(years_and_workplaces) < len(ps):

            # associate workplaces with years
            [years_and_workplaces[row[4]].append(row[3]) for row in ps]  # row[3] = workplaces

            # CASE (F)
            # if one year features 3+ workplaces, set that person-sequence aside for manual inspection
            if max([len(v) for v in years_and_workplaces.values()]) > 2:
                odd_person_sequences.append(ps)

            else:  # no year features more than two institutions

                # CASE (G)
                # if the overlap is of 3+ years, split up the person-year
                if len(ps) - len(years_and_workplaces) > 2:
                    distinct_persons.extend(split_sequences(ps))

                else:  # the overlap is of one or two years

                    # isolate the overlap years
                    overlap_years = {yr: wrk_plcs for yr, wrk_plcs in years_and_workplaces.items()
                                     if len(wrk_plcs) > 1}

                    # if the overlap is in the middle of the person-sequence
                    if min(overlap_years) > min(years_and_workplaces) \
                            and max(overlap_years) < max(years_and_workplaces):

                        # CASES (A) AND (B)
                        # if the overlap marks a transition
                        transition = if_transition(years_and_workplaces, overlap_years)
                        if transition:
                            # mark for removal the rows which match the receiving/destination workplace
                            # keeping the sending workplace is arbitrary, it only matters that the
                            # choice be applied consistently
                            for ovrlp_yr in overlap_years:
                                to_remove.add(str(ovrlp_yr) + '-' + transition['workplace_after'])

                        # CASE (H)
                        # no transition, a blip in an otherwise continuous workplace sequence
                        # throw out the blip
                        else:
                            [to_remove.add(str(yr) + '-' + str(wrk_plc)) for yr, wrk_plc in overlap_years
                             if wrk_plc != transition['workplace_before']]

                    else:  # the overlap is at one or both boundaries

                        # CASES (E)  OR (H)
                        # if overlap is on both boundaries
                        if min(overlap_years) == min(years_and_workplaces) \
                                and max(overlap_years) == max(years_and_workplaces):
                            # mark for removal the workplace in the first row
                            # this choice is arbitrary, it only matters that it be applied consistently
                            first_workplace = ps[0][3]
                            to_remove.add([str(yr) + '-' + first_workplace for yr in overlap_years])

                        # CASES (C) OR (H)
                        # if the overlap is only on the lower boundary,
                        elif min(overlap_years) == min(years_and_workplaces) \
                                and max(overlap_years) < max(years_and_workplaces):

                            # throw out the workplace that we transition FROM; this eliminates one mobility event

                            # get the sending year-workplace
                            sorted_years = sorted(list(overlap_years))
                            first_overlap_year = sorted_years[0]
                            first_overlap_year_idx = sorted_years.index(first_overlap_year)
                            year_before = sorted_years[first_overlap_year_idx - 1]
                            sending_workplace = years_and_workplaces[year_before]

                            # and mark for removal the years with the sending workplace
                            [to_remove.add(str(yr) + '-' + str(wrk_plc)) for yr, wrk_plc in overlap_years
                             if wrk_plc == sending_workplace]

                        # CASES (D) OR (H)
                        # if the overlap is only on the upper boundary
                        elif max(overlap_years) == max(years_and_workplaces) \
                                and min(overlap_years) > min(years_and_workplaces):

                            # throw out the workplace we transition TO; this eliminates one mobility event

                            # get the destination year-workplace
                            sorted_years = sorted(list(overlap_years))
                            last_overlap_year = sorted_years[-1]
                            last_overlap_year_idx = sorted_years.index(last_overlap_year)
                            first_year_after = sorted_years[last_overlap_year_idx + 1]
                            destination_workplace = years_and_workplaces[first_year_after]

                            # and mark for removal the years with the destination workplace
                            [to_remove.add(str(yr) + '-' + str(wrk_plc)) for yr, wrk_plc in overlap_years
                             if wrk_plc == destination_workplace]

                        else:
                            # the person-sequence has slipped through the filters, save for visual inspection
                            odd_person_sequences.append(ps)

            # now apply the removal orders to the person sequences, to remove the overlaps

            # the new person-sequence, without overlaps
            new_ps = []
            for pers_yr in ps:
                if str(pers_yr[4]) + '-' + pers_yr[3] not in to_remove:  # the year-workplace combination
                    new_ps.append(pers_yr)

            # and add the new person-sequence to the list of distinct persons
            distinct_persons.append(new_ps)

            # keep track of the changes, so we can inspect visually and make sure it's behaving correctly

            ps.sort(key=operator.itemgetter(1, 2, 5)), new_ps.sort(key=operator.itemgetter(1, 2, 5))

            # we want a double-column csv file:
            # old person-sequence in first column, no-overlap sequence in second column
            for idx, pers_yr in enumerate(ps):
                if idx < len(new_ps) - 1:
                    change_log.append(pers_yr[1:3] + pers_yr[4:6] + ['', ''] + new_ps[idx][1:3] + new_ps[idx][4:6])
                else:
                    change_log.append(pers_yr[1:3] + pers_yr[4:6])
            change_log.append(['\n'])

        else:  # add all the person-year sequences with no overlap years as they are to the list of distinct persons
            distinct_persons.append(ps)

    # write to disk the tables of odd sequences and the change logs
    output_root_path = 'prep/pids/' + profession + '/' + profession

    odd_seqs = pd.DataFrame(odd_person_sequences)
    odd_seqs.to_csv(output_root_path + '_odd_person_sequences.csv')

    change_log = pd.DataFrame(change_log)
    change_log.to_csv(output_root_path + '_change_log.csv')

    # and return the list of distinct persons
    return distinct_persons

    # TODO need to write a test file for this...actually, already have one from before, somewhere...


def if_transition(years_and_workplaces, overlap_years):
    """
    Function that returns True if the overlap years marked a transition between workplaces, and False if it did not.

    NB: only built to handle one or two years of overlap

    :param years_and_workplaces: a dict of form {Year1: [workplace 1], Year2: [workplace1], Year3:[workplace2]}
    :param overlap_years: dict of key-value pairs of years_and_workplaces that have more than one workplace per year
                          e.g. {Year3: [workplace 3, workplace4]}
    :return: dict if a transition, None otherwise
    """

    years = sorted(list(years_and_workplaces))

    year_before, year_after = None, None

    # if there's only one year of overlap
    if len(overlap_years) == 1:
        ovrlp_yr_idx = years.index(list(overlap_years[0]))
        year_before, year_after = years[ovrlp_yr_idx - 1], years[ovrlp_yr_idx + 1]

    # if there are two years of overlap
    if len(overlap_years) == 2:
        ovrlap_yrs = sorted(list(overlap_years))
        lower_ovrlp_yr, upper_ovrlp_yr = ovrlap_yrs[0], ovrlap_yrs[1]
        lower_ovrlp_yr_idx, upper_ovrlp_yr_idx = years.index(lower_ovrlp_yr), years.index(upper_ovrlp_yr)
        year_before, year_after = years[lower_ovrlp_yr_idx - 1], years[upper_ovrlp_yr_idx + 1]

    # if the workplaces in the years before and after the overlap are different, we have a transition
    if years_and_workplaces[year_before] != years_and_workplaces[year_after]:
        # return a dict with keys: year before, year after, workplace before, workplace after
        return {'year_before': str(year_before), 'year_after': str(year_after),
                'workplace_before': years_and_workplaces[year_before],
                'workplace_after': years_and_workplaces[year_after]}
    else:  # if the before and after workplaces are the same, there's no transition
        return None


def split_sequences(person_sequence):
    """

    NB: BUILT ONLY FOR SEQUENCES THAT FEATURE ONLY ONE NAME IN 2 PLACES, WILL NOT WORK FOR ONE NAME IN 3+ PLACES

    Takes a year-sorted sequence of person years that share a full name which is in two places at once,
    and return two sequences, one for each place.

    I assume (heuristically) that distinct career sequences develop in the same Appellate Court area;
    elif they're in the same appellate area, then in the same Tribunal Area;
    elif they're in the same Tribunal Area, then in different Local Courts

    So, for example, the function should take this sequence with overlaps (CA == court area)

    (A)

    SURNAME    GIVEN NAME   INSTITUTION   YEAR  CA

    DERP       BOB JOE     ALPHA          2012  1
    DERP       BOB JOE     BETA           2012  2
    DERP       BOB JOE     ALPHA          2013  1
    DERP       BOB JOE     BETA           2013  2
    DERP       BOB JOE     ALPHA          2014  1
    DERP       BOB JOE     BETA           2014  2


    and return these two sequences

    (B)                                                     (C)

    SURNAME    GIVEN NAME   INSTITUTION   YEAR  CA          SURNAME    GIVEN NAME  INSTITUTION     YEAR  CA

    DERP       BOB JOE     ALPHA          2012  1           DERP        BOB JOE     BETA           2012  2
    DERP       BOB JOE     ALPHA          2013  1           DERP        BOB JOE     BETA           2013  2
    DERP       BOB JOE     ALPHA          2014  1           DERP        BOB JOE     BETA           2014  2


    :param person_sequence: a year-ordered sequence of person-years sharing a full name; as a list of lists
    :return: a list of person-sequences; in the example above, a list with [B, C]
    """

    # group by appellate area
    # value at index 6 holds appellate court area code
    p_seqs = [group for k, [*group] in itertools.groupby(person_sequence, key=operator.itemgetter(6))]

    # if you don't get two groups, group by tribunal area
    # value at index 7 holds tribunal area code
    if len(p_seqs) != 2:
        p_seqs = [group for k, [*group] in itertools.groupby(person_sequence, key=operator.itemgetter(7))]

    # if you don't get two groups, group by local court
    # value at index 8 holds local court code
    if len(p_seqs) != 2:
        p_seqs = [group for k, [*group] in itertools.groupby(person_sequence, key=operator.itemgetter(8))]

    # if you still don't get two groups, error out, something's wrong
    if len(p_seqs) != 2:
        raise ValueError("CAN'T SPLIT SEQUENCE INTO GROUPS, SOMETHING WRONG WITH INPUT SEQUENCE")

    # otherwise, return the groups
    else:
        return p_seqs


def interpolate_person_years(distinct_persons):
    """
    Sometimes otherwise continuous sequences are missing a year or two in the middle. It is unreasonable that
    someone actually retired from a judicial profession for such a short period, so we assume that an absence of two
    years or less reflects a book-keeping error, and interpolate the missing person-years.
    :param distinct_persons: a list of distinct persons, i.e. of person-sequences that feature no overlaps; this is
                             a triple nested list: of person-sequences, which is made up of person-years, each of
                             which is a list of person-year data
    :return: a list of distinct persons with interpolated person-years
    """
    pass


def unique_person_ids(distinct_persons):
    """
    Assign each person-year a new field with the person-ID to which the person-year belongs.
    :param distinct_persons: a list of distinct persons, i.e. of person-sequences that feature no overlaps; this is
                             a triple nested list: of person-sequences, which is made up of person-years, each of
                             which is a list of person-year data
    :return: a list of distinct persons, where each person-year has the person-level ID
    """
    pass


def cluster(profession):
    """
    Use the dedupe package to assign rows in a person-year table to a cluster: that cluster than gets a unique ID.
    NB: this code adapted from the example code at https://dedupeio.github.io/dedupe-examples/docs/csv_example.html

    :param profession: string, "judges", "prosecutors", "notaries" or "executori".
    :return:
    """

    input_file = 'prep/standardise/' + profession + '/' + profession + '_preprocessed.csv'
    output_file = 'prep/pids/' + profession + '/' + profession + '_pids.csv'
    # settings_file is a binary file, contains weights and predicates
    settings_file = 'prep/pids/' + profession + '/' + profession + '_learned_settings'
    training_file = 'prep/pids/' + profession + '/' + profession + '_training.json'

    # load the csv as a dict of dicts, each sub-dict is a person-year
    py_dict = {}
    with open(input_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            ascii_row = [(k, unidecode(v)) for (k, v) in row.items()]  # dedupe likes everything in ASCII
            row_id = int(row['cod rând'])
            py_dict[row_id] = dict(ascii_row)

    # if the setting file exists from previous runs, use that and skip training and learning
    if os.path.exists(settings_file):
        print('reading from', settings_file)
        with open(settings_file, 'rb') as f:
            deduper = dedupe.StaticDedupe(f)

    else:

        # field you want the deduper to take into consideration
        fields = [
            {'field': 'nume', 'type': 'String'},
            {'field': 'prenume', 'type': 'String'},
            {'field': 'sex', 'type': 'String'},
            {'field': 'instituţie', 'type': 'String'},
            {'field': 'an', 'type': 'String'},
            {'field': 'sex', 'type': 'String'},
        ]

        deduper = dedupe.Dedupe(fields)

        # if a training file from previous already exists, use that and skip training
        if os.path.exists(training_file):
            print('reading labeled examples from ', training_file)
            with open(training_file, 'rb') as f:
                deduper.prepare_training(py_dict, f)
        else:
            deduper.prepare_training(py_dict)

        print('starting active labeling...')

        dedupe.console_label(deduper)

        deduper.train()

        # save the training data and settings to disk
        with open(training_file, 'w') as tf:
            deduper.write_training(tf)

        with open(settings_file, 'wb') as sf:
            deduper.write_settings(sf)

    print('clustering...')
    clustered_dupes = deduper.partition(py_dict, 0.5)

    # show how many clusters of (de)duplicate rows the deduper generated
    print('# duplicate sets', len(clustered_dupes))

    # associate the cluster ids with the person-year entries
    cluster_membership = {}
    for cluster_id, (records, scores) in enumerate(clustered_dupes):
        for record_id, score in zip(records, scores):
            cluster_membership[record_id] = {
                "cod personal": cluster_id,
                "confidence_score": score
            }

    # update the input file with cluster IDs and the confidence score of that cluster association
    with open(output_file, 'w') as f_output, open(input_file) as f_input:

        reader = csv.DictReader(f_input)
        fieldnames = ['cod personal', 'confidence_score'] + reader.fieldnames

        writer = csv.DictWriter(f_output, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            row_id = int(row['cod rând'])
            row.update(cluster_membership[row_id])
            writer.writerow(row)

# remove the edge years -- too much of this signal is censoring noise, would rather keep something I know
# is bad than assume/hope/pretend it'll turn out good
# ps = [py for py in pers_seq if py[4] != censor_years[0] and py[4] != censor_years[1]]  # py[4] = year
