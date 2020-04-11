import person_id_assigner

if __name__ == '__main__':
    j_infile = "input_tables/judges_unit_gender.csv"
    j_outfile = "output_tables/judges_unit_gender_pid.csv"
    p_infile = "input_tables/prosecutors_unit_gender.csv"
    p_outfile = "output_tables/prosecutors_unit_gender_pid.csv"

    person_id_assigner.assign_unique_person_id(j_infile, j_outfile)

# TODO deal with known maiden names, i.e. those surnames in brackets

# TODO deal with unique names that occur at the same place, at the same time
# down to five of these IDs, still a bit of work to check things are behaving properly

# TODO not sure the deduplicators and ID mergers are updating the table properly, need to check more

# TODO update to use operator.itemgetter instead of lambda where possible, and use list.sort instead of
# sorted so there's less remaking things to put in memory

# TODO use literal constructors (e.g. on sets) wherever possible

#     with open(j_infile, 'r') as f:
#         reader = csv.reader(f)
#         next(reader, None)
#         table = list(reader)
