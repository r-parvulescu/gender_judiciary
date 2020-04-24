"""
Code for assigning each court a unique ID and marking its location in the judicial hierarchy.
Additionally, assigns a gender (including "dk" for don't know) to each person-month.
infile headers: [nume, prenume, instanță/parchet, an, lună]
"""

import csv
import json
from augmenter.units import unitdict_helpers
from augmenter.pids import transdict_tools
from augmenter.gender import gender_helpers
from augmenter.pids import give_pid


def augment_data(to_csv, prosecs=False):
    """augment the existing data table"""
    in_path = 'collector/prosecutors.csv' if prosecs else 'collector/judges.csv'
    augmented_data = add_columns(in_path, to_csv, parquet=True) if prosecs \
        else add_columns(in_path, to_csv, parquet=False)
    if to_csv:
        outfile = 'augmenter/prosecutors_ids.csv' if prosecs else 'augmenter/judges_ids.csv'
        with open(outfile, 'w') as out_file:
            writer = csv.writer(out_file)
            new_headers = ["cnp", "nume", "prenume", "sex", "instanță/parchet", "an", "lună",
                           "ca cod", "trib cod", "jud cod", 'nivel']
            writer.writerow(new_headers)
            for row in augmented_data:
                writer.writerow(row)
    return augmented_data


def add_columns(in_path, to_csv, parquet=False):
    """adds columns (gender, unique person id, etc.) to the basic person-period table"""
    # load up the dictionaries
    unit_codes = 'augmenter/units/parquet_codes.txt' if parquet else 'augmenter/units/court_codes.txt'
    with open(unit_codes, 'r') as ucd, open('augmenter/gender/ro_gender_dict.txt', 'r') as gd:
        unit_codes_dict = json.load(ucd)
        gender_dict = json.load(gd)
    with open('augmenter/pids/transdicts/fullnames.txt', 'r') as fn_td, \
            open('augmenter/pids/transdicts/given_names.txt', 'r') as gn_td, \
            open('augmenter/pids/transdicts/surnames.txt', 'r') as sn_td:
        tds = [json.load(fn_td), json.load(gn_td), json.load(sn_td)]
    # correct for misplaced surnames
    sn_corrected = surname_correction(in_path)
    # deduplicate names, add columns for person gender and for unit codes
    with_dedup_gend_unit = []
    confused_names_resolved = {}
    for row in sn_corrected:
        row = list(filter(None, row))
        row = transdict_tools.deduplicate_names(row, tds)  # update row with deduplicated name
        unit_code_and_level = unitdict_helpers.set_unitcode_level(row[2], unit_codes_dict)  # unit name = row[2]
        gender = gender_helpers.get_gender(row[1], row, confused_names_resolved, gender_dict)
        new_row = row[:2] + [gender] + row[2:] + unit_code_and_level
        with_dedup_gend_unit.append(new_row)
    with_pids = give_pid.set_unique_pid(with_dedup_gend_unit)  # set unique person ids
    return with_pids


def surname_correction(in_path):
    """
    handle given names that incorrectly contain surnames;
    works at table level since we sometimes correct multiple rows at once
    """
    corrected_data_table = []
    with open('augmenter/gender/ro_gender_dict.txt') as gd, open(in_path, 'r') as in_file:
        gender_dict = json.load(gd)
        reader = csv.reader(in_file)
        next(reader)  # skip header
        for row in reader:
            names = list(filter(None, row[1].split(' ')))
            misplaced_surname = ''
            for name in names:
                if gender_dict[name] == 'surname':
                    misplaced_surname = misplaced_surname + name
            if misplaced_surname:
                # surname is at beginning, correct row
                # e.g. ŞESTACOVSCHI	MOANGĂ SIMONA
                if misplaced_surname[:3] == row[1][:3]:
                    surname = row[0] + ' ' + misplaced_surname
                    given_name = row[1].replace(misplaced_surname, '').strip()
                    new_row = [surname, given_name] + row[2:]
                    corrected_data_table.append(new_row)
                # surname is at end, correct row
                # e.g. 'CORNOIU', 'VICTOR JITĂRAŞU'
                elif misplaced_surname[-3:] == row[1][-3:]:
                    surname = row[0] + ' ' + row[1].split()[-1]
                    given_name = row[1].replace(misplaced_surname, '').strip()
                    new_row = [surname, given_name] + row[2:]
                    corrected_data_table.append(new_row)
                # maiden name got tacked at the end of given names, append to surnames
                # e.g. 'MUNTEANU RETEVOESCU', 'ANA MARIA (DUMBRAVĂ)'
                elif misplaced_surname[0] == '(':
                    surname = row[0] + misplaced_surname
                    given_name = row[1].replace(misplaced_surname, '').strip()
                    new_row = [surname, given_name] + row[2:]
                    corrected_data_table.append(new_row)
                # two names banged together, correct old row, make new row
                else:
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
