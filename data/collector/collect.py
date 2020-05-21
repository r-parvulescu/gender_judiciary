"""
Collects data from different format files into a table.
"""

import os
import csv
from collector.converter.triage import triage, get_doc_data


def make_table(root_directory, to_csv, parquet=False):
    """
    Go through doc files, extract data and put it all into a csv file.
    :return: None
    """
    print(parquet)
    out_path = 'collector/prosecutors.csv' if parquet else 'collector/judges.csv'
    person_period_table = []
    counter = 0
    for subdir, dirs, files in os.walk(root_directory):
        for file in files:
            counter += 1
            if counter < 10000:
                file_path = subdir + os.sep + file
                print(file_path)
                cleaner_text, year, month = triage(file_path, parquet)
                if cleaner_text:
                    people_periods = get_doc_data(cleaner_text, year, month, prosecs=parquet)
                    for pp in people_periods:
                        person_period_table.append(pp)
    if to_csv:
        head = ["nume", "prenume", "instanță/parchet", "an", "lună"]
        with open(out_path, 'w') as outfile:
            writer = csv.writer(outfile, delimiter=',')
            writer.writerow(head)
            for row in person_period_table:
                writer.writerow(row)
    return person_period_table


def collect_data(to_csv, zipped=False, prosecs=False):
    """collect data from .doc files, (maybe) spit out a csv and return a table as a list of lists"""
    if zipped:
        in_path = 'collector/converter/input/prosecutors_12.2005_12.2019.zip' if prosecs \
            else 'collector/converter/input/judges_12.2005_04.2020.zip'
    else:
        in_path = 'collector/converter/input/prosecutors_12.2005_12.2019' if prosecs \
            else 'collector/converter/input/judges_12.2005_04.2020'
    return make_table(in_path, to_csv, parquet=prosecs)
