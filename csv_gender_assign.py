# csv_gender_assign.py
# script for taking turning the doc files from freedom of information requests from the RO judiciary
# into a standardised csv format, which includes associating each name with a gender
# also, creates a RO dictionary of gendered names

import os, json, csv, re, string, textract
from collections import deque


def standardise_path(path):
    """
    standardise all the paths to "root/magistrati/YYYY/MM/court_DD.MM.YYYY.doc
    :param path: string indicating whether we're looking the judge or prosecutor data directory
    :return: none
    """

    root = "/home/radu/insync/docs/CornellYears/6.SixthYear/currently_working/gender_judiciary/data/magistrati/"
    directory = root + path

    for subdir, dirs, files in os.walk(directory):
        for filename in files:
            new_filename = ''
            subdirectory_path = os.path.relpath(subdir, directory)  # get the path to your subdirectory
            file_subpath = os.path.join(subdirectory_path, filename)  # get the path to your file
            # what follows is different ways of turning different formats into "court_DD.MM.YYYY.doc"
            # with standardised county names and no diacritics
            if str(filename)[0].isalpha():  #
                for i in file_subpath.split('/'):
                    if str(i)[0] == '0':
                        if filename[3:7].lower() == 'alba':
                            new_filename = 'ca_albaiulia' + '_' + str(i) + '.doc'
                        elif filename[3:5].lower() == 'tg':
                            new_filename = 'ca_targumures' + '_' + str(i) + '.doc'
                        elif filename[0].lower() == 'î':
                            new_filename = 'iccj' + '_' + str(i) + '.doc'
                        else:
                            new_filename = filename.replace(' ', '_').replace('.doc', '').lower() + '_' + str(
                                i) + '.doc'
            elif str(filename)[0].isdigit():
                date = filename[:10].replace('_', '.')
                if subdirectory_path[8] == "C":
                    new_filename = 'ca_' + subdirectory_path[20:].lower() + '_' + date + '.doc'
                else:
                    new_filename = 'iccj' + '_' + date + '.doc'
            else:
                # give back-up files that start with a '~' zero name length
                pass

            if len(new_filename) > 0:  # skip the back-ups
                new_subpath = root + "judecatori/doc_format_clean" + '/' + new_filename[-8:-4] + '/' + new_filename[
                                                                                                       -11:-9:]
                # make the new directory structure
                if not os.path.exists(new_subpath):
                    os.makedirs(new_subpath)

                # and move the renamed files
                old_filepath = directory + '/' + file_subpath
                new_filepath = os.path.join(new_subpath, new_filename)
                os.rename(old_filepath, new_filepath)


def doc_to_csv(path):
    """
    Convert the doc files with personnel tables from the RO judiciary into person-period csv's with the following
    columns: person-period ID, person ID, last name, other names, year, month, gender, place of court,
    hierarchical court level (e.g. appellate, high court), appellate branch, tribunal branch.
    Then dump that csv in the same directory as it's associated doc
    :param path: a string giving the path for the main directory branch where all the docs are located
    :return: none
    """

    # output csv column headers
    headers = ['surname', 'given name(s)', 'year', 'month', 'gender', 'hierarchical level',
               'base unit', 'appellate unit', 'tribunal unit']
    root = "/home/radu/insync/docs/CornellYears/6.SixthYear/currently_working/gender_judiciary/data/magistrati/"
    directory = root + path

    counter = 0

    # go through each file
    for subdir, dirs, files in os.walk(directory):
        for f in files:
            if str(f)[-3:] == 'doc':  # since putting new .csv files next to .doc, want to avoid catching your tail
                print(f)
                counter += 1
                print(counter)
                if counter > 0:  # useful when debugging to control which files I deal with
                    subdirectory_path = os.path.relpath(subdir, directory)  # get the path to your subdirectory
                    f_subpath_old = os.path.join(subdirectory_path, f)  # get the path to your file
                    full_path_old = directory + '/' + f_subpath_old

                    # get some info from the filename
                    year = str(f)[-8:-4]
                    month = str(f)[-11:-9]

                    text = textract.process(full_path_old).decode('utf-8')  # extract from .doc
                    big_list = []

                    if str(f)[0] == 'i':  # we're dealing with the high court
                        iccj_rows = people_per_unit(text, year, month, 'na', 'na', 1, f)
                        big_list.append(iccj_rows)


                    elif str(f)[0:2] == 'cm':  # we're dealing with the military court of appeals
                        cma_tribunals = deque(text.split('TRIBUNALUL'))  # split by tribunals
                        # first entry is appellate court, above tribunals
                        cma_place_and_lines = get_place_and_clean(cma_tribunals[0])
                        cma_rows = people_per_unit(cma_tribunals[0], year, month, 'na', cma_place_and_lines[0], 2, f)
                        cma_tribunals.pop(0)  # and remove
                        big_list.append(cma_rows)

                        # the lowest court is the military tribunal
                        for t in cma_tribunals:
                            cma_t_rows = people_per_unit(t, year, month, 'na', cma_place_and_lines[0], 3, f)
                            big_list.append(cma_t_rows)


                    else:
                        # all other courts
                        tribunals = deque(text.split('TRIBUNALUL'))  # split by tribunal
                        # first entry is appellate court, above all tribunals
                        apel_place_and_lines = get_place_and_clean(tribunals[0])
                        ca_rows = people_per_unit(tribunals[0], year, month,
                                                  apel_place_and_lines[0].replace('CURTEA DE APEL ', ''), 'na', 2, f)
                        tribunals.pop(0)  # and remove appellate court
                        big_list.append(ca_rows)

                        for t in tribunals:  # second split is by judecatorii/first order courts
                            jud = deque(re.split(r'JUDECĂTORIA|JUDECATORIA', t))
                            # the first entry is the tribunal, above all judecatorii
                            trib_place_and_lines = get_place_and_clean(jud[0])
                            trib_rows = people_per_unit(jud[0], year, month,
                                                        apel_place_and_lines[0].replace('CURTEA DE APEL ', ''),
                                                        trib_place_and_lines[0], 3, f)
                            jud.pop(0)  # and remove
                            big_list.append(trib_rows)

                            for j in jud:  # finally, extract names from first order courts
                                j_rows = people_per_unit(j, year, month,
                                                         apel_place_and_lines[0].replace('CURTEA DE APEL ', ''),
                                                         trib_place_and_lines[0], 4, f)
                                big_list.append(j_rows)

                    big_list = [item for sublist in big_list for item in sublist]  # flatten
                    f_new = str(f)[:-3] + 'csv'  # new .csv filename
                    f_subpath_new = os.path.join(subdirectory_path, f_new)
                    full_path_new = directory + '/' + f_subpath_new

                    with open(full_path_new, 'w') as csvfile:  # set up the csv writer
                        writer = csv.writer(csvfile, delimiter=',')
                        writer.writerow(headers)

                        for r in big_list:
                            writer.writerow(r)

                else:
                    pass


def get_place_and_clean(text):
    """
    Return the court place out of a string of a certain format, and turn the rest of the lines into a list
    :param text: a string of a certain format, can be seen by printing from function doc_to_csm
    :return: a tuple: 1st entry is court place, second entry is list of lines
    """
    cleaner_text = text.replace('|', '').strip().splitlines()  # clean and split by line
    court_place = re.split('din', cleaner_text[0])[0].strip().replace('(', '')  # first entry is court place
    # court_place = cleaner_text[0].split('din')[0].strip().replace('(','')
    cleaner_text.pop(0)  # remove court name
    if re.match(r'[0-9]+', cleaner_text[0]) is not None:  # handle if second line is like '1 DECEMBRIE 2015'
        cleaner_text.pop(0)
    return court_place, cleaner_text


def people_per_unit(text, year, month, apel_unit, trib_unit, level, file_name):
    """
    Make a list of entries that can then be dumped as a csv row. Columns are:last name,
    other names, year, month, gender, place of court, hierarchical court level (e.g. appellate, high court),
    appellate branch, tribunal branch.
    :param text: a string containing information in a certain format
    :param year: year associated with tenure
    :param month: month associated with tenure
    :param apel_unit: appellate jurisdiction
    :param trib_unit: tribunal jurisdiction
    :param level: hierarchical levels; 1 = high court, 2 = appellate, 3 = tribunal, 4 = low court
    :param file_name: file from which all this data is drawn
    :return: a list of rows
    """

    # get the info
    place_and_cleaner_text = get_place_and_clean(text)
    # extract names
    list_of_rows = []
    for i in place_and_cleaner_text[1]:
        names = get_person_names(i)
        if names is not None:
            # catch and handle exceptions
            if len(names) == 1 or (re.match(r'[0-9]+', names[0]) is not None):
                ex = exception_catcher(names, file_name)
                if ex[0] == 1:
                    apel_unit = names[0]
                    continue
                elif ex[0] == 2:
                    names = [ex[1][0], ex[1][1]]
                else:
                    continue

            row = [names[0], names[1], year, month, '', level, place_and_cleaner_text[0], apel_unit, trib_unit]
            list_of_rows.append(row)

    return list_of_rows


def get_person_names(text):
    """
    Extract names from a list, as generated by the doc_to_csv function
    :param text: a string of a certain format, can be seen by printing from function doc_to_csm
    :return: a tuple of names, surname followed by given names
    """
    # bunch of cleaning
    tidy_text = text.strip()  # remove some whitespace
    if tidy_text.isupper():  # excludes headers from doc tables, since all names are capitalised
        # replace hyphens with dashes, parens with spaces
        tidier = tidy_text.replace('–', '-').replace('(', ' ').replace(')', ' ')
        tidier_still = re.sub(r'\d', '', tidier)  # get rid of floating digits
        tidiest = tidier_still.split(' ' * 4)  # split by the gulf of spaces separating sur- and given names
        names = []
        for n in tidiest:
            if n != '':  # exclude empty strings
                n = ' '.join(n.split())  # reduce whitespace, replace
                n = n.replace(' - ', ' ').replace('- ', ' ').replace(' -', ' ').replace('-', ' ')  # remove dashes
                names.append(n)
        return names


def exception_catcher(a_list, file_name):
    """
    This function catches problems arising, ultimately, from how textract splits up long lines when it shouldn't.
    Since I don't want to go into textract itself, and since this error is bad, I deal with it here.
    The problem shows up is as names with single entries: that's our clue.
    :param a_list: a list of strings, from get_person_names
    :param file_name: file where the exception originates
    :return: True or False
    """

    # 1 = it's an appellate court name,
    # 2 = we give back a full name
    # 3 = exception we note for later, just skip for now

    exception_log = '/home/radu/insync/docs/CornellYears/6.SixthYear/currently_working/gender_judiciary/data/magistrati/judecatori/exception_log.csv'
    with open(exception_log, 'a') as exc:
        writer = csv.writer(exc, delimiter=',')

        # names of appellate courts
        ca = ['ALBA IULIA', 'BACAU', 'BRASOV', 'BUCURESTI', 'CLUJ' 'CONSTANTA', 'CRAIOVA', 'GALATI',
              'IASI', 'ORADEA', 'PITESTI', 'PLOIESTI', 'SUCEAVA', 'TARGU MURES', 'TIMISOARA']
        # one error has to do with Court of Appeals titles that are too long, the other with multiple given names
        # if it's the second, I just ignore it, the first two given names are enough to identify gender
        if a_list[0] in ca:
            return [1]

        # sometimes you get names like this ['2.', 'MUNGIU', 'ELENA']
        elif re.match(r'[0-9]+', a_list[0]) is not None:
            if len(a_list[0]) > 2:
                names = [a_list[1], a_list[2]]
                return [2, names]
            else:
                print(file_name)
                print(a_list)
                answr = input('There is a problem here, skip name? Y/N')
                if answr.upper() == 'Y':
                    return [3]
                else:
                    a2 = input('Which are the given names? Give list index: 1,2, etc.')
                    names = ['N/A', a_list[a2]]
                    return [2, names]


        elif len(a_list[0]) > 15:
            # this is for dealing with stuff like
            # ['NICULA SOBEA CAMELIA ANGELA'] or
            # ['TICHINDELEAN MARIOARA'] or
            # For the first two cases, keep first surname and last given name. May throw out info,
            # but at least we have an identifiable person with a given name for gender labelling.
            two_names = a_list[0].split(' ')
            if len(two_names[-1]) < 12:
                names = [two_names[0], two_names[-1]]
                return [2, names]

            # for cases like ['DIACONESCU MACARENCOSPERANŢA'] I have to change the source by hand, ugh
            else:
                writer.writerow([a_list, str(file_name)])
                return [3]
        else:
            return [3]


def file_remover(path, ext):
    """
    Recursively remove files with a certain extension from a directory.
    :param path: a path to the directory, as a string
    :param ext: the extension we want to remove, as string
    :return: None
    """

    for subdir, dirs, files in os.walk(path):
        for f in files:
            subdirectory_path = os.path.relpath(subdir, path)  # get the path to your subdirectory
            part_subpath = os.path.join(subdirectory_path, f)  # get the path to your file
            full_path = path + '/' + part_subpath
            if f.endswith(ext):
                os.remove(os.path.join(full_path))


def make_gend_dict(dict_path, data_files_path):
    """
    Reads csv's in a directory for names. If the name has a known gender in a dictionary, then assigns that gender
    to the name in the csv. Otherwise, it prompts you to provide a gender, writes in teh csv and also puts that new
    name:gender pair into the dictionary.
    :param data_files_path: path to the directory containing the data files
    :param dict_path: path to the name:gender dictionary
    :return: None
    """

    gend_dict = {}
    counter = 0
    # go through files, building gender dict
    for subdirs, dirs, files in os.walk(data_files_path):
        for f in files:
            if str(f)[-3:] == 'csv':
                # print(f)
                subdirectory_path = os.path.relpath(subdirs, data_files_path)  # get the path to your subdirectory
                f_subpath = os.path.join(subdirectory_path, f)  # get the path to your file
                full_path = data_files_path + '/' + f_subpath
                with open(full_path) as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    next(csv_reader)  # skip head
                    for row in csv_reader:
                        given_names = row[1].split(' ')
                        for name in given_names:
                            if name not in gend_dict and name.isalpha():  # prompt to assign name
                                print(name)
                                answer = input("What gender is this name? f,m,dk ")
                                if not ((answer == 'f') or (answer == 'm') or (answer == 'dk')):
                                    answer = input("Incorrect format, please, what gender is this name? f,m,dk ")
                                gend_dict[name] = answer
                                counter += 1

                            if counter % 10 == 0:  # update every ten answers
                                # dump the dict
                                with open(dict_path, 'w') as outfile:
                                    json.dump(gend_dict, outfile)

    # dump the dict
    with open(dict_path, 'w') as outfile:
        json.dump(gend_dict, outfile)


def assign_gender_to_csv(data_files_path, dict_path, error_file_path):
    """
    Read gender of names from dict and assign to appropriate column in csv files.
    :param data_files_path: path to directory containing data files
    :param dict_path: path to gender dict file
    :param error_file_path: path to the error log file
    :return: none
    """

    # NB: need to check the 2006 files (e.g. ca_craiova_01.04.2006.csv), looks like it's systematically
    # confused surnames and given names

    headers = ['surname', 'given name(s)', 'year', 'month', 'gender', 'base unit',
               'hierarchical level', 'appellate unit', 'tribunal unit']

    counter = 0

    with open(error_file_path, 'a') as efile:
        e_writer = csv.writer(efile, delimiter=';')

        with open(dict_path) as dict_file:
            gend_dict = json.load(dict_file)

            # go through files, assigning gender to names
            for subdirs, dirs, files in os.walk(data_files_path):
                for f in files:
                    if str(f)[-3:] == 'csv':

                        # keep track
                        counter += 1
                        print(f)
                        print(counter)

                        subdirectory_path = os.path.relpath(subdirs,
                                                            data_files_path)  # get the path to your subdirectory
                        f_subpath = os.path.join(subdirectory_path, f)  # get the path to your file
                        full_path = data_files_path + '/' + f_subpath

                        all_new_rows = []
                        with open(full_path) as inFile:
                            csv_reader = csv.reader(inFile, delimiter=',')
                            next(csv_reader)  # skip head
                            for row in csv_reader:
                                updated_row = row
                                person_gender = []
                                if row[4] == '':  # if there's no gender entry already
                                    # clean punctuation, split on spaces
                                    cleaner = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
                                    given_names = row[1].translate(cleaner).strip().split(' ')
                                    for name in given_names:
                                        if name not in gend_dict:
                                            # mark as 'don't know' and put errors in another file
                                            # for later inspection
                                            person_gender.append('dk')
                                            error = (str(f), row)
                                            e_writer.writerow(error)
                                        else:
                                            person_gender.append(gend_dict[name])
                                    if len(person_gender) > 1:  # if there's more than one name
                                        if not check_equal(person_gender):  # if the genders from the names don't match
                                            if ('f' in person_gender) and (
                                                    'm' in person_gender):  # gender contradiction
                                                print(row)
                                                print(f)
                                                answer = input("Gender contradiction, resolve please: f,m,dk ")
                                                if not ((answer == 'f') or (answer == 'm') or (answer == 'dk')):
                                                    answer = input(
                                                        "Incorrect format, please, what gender is this name? f,m,dk ")
                                                person_gender = answer
                                            else:  # if there's a clear label and a "don't know", opt for the clear label
                                                if 'f' in person_gender:
                                                    person_gender = 'f'
                                                elif 'm' in person_gender:
                                                    person_gender = 'm'
                                        else:  # when all the names are the same gender
                                            person_gender = person_gender[0]
                                    else:
                                        if type(person_gender) == list:
                                            person_gender = ' '.join(map(str, person_gender))  # make it a string
                                    updated_row[4] = person_gender
                                all_new_rows.append(updated_row)

                        # now write in the updated .csv
                        with open(full_path, 'w') as outfile:
                            writer = csv.writer(outfile, delimiter=',')
                            writer.writerow(headers)
                            for r in all_new_rows:
                                writer.writerow(r)


def check_equal(lst):
    """
    Check if every entry in the list is identical
    :param lst: a list
    :return: True or False
    """
    return lst[1:] == lst[:-1]


def get_fullpath(from_root, subdirs, filename):
    """
    Given a path starting from the root, then subdirectories file names from os.walk,
    return an absolute filepath.
    :param from_root: a filepath from root to the directory from whence os.walk starts its job
    :param
    :param
    :return:
    """

    subdirectory_path = os.path.relpath(subdirs, data_files_path)  # get the path to your subdirectory
    f_subpath = os.path.join(subdirectory_path, f)  # get the path to your file
    full_path = data_files_path + '/' + f_subpath


data_files_path = "/home/radu/insync/docs/CornellYears/6.SixthYear/currently_working/gender_judiciary/data/magistrati/judecatori/doc_format_clean"
gend_dict_path = '/home/radu/insync/docs/CornellYears/6.SixthYear/currently_working/gender_judiciary/data/magistrati/judecatori/ro_gender_dict.txt'
error_file = '/home/radu/insync/docs/CornellYears/6.SixthYear/currently_working/gender_judiciary/data/magistrati/judecatori/error_file.csv'

# dir_to_clean = "/home/radu/insync/docs/CornellYears/6.SixthYear/currently_working/gender_judiciary/data/magistrati/judecatori/doc_format_clean"
# doc_to_csv('judecatori/doc_format_clean')
# file_remover(dir_to_clean,'.csv')


# make_gend_dict(gend_dict_path,data_files_path)

# assign_gender_to_csv(data_files_path,gend_dict_path,error_file)
