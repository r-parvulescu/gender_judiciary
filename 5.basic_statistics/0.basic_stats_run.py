import csv
import entry_exit
import totals

if __name__ == '__main__':

    j_infile = "input_tables/judges_unit_gender_pid_mobility_level.csv"
    with open(j_infile, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        table = list(reader)

    print("TOTAL JUDGES PER YEAR")
    print(totals.people_per_year(table, 2005, 2018)[1:])
    print('----------------------------------------------------------------------------------------------------')
    print("TOTAL MOBILITY PER YEAR")
    print(totals.total_mobility(table, 2005, 2018))
    print('----------------------------------------------------------------------------------------------------')
    print("TOTAL PROMOTIONS PER YEAR")
    print(entry_exit.mobility_per_year_per_level(table, 2005, 2018, 'up', year_sum=True))
    print('----------------------------------------------------------------------------------------------------')
    print("TOTAL EXITS PER YEAR")
    print(entry_exit.mobility_per_year_per_level(table, 2005, 2018, 'out', year_sum=True))
    print("TOTAL ENTRIES PER YEAR")
    print(entry_exit.entries_per_year_per_level(table, 2005, 2018, year_sum=True))

    print('----------------------------------------------------------------------------------------------------')

    print("ENTRIES BY LEVEL PER YEAR")
    moves_by_level = entry_exit.entries_per_year_per_level(table, 2005, 2018, year_sum=False)
    for c in moves_by_level:
        print(c)

    print('----------------------------------------------------------------------------------------------------')

    print("EXITS PER LEVEL PER YEAR")
    moves_by_level = entry_exit.mobility_per_year_per_level(table, 2005, 2018, 'out', year_sum=False)
    for c in moves_by_level:
        print(c)
