""""
Pipeline from data collection, to augmenting with new columns (gender, employment unit, etc.) to sampling.
"""

from prep import preprocess
from prep.gender import gender
from prep.units import units
from collector.converter import convert


if __name__ == '__main__':
    # preparing the dictionaries

    # supplement the
    # gender.make_gender_dict('collector/converter/output/prosecutors/prosecutors_month.csv')
    # gender.make_gender_dict('collector/converter/output/prosecutors/prosecutors_year.csv')

    # units.hierarchy_to_codes('judges')
    # units.hierarchy_to_codes('prosecutors')

    # the sequential feed from collecting to sampling
    professions = ['judges']
    for p in professions:
        # convert.make_pp_table(p)
        preprocess.preprocess(p)

    # sample_data(2, True, prosecs=False)  # judges
    # sample_data(4, True, prosecs=True)  # prosecutors

    # TD_Olt_1988-2005 has sporadic year-month dates (i.e. still one obs per year, just some obs also give
    # the month and day). I removed the year-day data to avoid errors in the code thinking the data was
    # actually month level
