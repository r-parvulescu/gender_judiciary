"""
Functions that help clean data, for both prosecutor and judge .doc files.
"""

from string import digits


def pre_clean(text, parquet):
    """remove some ad hoc strings causing known issues"""
    text = text.replace('PARCHETUL DE PE LÂNGĂ  ', '')
    text = text.replace('( DIN RAZA TRIBUNALUL BISTRIŢA - NĂSĂUD)',
                        '( DIN RAZA TRIBUNALULUI BISTRIŢA - NĂSĂUD)')
    # Bucharest sectors
    text = text.replace("LUI 1", "LUI UNU").replace("LUI 2", "LUI DOI").replace("LUI 3", "LUI TREI")
    text = text.replace("LUI 4", "LUI PATRU").replace("LUI 5", "LUI CINCI").replace("LUI 6", "LUI ȘASE")
    if parquet:
        text = text.replace("TOR 1", "TORULUI UNU").replace("TOR 2", "TORULUI DOI")
        text = text.replace("TOR 4", "TORULUI PATRU").replace("TOR 3", "TORULUI TREI")
        text = text.replace("TOR 5", "TORULUI CINCI").replace("TOR 6", "TORULUI ȘASE")
    text = text.translate(str.maketrans('', '', digits))  # remove digits
    text = text.translate(str.maketrans('', '', '.'))  # remove periods
    text = text.replace('–', '-')
    return text


def multiline_name_contractor(people_periods):
    """catch exceptions, find multiline names, contracts them to one line, clean, and return all names"""
    for idx, val in enumerate(people_periods):
        if (val[0] == '') and (val[1] != 'NR') and (val[1] != 'PROCURORULUI') and (val[1] != "ILFOV") \
                and (val[1] != "TERORISM"):
            people_periods[idx - 1][1] = people_periods[idx - 1][1] + ' ' + people_periods[idx][1]
    return [i for i in people_periods if i[0] != '']
