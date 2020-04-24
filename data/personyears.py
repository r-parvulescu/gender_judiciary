""""
Pipeline from data collection, to augmenting with new columns (gender, employment unit, etc.) to sampling.
"""

from augmenter.gender import gender_helpers
from collector.collect import collect_data
from augmenter.augment import augment_data
from sampler.sample import sample_data

if __name__ == '__main__':
    # preparing the dictionaries
    # gender_helpers.make_gender_dict('collector/judges.csv')

    # the sequential feed
    '''
    collect_data(True, prosecs=False)  # judges
    collect_data(True, prosecs=True)  # prosecutors
    
    augment_data(True, prosecs=False)  # judges
    augment_data(True, prosecs=True)  # prosecutors
    '''

    # sample_data(2, True, prosecs=False)  # judges
    # sample_data(4, True, prosecs=True)  # prosecutors

'''
# kept trying to get this to work but it fails with errors
# "attempted relative import beyond top-level package"
# and "ImportError: No module named 'converter'".
# basically when it tries to reference a module in a child sibling directory, and that module being referenced
# ITSELF references something else in a sibling directory, it breaks

#import sys

#print(sys.path)
#sys.path.append('/home/radu/insync/docs/CornellYears/6.SixthYear/currently_working/gender_judiciary/gender_judiciary_pycharm/data/collector/converter')


'''
