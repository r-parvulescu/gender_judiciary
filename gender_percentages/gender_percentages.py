# gender_percentages.py
# get yearly gender percentages from the person-month file

import csv
import os
from collections import OrderedDict
from unidecode import unidecode


def gender_ratio(inpath):
    """
    Copmute percent female, across differents times and units, then dump into a csv.
    :param inpath: string; path to the source data file
    :return: none, spits out csv-file, overwrites if something's already there
    """

    # make a list of length twenty, each containing an ordered dict for years 2005-2015, inclusive
    # each ket is a year, the value is a list of counts, first a count for females, second a count for males
    y = [OrderedDict(
        sorted({'2005': [0, 0], '2006': [0, 0], '2007': [0, 0], '2008': [0, 0], '2009': [0, 0], '2010': [0, 0],
                '2011': [0, 0], '2012': [0, 0], '2013': [0, 0], '2014': [0, 0], '2015': [0, 0]}.items(),
               key=lambda t: t[0]))
        for i in range(0, 20)]

    # make an ordered dict of appellate court areas, each containing an ordered dict of year-gender counts
    apell_areas = OrderedDict(sorted({'ALBA IULIA': y[0], 'BACAU': y[1], 'BRASOV': y[2], 'BUCURESTI': y[3],
                                      'CLUJ': y[4], 'CONSTANTA': y[5], 'CRAIOVA': y[6], 'GALATI': y[7],
                                      'IASI': y[8], 'ORADEA': y[9], 'PITESTI': y[10], 'PLOIESTI': y[11],
                                      'SUCEAVA': y[12], 'TARGU MURES': y[13], 'TIMISOARA': y[14]}.items(),
                                     key=lambda t: t[0]))

    # make an ordered dict for hierarchcial court levels, each containing an ordered dict of year-gender counts
    # 1=ICCJ, 2=Appellate Courts, 3=Tribunals, 4=Low Courts
    hrarch_lvls = OrderedDict(
        sorted({'1': y[15], '2': y[16], '3': y[17], '4': y[18]}.items(), key=lambda t: t[0]))

    # ordered dict of total male-female counts for year, across all units
    years_total = y[19]

    # open the person-month file
    with open(inpath, 'r') as inFile:
        reader = csv.reader(inFile, delimiter=',')
        next(reader)  # skip header

        # increment male and female counters for the appropriate years and units
        for row in reader:
            if row[6] == 'f':
                years_total[row[4]][0] += 1  # counters for years
                hrarch_lvls[row[8]][row[4]][0] += 1  # counters for hierarhical levels
                if row[9] != 'na':  # avoids supreme court, since it's covered by hierarchical level 1
                    apell_areas[unidecode(row[9])][row[4]][0] += 1  # counters for appellate units

            elif row[6] == 'm':
                years_total[row[4]][1] += 1  # by years
                hrarch_lvls[row[8]][row[4]][1] += 1  # by hierarhical level
                if row[9] != 'na':  # avoids supreme court
                    apell_areas[unidecode(row[9])][row[4]][1] += 1  # by appellate unit

    # calculate percent female of person-months, rounded to one decimal
    # note, this assumes that the ratio of female to male person-months does not vary systematically,
    # e.g. men don't move more than women in any given year. If this were the case this would be a faulty
    # estimate of the gender composition of different years and units
    yearly_percentages = ['Pecent Female Per Year', '']
    for y in years_total:
        yearly_percentages.append(prcnt(years_total[y][0], years_total[y][1], 1))

    # calculate percent female of person months (to one decimal) for appellate areas
    ac_prcnt = [[] for i in range(0, 15)]  # make list to store percentages
    ac_cntr = 0
    for ac in apell_areas:
        ac_prcnt[ac_cntr] = [ac, '']
        for y in apell_areas[ac]:
            ac_prcnt[ac_cntr].append(prcnt(apell_areas[ac][y][0], apell_areas[ac][y][1], 1))
        ac_cntr += 1

    # calculate percent female of person months (to one decimal) for hierarchical levels
    hl_prcnt = [[] for i in range(0, 4)]  # make list to store percentages
    hl_cntr = 0
    for hl in hrarch_lvls:
        hl_prcnt[hl_cntr] = [str(hl), '']
        for y in hrarch_lvls[hl]:
            hl_prcnt[hl_cntr].append(prcnt(hrarch_lvls[hl][y][0], hrarch_lvls[hl][y][1], 1))
        hl_cntr += 1

    # write to file of descriptive statistics
    header = ['Unit', '', '2005', '2006', '2007', '2008', '2009',
              '2010', '2011', '2012', '2013', '2014', '2015']

    with open("gender_percentages.csv", 'w') as outfile:
        writer = csv.writer(outfile, delimiter=',')
        writer.writerow(header)
        writer.writerow('\n')
        writer.writerow(yearly_percentages)

        writer.writerow('\n')
        writer.writerow(['Appellate Areas'])
        for acr in ac_prcnt:
            writer.writerow(acr)

        writer.writerow('\n')
        writer.writerow(['Hierarchical Levels'])
        for hlr in hl_prcnt:
            writer.writerow(hlr)


def prcnt(a, b, c):
    """
    Given a part and its total, returns the percentage to desired decimal points
    :param a: int, part we are calculating percentage for
    :param b: int, total of which percent is calculated
    :param c: int, decimal places desired
    :return: float, percentage
    """

    return round(((a / (a+b)) * 100), c)

in_path = "month_person_RO_judges_2005-2015.csv"
gender_ratio(in_path)
