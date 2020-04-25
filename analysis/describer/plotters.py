"""
Functions for plotting basic statistics.
"""

from matplotlib import pyplot as plt
import numpy as np
from scipy.ndimage.filters import uniform_filter1d
from analysis.describer import persons, mobility


def retirement_entry(person_year_table, start_year, end_year, outfile):
    """
    two-panel plot, shared x-axis:
    top: retirement probabilities on left y-axis and number of entrants on right y-axis
    bottom: retirement probabilities by level of judicial hierarchy
    only graph observations between second and second-to-last, exclude for weird edges from interval censoring
    """

    ret_count = mobility.mob_counts(person_year_table, start_year, end_year, 'out', year_sum=True)[1:-1]
    ent_count = [e[1] for e in mobility.entries(person_year_table, start_year, end_year, year_sum=True)]
    ret_probs = mobility.mob_percent(person_year_table, 'mişcat_out', ['an', 'nivel'])

    fig1 = plt.figure(figsize=(10, 5))
    x = np.linspace(start_year, end_year, len(range(start_year, end_year + 1)))[1:-1]

    # top panel, on retirements and entries
    ax_ret = fig1.add_subplot(211)
    ax_ret.plot(x, [i[1] for i in ret_count], 'b-', label='retirements')
    ax_ret.plot(x, ent_count, 'r--', label='entries')

    ax_ret.legend(loc='upper right', fancybox=True, fontsize='small')
    ax_ret.set_title('Yearly Number of Retirements and Entries, 2007-2017')
    ax_ret.set_ylabel('total number')
    ax_ret.tick_params(axis='y')
    yticks_ret = ax_ret.yaxis.get_major_ticks()
    yticks_ret[0].label1.set_visible(False)
    yticks_ret[-1].label1.set_visible(False)
    plt.setp(ax_ret.get_xticklabels(), visible=False)

    # bottom panel, on retirement probability by level
    ret_probs = [(*yr_lvl, prob) for yr_lvl, prob in ret_probs
                 if int(start_year + 1) <= int(yr_lvl[0]) <= int(end_year - 1)]  # flatten tuple of tuples
    lvl1 = [i[2] * 100 for i in ret_probs if i[1] == '1']
    lvl2 = [i[2] * 100 for i in ret_probs if i[1] == '2']
    lvl3 = [i[2] * 100 for i in ret_probs if i[1] == '3']
    lvl4 = [i[2] * 100 for i in ret_probs if i[1] == '4']

    ax_multi = fig1.add_subplot(212, sharex=ax_ret)
    ax_multi.plot(x, lvl1, 'r--', label='Local Court')
    ax_multi.plot(x, lvl2, 'b-', label='County Tribunal')
    ax_multi.plot(x, lvl3, 'g:', label='Regional Court of Appeals')
    ax_multi.plot(x, lvl4, 'k-.', label='High Court')

    xticks = ax_multi.xaxis.get_major_ticks()
    xticks[0].label1.set_visible(False)
    xticks[-1].label1.set_visible(False)
    yticks_multi = ax_multi.yaxis.get_major_ticks()
    yticks_multi[0].label1.set_visible(False)
    yticks_multi[-1].label1.set_visible(False)

    title = 'Yearly Retirement Probability by Judicial Level, ' + str(start_year) + '-' + str(end_year)
    ax_multi.set_title(title)
    ax_multi.set_xlabel('year')
    ax_multi.set_ylabel('retirement \n probability (%)')
    ax_multi.legend(loc='upper right', fancybox=True, fontsize='small')
    plt.tight_layout()
    plt.savefig(outfile)


def promotion_probs(person_year_table, start_year, end_year, outfile):
    """plot moving average of promotion probability, per level"""
    prom_probs = mobility.mob_percent(person_year_table, 'mişcat_up', ['an', 'nivel'])
    probs = [(*yr_lvl, prob) for yr_lvl, prob in prom_probs
             if int(start_year) <= int(yr_lvl[0]) <= int(end_year - 1)]  # flatten tuple of tuples
    # huge yearly variance, smooth with moving average of size 3, for edges just multiply edge value
    lvl1_avg = uniform_filter1d([p[2] for p in probs if p[1] == '1'], size=3, mode='nearest')
    lvl2_avg = uniform_filter1d([p[2] for p in probs if p[1] == '2'], size=3, mode='nearest')
    lvl3_avg = uniform_filter1d([p[2] for p in probs if p[1] == '3'], size=3, mode='nearest')

    fig1 = plt.figure(figsize=(10, 4.6))
    ax = fig1.add_subplot(111)
    x = [i for i in range(start_year, end_year)]

    ax.plot(x, lvl1_avg, 'r--', label='Local Court')
    ax.plot(x, lvl2_avg, 'b-', label='County Tribunal')
    ax.plot(x, lvl3_avg, 'g:', label='Regional Court of Appeals')

    ax.set_xticks([i for i in range(start_year + 1, end_year, 2)])
    yticks = ax.yaxis.get_major_ticks()
    yticks[0].label1.set_visible(False)
    yticks[-1].label1.set_visible(False)

    # put legend underneath x-axis
    box = ax.get_position()  # shrink axis height by 10% at bottom
    ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.14), fancybox=True, ncol=3, fontsize='small')

    title = 'Promotion Probability by Judicial Level (Moving Average), ' + str(start_year) + '-' + str(end_year - 1)
    plt.title(title)
    plt.xlabel("year")
    plt.ylabel("promotion \n probability (%)")
    plt.savefig(outfile)


def female_percent_graph(person_year_table, start_year, end_year, outfile):
    """line graphs percent female per year, per level"""
    percentages = persons.percent_female(person_year_table, levels=True)
    centages = [(*cent_lvl, cent) for cent_lvl, cent in percentages
                if int(start_year) <= int(cent_lvl[0]) <= int(end_year)]  # flatten tuple of tuples
    lvl1 = [i[2] * 100 for i in centages if i[1] == '1']
    lvl2 = [i[2] * 100 for i in centages if i[1] == '2']
    lvl3 = [i[2] * 100 for i in centages if i[1] == '3']
    lvl4 = [i[2] * 100 for i in centages if i[1] == '4']

    fig1 = plt.figure(figsize=(10, 4.6))
    ax = fig1.add_subplot(111)
    x = np.linspace(start_year, end_year, len(range(start_year, end_year + 1)))

    ax.plot(x, lvl1, 'r--', label='Local Court')
    ax.plot(x, lvl2, 'b-', label='County Tribunal')
    ax.plot(x, lvl3, 'g:', label='Regional Court of Appeals')
    ax.plot(x, lvl4, 'k-.', label='High Court')

    yticks = ax.yaxis.get_major_ticks()
    yticks[0].label1.set_visible(False)
    yticks[-1].label1.set_visible(False)
    ax.set_xticks([i for i in range(start_year + 1, end_year, 2)])

    # put legend underneath x-axis
    box = ax.get_position()  # shrink axis height by 10% at bottom
    ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.14), fancybox=True, ncol=4, fontsize='small')

    title = 'Percent Female by Judicial Level, ' + str(start_year) + '-' + str(end_year)
    plt.title(title)
    plt.xlabel("year")
    plt.ylabel("percent female")
    plt.savefig(outfile)
