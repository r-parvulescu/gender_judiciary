"""
Functions for making/updating court and gender dicts, and handling surnames misattributed as given names.
"""

import json
import csv


def assign_court_codes(units_hierarchical, units_codes, parquet=False):
    """take a hierarchical dict of units and return a dict with court names and codes"""
    units = {}
    with open(units_hierarchical) as ch:
        data = json.load(ch)
        for ca_k, ca_v in data.items():
            apellate = ca_k[22] if parquet else ca_k[0]
            if apellate == "C":
                ca_code = data[ca_k][0]
                units[ca_k] = [ca_code, '-88', '-88']
                for trib_k, trib_v in data[ca_k][1].items():
                    trib_code = data[ca_k][1][trib_k][0]
                    units[trib_k] = [ca_code, trib_code, '-88']
                    if ("COMERC" not in trib_k) and ("MINORI" not in trib_k):
                        for jud_k, jud_v in data[ca_k][1][trib_k][1].items():
                            jud_code = (data[ca_k][1][trib_k][1][jud_k])
                            units[jud_k] = [ca_code, trib_code, jud_code]
                else:
                    if parquet:
                        units["PARCHETUL DE PE LÂNGĂ ÎNALTA CURTE DE CASAŢIE ŞI JUSTIŢIE"] = ['-88', '-88', '-88']
                        units["DIRECŢIA DE INVESTIGARE A INFRACŢIUNILOR DE CRIMINALITATE ORGANIZATĂ ŞI TERORISM"] = \
                            ["DIICOT", '-88', '-88']
                        units["DIRECŢIA NAŢIONALĂ ANTICORUPŢIE"] = ['DNA', '-88', '-88']
                    else:
                        units["ÎNALTA CURTE DE CASAŢIE ŞI JUSTIŢIE"] = ['-88', '-88', '-88']
    with open(units_codes, 'w') as json_file:
        json.dump(units, json_file)


def make_gend_dict(csv_file, in_gender_dict, out_gender_dict):
    """updates existing name-gender dict with input from the person-year csv table"""
    with open(in_gender_dict, 'r') as gd, open(csv_file, 'r') as f, open(out_gender_dict, 'w') as outfile:
        gend_dict = json.load(gd)
        counter = 0
        row_count = 0
        # go through files, building gender dict
        reader = csv.reader(f)
        next(reader, None)  # skip head
        for row in reader:
            print(row_count)
            row_count += 1
            given_names = row[1].split(' ')
            for name in given_names:
                if name not in gend_dict:  # prompt to assign name
                    print(name)
                    answer = input("What gender is this name? f,m,dk, surname ")
                    if not ((answer == 'f') or (answer == 'm') or (answer == 'dk') or (answer == 'surname')):
                        answer = input("Incorrect format, please, what gender is this name? f,m,dk ")
                    gend_dict[name] = answer
                    counter += 1
        # dump the dict
        json.dump(gend_dict, outfile)


def surname_correction(csv_infile, gender_dict):
    """handle given names that incorrectly contain surnames"""
    with open(csv_infile, 'r') as infile, open(csv_infile[:-4] + "_surname_corrected.csv", 'w') as outfile, \
            open(gender_dict, 'r') as gd:
        reader = csv.reader(infile)
        next(reader, None)  # skip headers

        writer = csv.writer(outfile)
        new_headers = ["nume", "prenume", "sex", "instanță/parchet", "an", "lună", "CA cod", "trib cod", "jud cod"]
        writer.writerow(new_headers)

        gender_dict = json.load(gd)

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
                    writer.writerow(new_row)
                # surname is at end, correct row
                # e.g. 'CORNOIU', 'VICTOR JITĂRAŞU'
                elif misplaced_surname[-3:] == row[1][-3:]:
                    surname = row[0] + ' ' + row[1].split()[-1]
                    given_name = row[1].replace(misplaced_surname, '').strip()
                    new_row = [surname, given_name] + row[2:]
                    writer.writerow(new_row)
                # two names banged together, correct old row, make new row
                else:
                    start_name = row[1].find(misplaced_surname)
                    other_person = row[1][start_name:].strip().split(' ')
                    surname = other_person[0]
                    given_name = other_person[1]
                    new_row = [surname, given_name] + row[2:]
                    old_row = [row[0]] + [row[1].replace(row[1][start_name:], '').strip()] + row[2:]
                    writer.writerow(old_row)
                    writer.writerow(new_row)
            else:
                writer.writerow(row)


if __name__ == '__main__':
    judges_infile = 'tables/judges/judges.csv'
    prosec_infile = 'tables/prosecutors/prosecutors.csv'
    in_gend_dict = "dicts/ro_gender_dict.txt"
    out_gend_dict = "dicts/ro_gender_dict_updated.txt"

    c_hierarchical = "dicts/courts_hierarchical.txt"
    p_hierarchical = "dicts/parquets_hierarchical.txt"
    c_codes = "dicts/court_codes.txt"
    p_codes = "dicts/parquet_codes.txt"

    # assign_court_codes(c_hierarchical, c_codes)
    # assign_court_codes(p_hierarchical, p_codes, parquet=True)
    # make_gend_dict(judges_infile, in_gend_dict, out_gend_dict)
    # surname_correction(judges_infile, in_gend_dict)
