"""
Functions for generating descriptive statistics.
"""

import csv
from analysis.describer import mobility, plotters, persons


def describe(profession, source_data, start_year, end_year, prosecs=False):
    """make table and figures of descriptive statistics"""

    outfile = 'describer/output/' + profession + '/descriptives.csv'
    fig1 = 'describer/output/' + profession + '/fig1_retirement_entry'
    fig2 = 'describer/output/' + profession + '/fig2_mobility_up_across'
    fig3 = 'describer/output/' + profession + '/fig3_percent_female'
    with open(source_data, 'r') as infile:
        reader = csv.reader(infile)
        next(reader, None)  # skip headers
        table = list(reader)
    # spit out basic statistics
    descriptives_table(table, outfile, start_year, end_year, prosecs=prosecs)
    # make figure 1, on retirements and entries
    plotters.retirement_entry(table, start_year, end_year, fig1)
    # make figure 2, on promotions
    plotters.promotion_probs(table, start_year, end_year, fig2)
    # make figure 3, on gender percentages
    plotters.female_percent_graph(table, start_year, end_year, fig3)


def descriptives_table(table, outfile, start_yr, end_yr, prosecs=False):
    """dump descriptive statistics in a csv"""
    stats = [("TOTAL MAGISTRATES PER YEAR", persons.people_per_year(table, start_yr, end_yr)[1:]),
             ("PERCENT FEMALE PER YEAR, PER LEVEL", persons.percent_female(table, levels=True)),
             ("TOTAL MOBILITY PER YEAR", mobility.total_mobility(table, start_yr, end_yr)),
             ("TOTAL ENTRIES PER YEAR", mobility.entries(table, start_yr, end_yr, year_sum=True)),
             ("ENTRIES BY PER YEAR, PER LEVEL", mobility.entries(table, start_yr, end_yr, year_sum=False)),
             ("TOTAL RETIREMENTS PER YEAR", mobility.mob_counts(table, start_yr, end_yr, 'out', year_sum=True)),
             ("RETIREMENTS PER YEAR, PER LEVEL", mobility.mob_counts(table, start_yr, end_yr, 'out', year_sum=False)),
             ("PROBABILITY OF RETIREMENT PER YEAR", mobility.mob_percent(table, 'mişcat_out', ['an'])),
             ("PROBABILITY OF RETIREMENT PER YEAR, PER LEVEL", mobility.mob_percent(table,
                                                                                    'mişcat_out', ['an', 'nivel'])),
             ("TOTAL PROMOTIONS PER YEAR", mobility.mob_counts(table, start_yr, end_yr, 'up', year_sum=True)),
             ("TOTAL PROMOTIONS PER YEAR, PER LEVEL", mobility.mob_counts(table, start_yr, end_yr,
                                                                          'up', year_sum=False)),
             ("PROBABILITY OF PROMOTION PER YEAR", mobility.mob_percent(table, 'mişcat_up', ['an'])),
             ("PROBABILITY OF PROMOTION PER YEAR, PER LEVEL", mobility.mob_percent(table,
                                                                                   'mişcat_up', ['an', 'nivel'])),
             ("TOTAL DEMOTIONS PER YEAR", mobility.mob_counts(table, start_yr, end_yr, 'down', year_sum=True)),
             ("TOTAL DEMOTIONS PER YEAR, PER LEVEL", mobility.mob_counts(table, start_yr, end_yr,
                                                                         'down', year_sum=False)),
             ("PROBABILITY OF DEMOTION PER YEAR", mobility.mob_percent(table, 'mişcat_down', ['an'])),
             ("PROBABILITY OF DEMOTION PER YEAR, PER LEVEL", mobility.mob_percent(table,
                                                                                  'mişcat_down', ['an', 'nivel'])),
             ("TOTAL LATERAL MOVES PER YEAR", mobility.mob_counts(table, start_yr, end_yr, 'across', year_sum=True)),
             ("TOTAL LATERAL MOVES PER YEAR, PER LEVEL", mobility.mob_counts(table, start_yr, end_yr,
                                                                             'across', year_sum=False)),
             ("PROBABILITY OF LATERAL MOVES PER YEAR", mobility.mob_percent(table, 'mişcat_across', ['an'])),
             ("PROBABILITY OF LATERAL MOVES PER YEAR, PER LEVEL",
              mobility.mob_percent(table, 'mişcat_across', ['an', 'nivel'])),
             ["RETIREMENTS PER YEAR PER COURT OF APPEALS, TOP 5"],
             ["RETIREMENTS PER YEAR PER TRIBUNAL, TOP 5"],
             ["RETIREMENTS PER YEAR PER JUDECĂTORIE, TOP 5"],
             ("PER COHORT, 5 YEAR COMPLETED MOBILITY COUNTS", mobility.mob_cohorts(table, 5, start_yr, end_yr)),
             ("PER COHORT, 5 YEAR COMPLETED MOBILITY PROBABILITIES",
              mobility.mob_cohorts(table, 5, start_yr, end_yr, percent=True))]
    with open(outfile, 'w') as f:
        writer = csv.writer(f)
        for s in stats:
            writer.writerow([s[0]])
            if ('LEVEL' in s[0]) or ('COUNTS' in s[0]):
                [writer.writerow(i) for i in s[1]]
            elif s[0][-1] == '5':
                if "APPEALS" in s[0]:
                    unit_list = ['PCA' + str(i) for i in range(1, 16)] + ['DIICOT', 'DNA'] if prosecs \
                        else ['CA' + str(i) for i in range(1, 16)]
                    mob = mobility.mobility_per_year_per_unit(table, unit_list, start_yr, end_yr,
                                                              '3', 'out', year_sum=False)
                elif "TRIBUNAL" in s[0]:
                    unit_list = ['PTB' + str(i) for i in range(1, 46)] if prosecs \
                        else ['TB' + str(i) for i in range(1, 47)]
                    mob = mobility.mobility_per_year_per_unit(table, unit_list, start_yr, end_yr,
                                                              '2', 'out', year_sum=False)
                elif "JUDECĂTORIE" in s[0]:
                    unit_list = ['PJ' + str(i) for i in range(1, 178)] if prosecs \
                        else ['J' + str(i) for i in range(1, 178)]
                    mob = mobility.mobility_per_year_per_unit(table, unit_list, start_yr, end_yr,
                                                              '1', 'out', year_sum=False)
                [writer.writerow([yr_unit[0], yr_unit[1][-5:]]) for yr_unit in mob]
            else:
                writer.writerow(s[1])
            writer.writerow('\n')
