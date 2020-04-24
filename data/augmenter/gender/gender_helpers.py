"""
Makes and updates the name : gender dictionary.
"""

import json
import csv


def get_gender(given_names, row, confusing_names_resolved, gender_dict):
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
            if ' '.join(given_names) in confusing_names_resolved.keys():
                person_gender = confusing_names_resolved[' '.join(given_names)]
            else:
                print(row)
                answer = input("Gender contradiction, resolve please: f,m,dk ")
                if not ((answer == 'f') or (answer == 'm') or (answer == 'dk')):
                    answer = input(
                        "Incorrect format, please, what gender is this name? f,m,dk ")
                person_gender = answer
                confusing_names_resolved[' '.join(given_names)] = person_gender
        else:  # if a clear label and a "don't know", opt for clear label
            if 'f' in person_gender:
                person_gender = 'f'
            elif 'm' in person_gender:
                person_gender = 'm'
    else:
        if person_gender:
            person_gender = person_gender[0]
    return person_gender


def make_gender_dict(csv_file):
    """updates existing name-gender dict with input from the person-year csv table"""
    with open(csv_file, 'r') as f, open('augmenter/gender/ro_gender_dict.txt', 'r') as in_gd, \
            open('augmenter/gender/ro_gender_dict_updated.txt', 'w') as out_gd:
        gender_dict = json.load(in_gd)
        # go through files, building gender dict
        reader = csv.reader(f)
        next(reader, None)  # skip head
        for row in reader:
            given_names = row[1].split(' ')
            for name in given_names:
                if name not in gender_dict:  # prompt to assign name
                    print(row[0], row[1])
                    print(name)
                    answer = input("What gender is this name? f,m,dk, surname ")
                    if not ((answer == 'f') or (answer == 'm') or (answer == 'dk') or (answer == 'surname')):
                        answer = input("Incorrect format, please, what gender is this name? f,m,dk ")
                    gender_dict[name] = answer
        # dump the dict
        json.dump(gender_dict, out_gd)
