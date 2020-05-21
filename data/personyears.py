""""
Pipeline from data collection to pre-processing (name cleaning, sampling, adding person IDs and gender, etc.)
"""

import csv
from prep import preprocess
from collector.converter import convert


if __name__ == '__main__':

    # the sequential feed from collecting to sampling
    professions = ['prosecutors', 'judges']
    for p in professions:
        print("---------------------------------------")
        print("PROCESSING THE: ", p.upper())
        print("---------------------------------------")

        # convert.make_pp_table(p)
        person_years = preprocess.preprocess(p)

        # save the complete table to disk
        outfile = 'prep/output/' + p + '_preprocessed.csv'
        with open(outfile, 'w') as out_file:
            writer = csv.writer(out_file)
            new_headers = ["cod rând", "cod persoană", "nume", "prenume", "sex", "instituţie", "an",
                           "ca cod", "trib cod", "jud cod", "nivel"]
            writer.writerow(new_headers)
            [writer.writerow(py) for py in person_years]
