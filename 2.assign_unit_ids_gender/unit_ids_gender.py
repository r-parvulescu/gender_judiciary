"""
Code for assigning each court a unique ID and marking its location in the judicial hierarchy.
Additionally, assigns a gender (including "dk" for don't know) to each person-month.
infile headers: [nume, prenume, instanță/parchet, an, lună]
"""

import csv
import json


def add_columns(infile, outfile, gender_dict, unit_codes):
    with open(infile, 'r') as in_file, open(outfile, 'w') as out_file, open(gender_dict, 'r') as gd, \
            open(unit_codes) as uc:
        gender_dict = json.load(gd)
        court_codes_dict = json.load(uc)

        writer = csv.writer(out_file)
        new_headers = ["nume", "prenume", "sex", "instanță/parchet", "an", "lună", "CA cod", "trib cod", "jud cod"]
        writer.writerow(new_headers)

        reader = csv.reader(in_file)
        next(reader, None)  # skip headers
        row_count = 0
        confused_names_resolved = {}
        for row in reader:
            row = list(filter(None, row))
            row_count += 1
            court_name = row[2]
            court_codes = court_codes_dict[court_name.strip()]
            person_gender = get_gender(row[1], gender_dict, row, confused_names_resolved)
            new_row = row[:2] + [person_gender] + row[2:] + court_codes
            writer.writerow(new_row)


def get_gender(given_names, gender_dict, row, confused_names_resolved):
    """assign gender to each person-period"""
    person_gender = []
    given_names = given_names.split(' ')
    for name in given_names:
        if name not in gender_dict:
            print(row)  # show problem
            return ''
        else:
            if gender_dict[name] != "surname":
                person_gender.append(gender_dict[name])
    # if more than one given name, go with majority vote
    if not (person_gender[1:] == person_gender[:-1]):
        # if name genders don't match
        if ('f' in person_gender) and ('m' in person_gender):
            if ' '.join(given_names) in confused_names_resolved.keys():
                person_gender = confused_names_resolved[' '.join(given_names)]
            else:
                print(row)
                answer = input("Gender contradiction, resolve please: f,m,dk ")
                if not ((answer == 'f') or (answer == 'm') or (answer == 'dk')):
                    answer = input(
                        "Incorrect format, please, what gender is this name? f,m,dk ")
                person_gender = answer
                confused_names_resolved[' '.join(given_names)] = person_gender
        else:  # if a clear label and a "don't know", opt for clear label
            if 'f' in person_gender:
                person_gender = 'f'
            elif 'm' in person_gender:
                person_gender = 'm'
    else:
        if person_gender:
            person_gender = person_gender[0]
    return person_gender


if __name__ == '__main__':
    gend_dict = "dicts/ro_gender_dict.txt"
    c_codes = "dicts/court_codes.txt"
    p_codes = "dicts/parquet_codes.txt"
    judges_infile = 'tables/judges/judges_surname_corrected.csv'
    prosec_infile = 'tables/prosecutors/prosecutors_surname_corrected.csv'
    judges_outfile = 'tables/judges/judges_unit_gender.csv'
    prosec_outfile = 'tables/prosecutors/prosecutors_unit_gender.csv'

    # add_columns(judges_infile, judges_outfile, gend_dict, c_codes)
    add_columns(prosec_infile, prosec_outfile, gend_dict, p_codes)
