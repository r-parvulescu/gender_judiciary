import csv
import get_samples
import add_cols

if __name__ == '__main__':

    j_infile = "input_tables/judges_unit_gender_pid.csv"
    j_outfile = "output_tables/judges_unit_gender_pid_mobility_level.csv"

    with open(j_infile, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        table = list(reader)

    table = get_samples.person_quarter_sampler(table)
    table = get_samples.person_year_sampler(table, 2)
    table = add_cols.add_mobility_column(table)
    table = add_cols.add_level_column(table)

    with open(j_outfile, 'w') as outfile:
        writer = csv.writer(outfile)
        header = ["id", "nume", "prenume", "sex", "instanță/parchet", "mişcat", "an", "lună",
                  "CA cod", "trib cod", "jud cod", "nivel"]
        writer.writerow(header)
        for row in table:
            writer.writerow(row)
