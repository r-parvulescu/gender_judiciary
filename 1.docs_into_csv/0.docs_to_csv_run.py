import docs_to_csv

if __name__ == '__main__':
    j_archive = 'judges_12.2005_04.2017.zip'
    p_archive = 'prosecutors_12.2005_04.2017.zip'
    j_directory = 'judges_12.2005_04.2017'
    p_directory = 'prosecutors_12.2005_04.2017'
    prosecutors_split_mark = 'PARCHETUL '
    judges_split_mark = 'JUDECĂTORIA |JUDECATORIA |TRIBUNALUL |CURTEA DE APEL'
    # docs_to_csv.docs_to_csv(p_directory, "prosecutors.csv", prosecutors_split_mark, parquet=True)
    docs_to_csv.docs_to_csv(j_directory, "judges.csv", judges_split_mark)
