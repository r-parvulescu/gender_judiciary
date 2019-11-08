# gender_ratios.py
# get yearly gender ratios from the person_year file

import csv
from collections import OrderedDict
from unidecode import unidecode
from natsort import natsorted


def gender_ratio(inpath, outpath):
    """
    Get gender ratios over time for each separate entity and for different aggregates thereof,
    then dump it into a csv.
    :param inpath: string; path to the source data file
    :param outpath: string; path to csv holding the descriptive statistics
    :return: None
    """

    # make a list of ordered dicts for years; first value in key list is female count, second is male count
    y = [OrderedDict(
        sorted({'2005': [0, 0], '2006': [0, 0], '2007': [0, 0], '2008': [0, 0], '2009': [0, 0], '2010': [0, 0],
                '2011': [0, 0], '2012': [0, 0], '2013': [0, 0], '2014': [0, 0], '2015': [0, 0]}.items(),
               key=lambda t: t[0]))
        for i in range(0, 20)]

    # first value in key list is female count, second is male count
    appellate_courts = OrderedDict(sorted({'ALBA IULIA': y[0], 'BACAU': y[1], 'BRASOV': y[2], 'BUCURESTI': y[3],
                                           'CLUJ': y[4], 'CONSTANTA': y[5], 'CRAIOVA': y[6], 'GALATI': y[7],
                                           'IASI': y[8], 'ORADEA': y[9], 'PITESTI': y[10], 'PLOIESTI': y[11],
                                           'SUCEAVA': y[12], 'TARGU MURES': y[13], 'TIMISOARA': y[14]}.items(),
                                          key=lambda t: t[0]))

    # 1=ICCJ, 2=Appellate Courts, 3=Tribunals, 4=Low Courts
    hierarchical_levels = OrderedDict(
        sorted({'1': y[15], '2': y[16], '3': y[17], '4': y[18]}.items(), key=lambda t: t[0]))

    years_total = y[19]

    with open(inpath, 'r') as infile:
        reader = csv.reader(infile, delimiter=',')
        next(reader)  # skip header

        for row in reader:
            # totals
            if row[6] == 'f':
                years_total[row[4]][0] += 1  # by year
                hierarchical_levels[row[8]][row[4]][0] += 1  # by hierarhical level
                if row[9] != 'na':  # avoids supreme court
                    appellate_courts[unidecode(row[9])][row[4]][0] += 1  # by appellate unit

            elif row[6] == 'm':
                years_total[row[4]][1] += 1  # by years
                hierarchical_levels[row[8]][row[4]][1] += 1  # by hierarhical level
                if row[9] != 'na':  # avoids supreme court
                    appellate_courts[unidecode(row[9])][row[4]][1] += 1  # by appellate unit

    # make ratios per year
    yearly_ratios = ['Per Year', '']
    for y in years_total:
        # print(round(years_total[y][0]/years_total[y][1],3))
        yearly_ratios.append(round(years_total[y][0] / years_total[y][1], 3))

    # make ratios per appellate unit
    ac_ratios = [[] for i in range(0, 15)]
    ac_counter = 0
    for ac in appellate_courts:
        ac_ratios[ac_counter] = [ac, '']
        for y in appellate_courts[ac]:
            ac_ratios[ac_counter].append(round(appellate_courts[ac][y][0] / appellate_courts[ac][y][1], 3))
        ac_counter += 1

    # make ratios per hierarchical level
    hl_ratios = [[] for i in range(0, 4)]
    hl_counter = 0
    for hl in hierarchical_levels:
        hl_ratios[hl_counter] = [str(hl), '']
        for y in hierarchical_levels[hl]:
            hl_ratios[hl_counter].append(round(hierarchical_levels[hl][y][0] / hierarchical_levels[hl][y][1], 3))
        hl_counter += 1

    # write to file of descriptive statistics
    header = ['Unit', '', '2005', '2006', '2007', '2008', '2009',
              '2010', '2011', '2012', '2013', '2014', '2015']
    with open(outpath, 'w') as outfile:
        writer = csv.writer(outfile, delimiter=',')
        writer.writerow(header)
        writer.writerow('\n')
        writer.writerow(yearly_ratios)

        writer.writerow('\n')
        writer.writerow(['Appellate Branches'])
        for acr in ac_ratios:
            writer.writerow(acr)

        writer.writerow('\n')
        writer.writerow(['Hierarchical Levels'])
        for hlr in hl_ratios:
            writer.writerow(hlr)


def surv_analysis_friendly(inpath, outpath, censor_period):
    """
    Turn a person-year table into on that is friendly for survival analysis (especially for the survival analysis
    package in scikit-learn). Each row is a unique person, showing the length of time they've been monitored, whether
    they experienced the event of interest (here, leaving the magistracy) or they're censored.
    :param inpath: string; path to person-month data file
    :param outpath: string; path to csv where data is to be dumped
    :param censor_period: int; the point at which data is censored
    :return: None
    """

    header = ['person ID', 'surname', 'given names', 'gender', 'time', 'event']
    id_dict = {}

    with open(inpath, 'r') as infile:
        reader = csv.reader(infile, delimiter=',')
        next(reader)  # skip header

        for row in reader:
            if row[1] not in id_dict:  # put in dict; True = event reached, False = censored
                if row[4] == str(censor_period):  # if at censor point
                    id_dict[row[1]] = [row[2], row[3], row[6], 1, False]
                else:  # mark as 'departed'
                    id_dict[row[1]] = [row[2], row[3], row[6], 1, True]
            else:
                if int(row[4]) < censor_period:  # last year of observation
                    id_dict[row[1]][3] += 1  # increment period
                else:
                    id_dict[row[1]][4] = False  # change censored status; don't count last year, since we count first

    # make survival analysis data file
    id_odict = OrderedDict(natsorted(id_dict.items()))
    with open(outpath, 'w') as outfile:
        writer = csv.writer(outfile, delimiter=',')
        writer.writerow(header)
        for i in id_odict:
            writer.writerow([i] + id_odict[i])


# in_path_gr = '/home/radu/insync/docs/CornellYears/6.SixthYear/currently_working/gender_judiciary/data/magistrati/judecatori/full_table.csv'
# out_path_gr = '/home/radu/insync/docs/CornellYears/6.SixthYear/currently_working/gender_judiciary/data/magistrati/judecatori/month_person_RO_judges_2005-2015.csv'
# gender_ratio(in_path_gr,out_path_gr)

in_path_sa = '/home/radu/insync/docs/CornellYears/6.SixthYear/currently_working/gender_judiciary/data/magistrati/judecatori/month_person_RO_judges_2005-2015.csv'
out_path_sa = '/home/radu/insync/docs/CornellYears/6.SixthYear/currently_working/gender_judiciary/data/magistrati/judecatori/surv_an_RO_judges_2005-2015.csv'
surv_analysis_friendly(in_path_sa, out_path_sa, 2015)
