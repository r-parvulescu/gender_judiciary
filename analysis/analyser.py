"""
Pipeline for describing the data: description, inference, prediction.
"""

from analysis.describer import describe

if __name__ == '__main__':
    # judges
    describe.describe('judges', 'input/judges_personyears.csv', 2006, 2020)
    # prosecutors
    describe.describe('prosecutors', "input/prosecutors_personyears.csv", 2005, 2016, prosecs=True)
