#person_year_maker.py
#script for combining the employment rolls (in .csv format) of appellate units
# into yearly or multi-year, person-year

import os, csv, json
from collections import deque

def combine_tables(in_dir, out_path, name_dict_path,sample_month):
    """
    Combines subt_tables into one big one, assigning unique person-year and person IDs.
    :param in_dir: directory where the csv's to be combined reside
    :param out_path: path where the joined table will reside
    :param name_dict_path: path to json dict file with key:values of "normalised person name:ID"
    :param sample_month: int; specify which month (1-12) you'd like to sample from
    :return: None
    """

    infile_counter = 0
    person_year_id = 0

    #load name_dict
    with open(name_dict_path, 'r') as name_dict:
        ndict = json.load(name_dict)

        #open out_file
        out_header = ['person-year ID','person ID','surname','given name(s)','year','month',
                      'gender','base unit', 'hierarchical level','appellate unit','tribunal unit']
        with open(out_path,'w') as csv_out:
            writer = csv.writer(csv_out,delimiter=',')
            writer.writerow(out_header)

            #go through data tables
            for subdir, dirs, files in os.walk(in_dir):
                for f in files:
                    if str(f)[-3:]=='csv': #catch only csv's
                            if str(subdir)[-2:] == str(sample_month): #month to sample

                                # keep track for debugging control
                                infile_counter += 1
                                print(f)
                                print(infile_counter)
                                if infile_counter > 0:

                                    #get in_file absolute path
                                    subdirectory_path = os.path.relpath(subdir, in_dir)  #get path to subdirectory
                                    f_subpath = os.path.join(subdirectory_path, f)  #get path to file
                                    f_fullpath = os.path.join(in_dir,f_subpath) #get full filepath

                                    with open(f_fullpath,'r') as csv_in:
                                        reader = csv.reader(csv_in,delimiter=',')
                                        next(reader) #skip header
                                        for row in reader:
                                            person_year_id += 1
                                            #normalise name: strip diacritics, all lowercase
                                            fullname = row[0] + ' ' + row[1]

                                            if fullname not in ndict: #ask what to do
                                                print(f)
                                                print(fullname)
                                                ans = input("Full name not in dict, skip? Y/N")
                                                if ans.upper == 'Y':
                                                    continue
                                            else:
                                                person_id = ndict[fullname]
                                                #make new row with person-year ID and person ID
                                                new_row = deque(row)
                                                new_row.insert(0,person_id)
                                                new_row.insert(0,person_year_id)
                                                writer.writerow(new_row)


def make_name_id_dict(name_dict_path,in_dir,sample_month):
    """
    Makes a dictionary that associated each full name with a unique ID.
    :param name_dict_path: string of absolute path to the dictionary file
    :param in_dir: directory in which  to look for csv's containing names
    :param sample_month: int; specify which month (1-12) you'd like to sample from
    :return: None
    """

    file_counter = 0
    ndict = {"last ID":0}

    #go through data tables
    for subdir, dirs, files in os.walk(in_dir):
        for f in files:
            if str(f)[-3:] == 'csv':  # catch only csv's
                if str(subdir)[-2:] == str(sample_month): #month to sample

                    #keep track for debugging control
                    file_counter+=1
                    print(f)
                    print(file_counter)
                    if file_counter>0:

                        # get in_file absolute path
                        subdirectory_path = os.path.relpath(subdir, in_dir)  # get path to subdirectory
                        f_subpath = os.path.join(subdirectory_path, f)  # get subpath to file
                        f_fullpath = os.path.join(in_dir, f_subpath)  # get full filepath

                        with open(f_fullpath, 'r') as csv_in:
                            reader = csv.reader(csv_in, delimiter=',')
                            next(reader)  # skip header
                            for row in reader:
                                fullname = row[0] + ' ' + row[1]
                                if fullname not in ndict: # get or assign person ID
                                    person_id = ndict['last ID'] + 1
                                    ndict['last ID'] = person_id
                                    ndict[fullname] = ndict['last ID']

    #dump the dict
    with open(name_dict_path, 'w') as outfile:
        json.dump(ndict, outfile)


in_directory = "/home/radu/insync/docs/CornellYears/6.SixthYear/currently_working/gender_judiciary/data/magistrati/judecatori/doc_format_clean"
outfile_path = '/home/radu/insync/docs/CornellYears/6.SixthYear/currently_working/gender_judiciary/data/magistrati/judecatori/full_table.csv'
name_dictionary_path = '/home/radu/insync/docs/CornellYears/6.SixthYear/currently_working/gender_judiciary/data/magistrati/judecatori/name_ID_dict.txt'


#make_name_id_dict(name_dictionary_path,in_directory,12)
#combine_tables(in_directory,outfile_path,name_dictionary_path,12)

