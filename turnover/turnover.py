# turnover.py
# using person-level IDs, calculate amount and qualities of turnover from person-period tables

import csv
import os
from collections import OrderedDict


def turnover(inpath, l, u):
    """
    Given a person-period table with unique person IDs, figure out who left and who came in between each period,
    and give statistics of that movement.
    :param inpath: str, path to person-period csv table
    :param l: int, lower period bound (e.g. 1998)
    :param u: int, upper period bound (e.g. 2008)
    :return: none, spit out csv of turnovers and stats thereof
    """
    os.getcwd()

    with open(inpath, 'r') as inFile:
        reader = csv.reader(inFile)
        next(reader)  # skip header

        # make ordered dict of period dicts
        dicts = OrderedDict(sorted({i: {} for i in range(l, u + 1)}.items(), key=lambda t: t[0]))

        # populate each dict with id-gender key-values
        for row in reader:
            dicts[int(row[4])][str(row[3])] = row[2]

        # compare consecutive sets for directional key:value differences, and save results
        # in turnover ordered dict
        turnover = OrderedDict()
        for i in range(l, u):
            leavers = set(dicts[i].items()) - set(dicts[i + 1].items())
            joiners = set(dicts[i + 1].items()) - set(dicts[i].items())

            male_left, female_left = 0, 0
            for j in leavers:
                if j[1] == "M":
                    male_left += 1
                if j[1] == "F":
                    female_left += 1
            total_left = male_left + female_left

            male_joined, female_joined = 0, 0
            for k in joiners:
                if k[1] == "M":
                    male_joined += 1
                if k[1] == "F":
                    female_joined += 1
            total_joined = male_joined + female_joined

            percent_women_left = prcnt(female_left, male_left, 0)
            total_personnel_change = total_left + total_joined
            net_personnel_gain = total_joined - total_left
            net_female_gain = (female_joined - female_left) - (male_joined - male_left)

            # dump into ordered dict
            years = str(i) + '-' + str(i + 1)
            turnover[years] = (total_left, female_left, total_joined, female_joined, total_personnel_change,
                               net_personnel_gain, net_female_gain)

        # write to csv
        head = ["period", "total left", "women left", "total joined", "women joined",
                "total turnover (leave + join)", "net personnel change (join - leave)",
                "net female change ([female join - female gain] -[male join - male gain])"]
        with open("iccj_turnover.csv", "w") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(head)
            writer.writerow('\n')

            for t in turnover.items():
                writer.writerow([t[0], t[1][0], t[1][1], t[1][2], t[1][3], t[1][4], t[1][5], t[1][6]])


def prcnt(a, b, c):
    """
    Given a part and its total, returns the percentage to desired decimal points
    :param a: int, part we are calculating percentage for
    :param b: int, other part, together sum to whole
    :param c: int, decimal places desired
    :return: float, percentage
    """

    return round(((a / (a + b)) * 100), c)

turnover("iccj_judecatori_2004-2018.csv", 2004, 2018)
