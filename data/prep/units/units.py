"""
Function for  assigning the a unit-code to a person-period given the full name of its unit
"""

import json


def set_unitcode_level(unit_name, unit_codes):
    """given a unit name return its code and hierarchical level"""
    code = unit_codes[unit_name.strip()]
    level = get_unit_level(code)
    return code + [level]


def get_unit_level(unit_code):
    """
    return a table with a column for court level:
    1 = judecătorie (lowest level, one);
    2 = tribunal (second level);
    3 = curte de apel (third level);
    4 = înalta curte de casaţie şi justiţie (High Court, highest level)
    """
    if unit_code[-1] != '-88':
        level = '1'
    elif unit_code[-2] != '-88':
        level = '2'
    elif unit_code[-3] != '-88':
        level = '3'
    else:
        level = '4'
    return level


def get_unit_codes(profession):
    unit = ''
    if profession == 'prosecutors':
        unit = 'parquet'
    if profession == 'judges':
        unit = 'court'
    unit_codes = 'prep/units/' + unit + '_codes.txt'
    with open(unit_codes, 'r') as uc:
        return json.load(uc)


def hierarchy_to_codes(profession):
    """
    Convert a dictionary of institutions with hierarchical structure like this:

    {'COURT OF APPEALS X': ['CAX',
        {'TRIBUNAL A': ['TBA',
            {'LOCAL COURT 2': 'LC2'}
        }
    }

    Into a dict where each institution full name is associated with a code uniquely describing that institutions's
    place within the relevant professional judicial hierarchcy. So the hierarchy dictionary above (referring to judge
    institutions, i.e. courts) would generate the following code dictionary:

    'LOCAL COURT 2': 'CAX', 'TBA', 'LC2'
    'TRIBUNAL A': 'CAX, 'TBA', '-88'
    'COURT OF APPEALS A': 'CAX', '-88', '-88'

    By convention, the high court of appeals has the code: '-88', '-88', '-88'.

    Dump the code dict in a json.txt file.

    :param profession: string: 'judges', 'prosecutors', 'notaries', 'executori'
    :return: None
    """

    units_hierarchical = ''
    units_codes = ''
    parquet = bool

    if profession == 'judges':
        parquet = False
        units_hierarchical = 'prep/units/courts_hierarchical.txt'
        units_codes = 'prep/units/court_codes.txt'
    if profession == 'prosecutors':
        parquet = True
        units_hierarchical = 'prep/units/parquets_hierarchical.txt'
        units_codes = 'prep/units/parquet_codes.txt'

    units = {}
    with open(units_hierarchical) as ch:
        data = json.load(ch)
        for ca_k, ca_v in data.items():
            apellate = ca_k[22] if parquet else ca_k[0]
            if apellate == "C":
                ca_code = data[ca_k][0]
                units[ca_k] = [ca_code, '-88', '-88']
                for trib_k, trib_v in data[ca_k][1].items():
                    trib_code = data[ca_k][1][trib_k][0]
                    units[trib_k] = [ca_code, trib_code, '-88']
                    if ("COMERC" not in trib_k) and ("MINORI" not in trib_k):
                        for jud_k, jud_v in data[ca_k][1][trib_k][1].items():
                            jud_code = (data[ca_k][1][trib_k][1][jud_k])
                            units[jud_k] = [ca_code, trib_code, jud_code]
                else:
                    if parquet:
                        units["PARCHETUL DE PE LÂNGĂ ÎNALTA CURTE DE CASAŢIE ŞI JUSTIŢIE"] = ['-88', '-88', '-88']
                        units["DIRECŢIA DE INVESTIGARE A INFRACŢIUNILOR DE CRIMINALITATE ORGANIZATĂ ŞI TERORISM"] = \
                            ["DIICOT", '-88', '-88']
                        units["DIRECŢIA NAŢIONALĂ ANTICORUPŢIE"] = ['DNA', '-88', '-88']
                    else:
                        units["ÎNALTA CURTE DE CASAŢIE ŞI JUSTIŢIE"] = ['-88', '-88', '-88']

    with open(units_codes, 'w') as json_file:
        json.dump(units, json_file)
