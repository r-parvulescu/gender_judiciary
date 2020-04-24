import json
import csv
import PyICU
from copy import deepcopy

given_name_mistakes = {"AMCA": "ANCA", "AMDREEA": "ANDREEA", "ANGELAA": "ANGELA", "CODRŢA": "CODRUŢA",
                       "CRIASTIANA": "CRISTIANA", "CRSITINA": "CRISTINA", "DANDU": "SANDU",
                       "DÂNZIANA": "SÂNZIANA", "ELRNA": "ELENA", "GENONEVA": "GENOVEVA", "GEORGICA": "GEORGICĂ",
                       "GHEORGEH": "GHEORGHE", "CIRNELIU": "CORNELIU", "IUNUŢ": "IONUŢ", "IYABELA": "ISABELA",
                       "LUARA": "LAURA", "MANUEMA": "MANUELA", "MARINENA": "MARINELA", "MRCEA": "MIRCEA",
                       "NICUŢOR": "NICUŞOR", "NILOLETA": "NICOLETA", "ORSALYA": "ORSOLYA", "OTILEA": "OTILIA",
                       "OTILIEA": "OTILIA", "PRTRONELA": "PETRONELA", "ROYALIA": "ROZALIA", "BUZĂU": '',
                       "VIRGINEI": "VIRGINEL", "C TIN": "CONSTANTIN", "D TRU": "DUMITRU", "CORIN A": "CORINA",
                       "MIHAELAIULIANA": "MIHAELA IULIANA", "GHEORGHW": "GHEORGHE", "VAENTIN": "VALENTIN",
                       "CĂTĂLI N": "CĂTĂLIN", "RONELA": "RONELLA", "ITILIA": "OTILIA", "ANC A": "ANCA",
                       "INSPECTOR CSM": '', "R?ZVAN": "RĂZVAN", "LUMINI?A": "LUMINIŢA", "CONSTAN?A": "CONSTANŢA",
                       "COASTACHE": "COSTACHE", "AIRELIANA": "AURELIANA", "ANABELA": "ANABELLA", "ANEE": "ANNE",
                       "ATILLA": "ATTILA", "CAREN": "CARMEN", "DUMITRIELA": "DUMITRELA", "ELANA": "ELENA",
                       "EUGEL": "EUGEN", "MARIETTA": "MARIETA", "SZENDA": "SZENDE", "ŞTEANIA": "ŞTEFANIA",
                       "KREISER": "KREISZER", "POMPILU": "POMPILIU", "SERCIU": "SERGIU"}

given_name_diacritics = {"ADELUTA": "ADELUŢA", "ANCUTA": "ANCUŢA", "ANISOARA": "ANIŞOARA", "ANUTA": "ANUŢA",
                         "AURAS": "AURAŞ", "BRANDUSA": "BRÂNDUŞA", "BRANDUŞA": "BRÂNDUŞA", "BRINDUSA": "BRÂNDUŞA",
                         "BRÎNDUŞA": "BRÂNDUŞA", "CALIN": "CĂLIN", "CATALIN": "CĂTĂLIN", "CLOPOTEL": "CLOPOŢEL",
                         "CONSTANTA": "CONSTANŢA", "COSTICA": "COSTICĂ", "CRACIUN": "CRĂCIUN",
                         "CRENGUTA": "CRENGUŢA", "DANTES": "DANTEŞ", "DANUT": "DĂNUŢ", "DANUŢ": "DĂNUŢ",
                         "DOINITA": "DOINIŢA", "DRAGOS": "DRAGOŞ", "DĂNUT": "DĂNUŢ", "FANEL": "FĂNEL",
                         "CAMPEANA": "CÂMPEANA", "CÎMPEANA": "CÂMPEANA", "FLORIŢA": "FLORIŢĂ",
                         "GHEORGITA": "GHEORGIŢĂ", "ROXAN": "ROXANA",
                         "GAROFITA": "GAROFIŢA", "GRATIELA": "GRAŢIELA", "HORATIU": "HORAŢIU", "ILENUTA": "ILENUŢA",
                         "IONUT": "IONUŢ", "JOITA": "JOIŢA", "LACRAMIOARA": "LĂCRIMIOARA", "IONICA": "IONICĂ",
                         "LACRAMOARA": "LĂCRIMIOARA", "LAURENTIU": "LAURENŢIU", "LAURENTIA": "LAURENŢIA",
                         "LENUTA": "LENUŢA", "LETITIA": "LETIŢIA", "LICUTA": "LICUŢA", "LUCRETIA": "LUCREŢIA",
                         "LUMINITA": "LUMINIŢA", "MIHAITA": "MIHĂIŢĂ", "MIHAIŢĂ": "MIHĂIŢĂ", "MIORITA": "MIORIŢA",
                         "MITICA": "MITICĂ", "MIUTA": "MIUŢA", "MUSATA": "MUŞATA", "NELUTA": "NELUŢA",
                         "NICOLITA": "NICOLIŢA", "NUTI": "NUŢI", "OPRICA": "OPRICĂ", "PATRITIU": "PATRIŢIU",
                         "PAUNIŢA": "PĂUNIŢA", "PETRICA": "PETRICĂ", "PETRISOR": "PETRIŞOR", "PETRUS": "PETRUŞ",
                         "PETRUTA": "PETRUŢA", "PUSA": "PUŞA", "RADITA": "RĂDIŢA", "SANDICA": "SĂNDICA",
                         "SASA": "SAŞA", "SEVASTITA": "SEVASTIŢA", "SMĂRĂNDITA": "SMĂRĂNDIŢA",
                         "SPERANTA": "SPERANŢA", "STEFAN": "ŞTEFAN", "STEFANIA": "ŞTEFANIA", "STELUTA": "STELUŢA",
                         "STERICA": "STERICĂ", "SÎNZIANA": "SÂNZIANA", "TAMAS": "TAMAŞ", "TANCUTA": "TANCUŢA",
                         "TANTA": "TANŢA", "VALERICA": "VALERICĂ", "VLADUT": "VLĂDUŢ", "ZOITA": "ZOIŢA",
                         "CODRUTA": "CODRUŢA", "DUMITRITA": "DUMITRIŢA", "FLORENTA": "FLORENŢA",
                         "MADALINA": "MĂDĂLINA", "MARIOARA": "MĂRIOARA", "BRADUTA": "BRĂDUŢA", "CHISCAN": "CHIŞCAN",
                         "LAURENTA": "LAURENŢA", "MĂRINICĂ": "MARINICĂ", "PĂCURETU": "PĂCUREŢU", "PRESURA": "PRESURĂ",
                         "RAZVAN": "RĂZVAN", "STANCESCU": "STĂNCESCU"}

'''
# remove names that should've been deal with by the transdict
with open("dicts/ro_gender_dict.txt") as gd:
    data = json.load(gd)
    mistake_replacers = given_name_mistakes.keys()
    diacritic_replacers = given_name_diacritics.keys()

    for m in mistake_replacers:
        data.pop(m, None)
    for d in diacritic_replacers:
        data.pop(d, None)

    with open("dicts/ro_gender_dict_purged.txt", 'w') as outfile:
        json.dump(data, outfile)
'''

'''
#put names in RO alphabetical order
unique_given_names = set()
with open(prosec_infile, 'r') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        given_names = row[1].split()
        for gn in given_names:
            unique_given_names.add(gn)

    collator = PyICU.Collator.createInstance(PyICU.Locale('ro_RO.UTF-8'))
    unique_given_names = [i for i in sorted(list(unique_given_names), key=collator.getSortKey)]

    for us in unique_given_names:
        print(us)
'''

'''
# get rid of key-value pairs you don't use, these are hangovers from previous editions
with open("dicts/ro_gender_dict.txt", 'r') as gd, open("tables/judges/judges_ids.csv", 'r') as infile:

    gender_dict = json.load(gd)
    reader = csv.reader(infile)
    next(reader)

    unique_given_names = set()
    for row in reader:
        given_names = row[1].split()
        for gn in given_names:
            unique_given_names.add(gn)

    new_dict = deepcopy(gender_dict)
    print(new_dict)
    for key in gender_dict.keys():
        if key not in unique_given_names:
            new_dict.pop(key, None)

    print(new_dict)
    with open("dicts/ro_gender_dict_purged.txt", 'w') as outfile:
        json.dump(new_dict, outfile)
'''

'''
#see surnames in gender dict
with open(gend_dict, 'r') as gd:
    gender_dict = json.load(gd)
    names = sorted(gender_dict.keys())
    for n in names:
        if gender_dict[n] == 'surname':
            print(n)
'''


def see_unique_unitnames(csv_file):
    """make a dict mapping dirty to clean and standardised unit names"""

    names = set()
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            unit_name = row[2]
            names.add(unit_name)
        names = sorted(list(names))
        for dn in names:
            print(dn)

# TODO assign parquet codes and genders for prosecutor data
# catch all common mess-up name-surname pairs, handle them uniquely
# then reduce all data down to quarters, all months in that quarter make a union
# make sure each person within quarter actually is unique, no doubling up for typos, etc.
# then sample one quarter (always the same quarter) each year
# need to map surnames with diacritics and correct mistakes


# multiline not cathing "PAŞCA CAMENIŢĂ SANDRA-IULIA"
# or DRUCAN GHEORGHE DANIEL, it looks like the multiname catcher really is missing a lot
# for the prosecutors
# DEAIL WITH WHAT IS CAUSING THIS: ENASESCUMIHAELA
# GUŞĂGEORGE	LUCIAN
# DEAL WITH ONE-AWAY LETTERS, LIKE "STOENESC	U ROXANA TEODORA"
# TODORANADRIAN	PETRE
# TULIŢĂIONUŢ
# CĂTĂLI N
