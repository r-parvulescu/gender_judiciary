"""
Assign each person-year a unique, person-level ID.
"""

import operator
import itertools
import os
import csv
import dedupe
from unidecode import unidecode


def two_in_one_place(person_year_table):
    """
    NB: !! this code only applies to person-year tables !! DO NOT APPLY TO PERSON MONTH TABLES

    NB: !! only do this for complete data, i.e. 2005 and later !!! WILL BE TOO GLITCHY ON INCOMPLETE DATA

    Sometimes we notice that a person is in two or more places at the same time. This can mean that

    a) two or more people share a name

    b) there's a book-keeping error: a common reason is that someone is added to the books of the new workplace
    BEFORE they've been take off the rolls of the old workplace.

    One way to distinguish between the two scenarios is to look first at the length of double-counting, and second
    at the context of the overlap.

    i) if a person is in two or more places for more than two years, it's likely to indicate that people share a name.
       Two years might seem a lot, but the mistake only needs to get made for two calendar months (Dec and Jan), and
       for us to have gotten particularly unlucky with month sampling, and the issue will show up across two years.

    ii) if the overlap is one or two years, and is located at the transition between workplaces, it's probably a
        book-keeping mistake. Examples of (ii) would be

    (A)                                                     (B)

    SURNAME    GIVEN NAME   INSTITUTION   YEAR               SURNAME    GIVEN NAME  INSTITUTION    YEAR

    DERP       BOB JOE      ALPHA         2012               DERP       BOB JOE     ALPHA          2012
    DERP       BOB JOE      ALPHA         2013               DERP       BOB JOE     ALPHA          2013
    DERP       BOB JOE      BETA          2013               DERP       BOB JOE     BETA           2013
    DERP       BOB JOE      BETA          2014               DERP       BOB JOE     ALPHA          2014
    DERP       BOB JOE      BETA          2015               DERP       BOB JOE     BETA           2014
    DERP       BOB JOE      BETA          2016               DERP       BOB JOE     BETA           2015

    Note that for (ii) to hold we need to observe a sending and receiving workplace. Cases (C), (D), and (E) below
    would NOT fall under the ambit of case (ii), because we can't observe both sending and receiving workplaces.

    (C)                                                     (D)

    SURNAME    GIVEN NAME   INSTITUTION   YEAR               SURNAME    GIVEN NAME  INSTITUTION    YEAR

    DERP       BOB JOE      ALPHA         2012               DERP       BOB JOE     BETA           2012
    DERP       BOB JOE      BETA          2012               DERP       BOB JOE     BETA           2013
    DERP       BOB JOE      BETA          2013               DERP       BOB JOE     BETA           2014
    DERP       BOB JOE      BETA          2014               DERP       BOB JOE     BETA           2015
    DERP       BOB JOE      BETA          2015               DERP       BOB JOE     ALPHA          2015

    (E)                                                     (F)

    SURNAME    GIVEN NAME   INSTITUTION   YEAR              SURNAME    GIVEN NAME  INSTITUTION     YEAR

    DERP       BOB JOE     ALPHA          03/2012           DERP        BOB JOE     ALPHA           03/2012
    DERP       BOB JOE     BETA           03/2012           DERP        BOB JOE     ALPHA           04/2012
    DERP       BOB JOE     ALPHA          04/2013           DERP        BOB JOE     BETA            04/2012
    DERP       BOB JOE     BETA           04/2013           DERP        BOB JOE     GAMMA           04/2012
    DERP       BOB JOE     ALPHA          05/2014           DERP        BOB JOE     BETA            05/2012
    DERP       BOB JOE     BETA           05/2015

    Note that in (F) one person is in three places at once. This is simply a straigth extension of cases (A) and (B).

    This function handles such overlaps by either throwing out transition rows (as per situation B) or splits sequences
    apart, giving each one a different, unique, person-level ID (as per situation A).

    NB: the approach is to throw out data that might indicate mobility, to get conservative estimates of mobility

    :param person_year_table: a table of person-years, as a list of lists
    :return: a person-year table, as a list of lists, with unique, person-level IDs in the second column.
    """

    # sort the data by surname and given name, then group data by surname and given name
    person_year_table.sort(key=operator.itemgetter(1, 2, 4))  # surname = row[1], given name = row[2], year = row[4]

    # keep groups if they feature one or more rows with the same year value
    person_sequences = [group for k, [*group] in itertools.groupby(person_year_table, key=operator.itemgetter(1, 2))]

    # initialise table of odd person-sequence exceptions to inspect manually later
    odd_person_sequences = []

    for ps in person_sequences:

        # initialise a dict of years available and the workplaces associated with each year
        years_and_workplaces = {row[4]: [] for row in ps}  # again, row[4] =  year

        # there's overlap when there are fewer years than rows
        if len(years_and_workplaces) < len(ps):

            # associate workplaces with years
            [years_and_workplaces[row[4]].append(row[3]) for row in ps]  # row[3] = workplaces

            # if one year features three or more institutions, save the person-sequence in a separate file,
            # need to inspect it manually
            if max([len(v) for v in years_and_workplaces.values()]) > 2:
                odd_person_sequences.extend(ps)

            # no year features more than two institutions, and the overlap is of three or more years,
            # split up the rows into different IDs to remove the overlap
            else:

                # if the overlap is of 3+ years, split up the rows into different IDs to remove the overlap
                # NB: there can't be overlap of more than two institutions, that's been handled above already
                if len(ps) - len(years_and_workplaces) > 2:
                    pass

                else:  # the overlap is of one or two years
                    # isolate the overlap years
                    overlap_years = {yr: wps for yr, wps in years_and_workplaces.items() if len(wps) > 1}

                    # if the overlap is in the middle
                    if max(overlap_years) < max(years_and_workplaces) \
                            and min(overlap_years) < min(years_and_workplaces):
                        # only keep the rows which resemble the departure institution
                        # this choice is arbitrary, it only matters that it be applied consistently
                        pass
                    else:  # the overlap is at one or both boundaries
                        # if the overlap is on the lower boundary,
                        if min(overlap_years) == min(years_and_workplaces):
                            # only keep the workplaces that we transition TO
                            pass
                        # if the overlap is on the upper boundary
                        elif max(overlap_years) == max(years_and_workplaces):
                            # only keep the workplaces we transition FROM
                            pass
                        elif min(overlap_years) == min(years_and_workplaces) \
                                and max(overlap_years) == max(years_and_workplaces):  # if overlap covers the whole time
                            # keep the workplace of the first row
                            # this choice is arbitrary, it only matters that it be applied consistently
                            pass

        # TODO need to write a test file for this...actually, already have one, somewhere...


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
