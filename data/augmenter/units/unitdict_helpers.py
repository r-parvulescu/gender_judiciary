"""
Function for making a dictionary of unit-name : unit-code (e.g. court-name : court-code).
"""

import json


def set_unitcode_level(unit_name, unit_codes):
    """given a unit name return its code and hierarchical level"""
    code = unit_codes[unit_name.strip()]
    level = get_unit_level(code)
    return code + [level]


def get_unit_level(unit_code):
    """
    return a table with a column for court level: 1 = judecătorie (lowest level, one); 2 = tribunal (second level);
     3 = curte de apel (third level); 4 = înalta curte de casaţie şi justiţie (High Court, highest level)
    """
    if unit_code[-1] != '-88':
        level = 1
    elif unit_code[-2] != '-88':
        level = 2
    elif unit_code[-3] != '-88':
        level = 3
    else:
        level = 4
    return level


def hierarchy_to_unit_codes(parquet=False):
    """take a hierarchical dict of units and return a dict with unit names and codes"""
    units_hierarchical = 'parquets_hierarchical.txt' if parquet else 'courts_hierarchical.txt'
    units_codes = 'parquet_codes.txt' if parquet else 'court_codes.txt'
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
