"""
Assign each person-year a unique, person-level ID.
"""

import os
import csv
import dedupe
from unidecode import unidecode


def cluster(profession):
    """
    Use the dedupe package to assign rows in a person-year table to a cluster: that cluster than gets a unique ID.
    NB: this code adapted from the example code at https://dedupeio.github.io/dedupe-examples/docs/csv_example.html

    :param profession: string, "judges", "prosecutors", "notaries" or "executori".
    :return:
    """

    input_file = 'prep/standardise/' + profession + '/' + profession + '_preprocessed.csv'
    output_file = 'prep/pids/' + profession + '/' + profession + '_dedupe_clusters.csv'
    # settings_file is a binary file, contains weights and predicates
    settings_file = 'prep/pids/' + profession + '/' + profession + '_learned_settings'
    training_file = 'prep/pids/' + profession + '/' + profession + '_training.json'

    # load the csv as a dict of dicts, each sub-dict is a person-year
    py_dict = {}
    with open(input_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            ascii_row = [(k, unidecode(v)) for (k, v) in row.items()]  # dedupe likes everything in ASCII
            row_id = int(row['cnp'])
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
            {'field': 'instituție', 'type': 'String'},
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
                "Cluster ID": cluster_id,
                "confidence_score": score
            }

    # update the input file with cluster IDs and the confidence score of that cluster association
    with open(output_file, 'w') as f_output, open(input_file) as f_input:

        reader = csv.DictReader(f_input)
        fieldnames = ['Cluster ID', 'confidence_score'] + reader.fieldnames

        writer = csv.DictWriter(f_output, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            row_id = int(row['cnp'])
            row.update(cluster_membership[row_id])
            writer.writerow(row)
