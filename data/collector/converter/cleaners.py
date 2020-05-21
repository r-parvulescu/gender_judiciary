"""
Functions and translation dictionaries for cleaning irregularities in text and person-period tables.
"""

import re
import string


def pre_clean(text, parquet):
    """standardise text by transforming string variants to one version"""
    text = space_name_replacer(text, court_sectors_buc)  # Bucharest sectors, courts
    if parquet:
        text = space_name_replacer(text, parquet_sectors_buc)  # Bucharest sectors, parquets
    # # replace all "Î" in middle of word with "Â", remove digits, and problem characters
    text = re.sub(r'\BÎ+\B', r'Â', text)  # replace all "Î" in middle of word with "Â"
    text = text.translate(str.maketrans('', '', string.digits))
    text = text.translate(str.maketrans({'.': ' ', '–': ' ', '-': ' ', '/': ' ', "'": '', "Ț": "Ţ", "Ș": "Ş",
                                         "Ů": "Ţ", "ﾞ": "Ţ", "’": "Ţ", ";": "Ş", "Ř": "Ţ", "]": ' ', '[': ' ',
                                         '_': ' '}))
    return text


def multiline_name_contractor(people_periods):
    """
    ignore dud lines, find multiline names amd contract them to one line,
    return table of cleaned people_period
    """
    for idx, val in enumerate(people_periods):
        if (val[0] == '') and (val[1] != 'NR') and (val[1] != 'PROCURORULUI') and (val[1] != "ILFOV") \
                and (val[1] != "TERORISM"):
            people_periods[idx - 1][1] = people_periods[idx - 1][1] + ' ' + people_periods[idx][1]
    return [i for i in people_periods if i[0] != '']


def space_name_replacer(text, dictio):
    """
    replaces all instances of irregular name (dict key) with corresponding regular name (dict value)
    handles names with spaces in them, e.g. "Radu Andrei"
    """
    for key, value in dictio.items():
        if key in text:
            text = text.replace(key, value)
    return text


def no_space_name_replacer(text, dictio):
    """
    replaces all instances of irregular name (dict key) with corresponding regular name (dict value)
    handles names with no spaces, e.g. "Maria"
    """
    text_list = text.split()
    for t in text_list:
        if t in dictio:
            text = text.replace(t, dictio[t])
    return text


def deduplicate_list_of_lists(list_of_lists):
    """
    Remove duplicate rows from table as list of lists quicker than list comparison: turn all rows to strings,
    put them in a set, them turn set elements to list and add them all to another list.
    :param list_of_lists: what it sounds like
    :return: list of lists without duplicate rows (i.e. inner lists)
    """
    uniques = {'|'.join(row) for row in list_of_lists}
    return [row.split('|') for row in uniques]


court_names = {"ALSED": "ALEŞD", "TÎRGU": "TÂRGU", "TĂRGU": "TÂRGU", "STEHAIA": "STREHAIA", "PITESTI": "PITEŞTI",
               "HÎRLĂU": "HÂRLĂU", "CAMPULUNG": "CÂMPULUNG", "VÎNJU": "VÂNJU", "RM  VÂLCEA": "RÂMNICU VÂLCEA",
               "RM VÂLCEA": "RÂMNICU VÂLCEA", "RM VALCEA": "RÂMNICU VÂLCEA", "COMERCIAL": "COMERC SPECIAL",
               "SPECIALIZAT": "COMERC SPECIAL", "TG ": "TÂRGU ", "SF ": "SFÂNTU ", "ORASTIE": "ORĂŞTIE",
               "BALCESTI": "BĂLCEŞTI", "BÎRLAD": "BÂRLAD", "COSTESTI": "COSTEŞTI", "ARGES": "ARGEŞ",
               "DRAGASANI": "DRĂGĂŞANI", "SÎNNICOLAU": "SÂNNICOLAU", "ŞOMCUTA": "ŞOMCUŢA", "VALCEA": "VÂLCEA",
               "ICCJ": "ÎNALTA CURTE DE CASAŢIE ŞI JUSTIŢIE", "TRIBUNAL II": "TRIBUNALUL BIHOR",
               "CURTEA DE APEL MUREŞ": "CURTEA DE APEL TÂRGU MUREŞ", "TRIB ": "TRIBUNALUL ", "HATEG": "HAŢEG",
               "JUD ": "JUDECĂTORIA ", "PETROSANI": "PETROŞANI", "JUDECATORIA": "JUDECĂTORIA",
               "ROŞIORII": "ROŞIORI"}

parquet_names = {"BRASOV": "BRAŞOV", "BUCUREŞTI": "BUCUREŞTI", "CONSTANTA": "CONSTANŢA", "PITESTI": "PITEŞTI",
                 "PLOIESTI": "PLOIEŞTI", "CAMPULUNG": "CÂMPULUNG", "VÎNJU": "VÂNJU", "RM  VALCEA": "RÂMNICU VÂLCEA",
                 "COMERCIAL": "COMERC SPECIAL", "SPECIALIZAT": "COMERC SPECIAL", "TG MURES": "TÂRGU MUREŞ",
                 "LEHLIU GARA": "LEHLIU GARĂ", "ODORHEIUL": "ODORHEIU", "ROSIORI": "ROŞIORI", "TÎRGU": "TÂRGU",
                 "TARGU": "TÂRGU", "IALOMITA": "IALOMIŢA", "ÎALTA": "ÎNALTA", "SÎNNICOLAU": "SÂNNICOLAU",
                 "TG BUJOR": "TÂRGU BUJOR", "LAPUS": "LĂPUŞ", "SECTORULUI CINCI BUCUREŞTI": "SECTORULUI CINCI",
                 "SECTORULUI DOI BUCUREŞTI": "SECTORULUI DOI", "SECTORULUI PATRU BUCUREŞTI": "SECTORULUI PATRU",
                 "SECTORULUI TREI BUCUREŞTI": "SECTORULUI TREI", "SECTORULUI UNU BUCUREŞTI": "SECTORULUI UNU",
                 "SECTORULUI ŞASE BUCUREŞTI": "SECTORULUI ŞASE", "SFANTU": "SFÂNTU", "ŞOMCUTA": "ŞOMCUŢA",
                 "JUDECĂTORIAVIŞEU": "JUDECĂTORIA VIŞEU", "TRIBUNALULBRAŞOV": "TRIBUNALUL BRAŞOV",
                 "TIMISOARA": "TIMIŞOARA", "HĂRŞOVA": "HÂRŞOVA", "CALARASI": "CĂLĂRAŞI",
                 "CÎMPENI": "CÂMPENI", "FAGARAS": "FĂGĂRAŞ", "INTORSURA BUZAULUI": "ÎNTORSURA BUZĂULUI",
                 "JUGOJ": "LUGOJ", "ZARNESTI": "ZĂRNEŞTI", "TRIBUNLAUL": "TRIBUNALUL", "INSURĂŢEI": "ÎNSURĂŢEI",
                 "REŞITA": 'REŞIŢA', "TÂRNAVENI": "TÂRNĂVENI", "CARAS SEVERIN": "CARAŞ SEVERIN",
                 "PROCURATURA JUDEŢEANĂ": "PARCHETUL DE PE LÂNGĂ TRIBUNALUL", "RĂCANI": "RĂCARI", "AGNIŢA": "AGNITA",
                 "PROCURATURA LOCALĂ": "PARCHETUL DE PE LÂNGĂ JUDECĂTORIA"}

court_sectors_buc = {"LUI 1": "LUI UNU", "LUI 2": "LUI DOI", "LUI 3": "LUI TREI", "LUI 4": "LUI PATRU",
                     "LUI 5": "LUI CINCI", "LUI 6": "LUI ŞASE",
                     'RAZA TRIBUNALUL BISTRI': 'RAZA TRIBUNALULUI BISTRI'}

parquet_sectors_buc = {"PARCHETUL DE PE LÂNGĂ  ": '', "TOR 1": "TORULUI UNU", "TOR 2": "TORULUI DOI",
                       "TOR 4": "TORULUI PATRU", "TOR 3": "TORULUI TREI", "TOR 5": "TORULUI CINCI",
                       "TOR 6": "TORULUI ŞASE", 'TORUL 1': "TORULUI UNU", "TORUL 2": "TORULUI DOI",
                       "TORUL 3": "TORULUI TREI", "TORUL 4": "TORULUI PATRU", "TORUL 5": "TORULUI CINCI",
                       "TORUL 6": "TORULUI ŞASE", "TRIBUNALULMF": "TRIBUNALUL PENTRU MINORI ŞI FAMILIE"}

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
                       "KREISER": "KREISZER", "POMPILU": "POMPILIU", "SERCIU": "SERGIU",
                       "ROMEO PETER": "ROMEO PÉTER", "CU PENSIE": '', 'FLOREA CRISTINA': 'FLORÉA CRISTINA',
                       "CU PLEACĂ ART": "", "SILIVIU": "SILVIU", "MARCECL": "MARCEL", "DANIELLA": "DANIELA",
                       "MARIEANA": "MARIANA", "PANTELEMON": "PANTELIMON", "OLIMPIEA": "OLIMPIA",
                       "VERGICICA": 'VERGINICA', "PARASCHIEVA": "PARASCHEVA", "NCOLAE": "NICOLAE", "TITIANA": "TATIANA",
                       "EUJEN": "EUGEN", "VIORIVA": 'VIORICA', "EMANELA": "EMANUELA", "VASIICĂ": "VASILICĂ",
                       "DUMMITRU": "DUMITRU", "EMANUEAL": "EMANUEL", "VASILII": 'VASILI', "ANTONETA": "ANTOANETA",
                       "ALEXANDR": "ALEXANDRA", "DIDONIA": "DIDONA", "CRISITINA": "CRISTINA"}

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
                         "RAZVAN": "RĂZVAN", "STANCESCU": "STĂNCESCU", "ENIKO": "ENIKŐ", "MANDICA": "MANDICĂ",
                         "ANIŞOARĂ": "ANIŞOARA", "ILEANUŢA": "ILENUŢA", "ALIOSA": "ALIOŞA", "FRASINA": "FRĂSINA",
                         "TANCUŢA": "TĂNCUŢA", "JANOS": "JÁNOS", "TAŢIANA": "TATIANA", "AŞLAN": 'ASLAN',
                         "SADÎC": 'SADÂC', "MIŢICĂ": "MITICĂ"}

prosec_surname_replacers = {"HĂLCIUG": "HĂLGIUG", "AILOAIE": "AILOAE", "ANDREIAS": "ANDREIAŞ",
                            "ANTĂLOAE": "ANTĂLOAIE", "ANUŢA": "ANUŢĂ", "APETROAIEI": "APETROIE", "ARAMA": "ARAMĂ",
                            "ARGESEANU": "ARGEŞEANU", "AVĂDĂNEI": "AVĂDĂNII", "BĂDIŢA": "BĂDIŢĂ",
                            "BĂRBUCIANU": "BĂRBUCEANU", "BANICA": "BANICĂ", "BLAJAN": "BLĂJAN", "BLANARU": "BLĂNARU",
                            "BOŢOCHINĂ": "BOŢOGHINĂ", "CAUTIS": "CAUTIŞ", "CEASCAI": "CEAŞCAI", "CEASCĂI": "CEAŞCAI",
                            "CECALACEAN": "CECĂLACEAN", "CENUSE": "CENUŞE", "CHIRILA": "CHIRILĂ", "CHIS": "CHIŞ",
                            "CIMPEAN": "CÂMPEAN", "CIOARA": "CIOARĂ", "CISMASU": "CISMAŞU", "CIUMARNEAN": "CIUMĂRNEAN",
                            "COCÎRLĂ": "COCÂRLĂ", "COMANITA": "COMĂNIŢĂ", "CREŢ": "CRET", "CUBLESAN": "CUBLEŞAN",
                            "CÎMPEAN": "CÂMPEAN", "CĂPĂŢÎNĂ": "CĂPĂŢÂNĂ", "DASCALU": "DASCĂLU", "DONTETE": "DONŢETE",
                            "DRAGAN": "DRĂGAN", "FACKELMAN": "FACKELMANN", "FOITOS": "FOITOŞ", "FRUNZA": "FRUNZĂ",
                            "GHITU": "GHIŢU", "GLONT": "GLONŢ", "GRIGORAS": "GRIGORAŞ", "GÎDEA": "GÂDEA",
                            "HARTMAN": "HARTMANN", "HOBINCU": "HOBÎNCU", "IANUS": "IANUŞ", "IASINOVSCHI": "IAŞINOVSCHI",
                            "IFTINICHI": "IFTINCHI", "ILIES": "ILIEŞ", "IONITA": "IONIŢA", "JABA": "JABĂ",
                            "JAŞCANUI": "JAŞCANU", "JUGASTRU": "JUGĂSTRU", "JĂRDIANA": "JĂRDIEANU",
                            "JĂRDIANU": "JĂRDIEANU", "KOVESI": "KÖVESI", "LIVADARU": "LIVĂDARU",
                            "LIVĂDARIU": "LIVĂDARU", "LIŢA": "LIŢĂ", "LĂNCRĂJAN": "LĂNCRĂNJAN", "MASCAS": "MASCAŞ",
                            "MATES": "MATEŞ", "MERISESCU": "MERIŞESCU", " MESAROS": "MESAROŞ", "MICLOSINĂ": "MICLOŞINĂ",
                            "MIERLITA": "MIERLIŢĂ", "MIRISAN": "MIRIŞAN", "MITRICA": "MITRICĂ", "MOACA": "MOACĂ",
                            "MORIŞCA": "MORIŞCĂ", "MAMALIGAN": "MĂMĂLIGAN", "MĂNDICA": "MĂNDICĂ", "NARITA": "NARIŢA",
                            "NEAMTU": "NEAMŢU", "NEGRUTIU": "NEGRUŢIU", "NĂVODARU": "NĂVĂDARU", "PAIUSI": "PAIUŞI",
                            "PETRICA": "PETRICĂ", "PETRUSCA": "PETRUŞCĂ", "PLESCA": "PLEŞCA", "POREMSCHI": "POREMBSCHI",
                            "POSTICA": "POSTICĂ", "POTERASU": "POTERAŞU", "POTÎRCĂ": "POTÂRCĂ", "PÎRLOG": "PĂRLOG",
                            "PRISECARIU": "PRISECARU", "PROSA": "PROŞA", "PURTAN": "PURTANT", "PÎRVU": "PÂRVU",
                            "PÎRCĂLĂBESCU": "PÂRCĂLĂBESCU", "RADOI": "RĂDOI", "RADUCANU": "RĂDUCANU",
                            "RAKOCZI": "RAKOCZY", "RASCOTA": "RASCOTĂ", "REINKE": "REINCKE", "SADIC": "SADÎC",
                            "SFÎRIAC": "SFÂRIAC", "SITIAVU": "SITIARU", "SOVA": "ŞOVA", "SPERIUSI": "SPERIUŞI",
                            "STANCULESCU": "STĂNCULESCU", "STEPĂNESCU": "STEPANENCU", "STOENESC": "STOENESCU",
                            "STRANCIUC": "STRANCIUG", "STRUNA": "STRUNĂ", "STRÎMBEI": "STRÂMBEI", "STÎNGĂ": "STÂNGĂ",
                            "SUBTIRELU": "SUBŢIRELU", "SUTMAN": "SUTIMA", "TARNOVIETCHI": "TARNOVIEŢCHI",
                            "TELEKI": "TELEKY", "TIGANAS": "ŢIGĂNAŞ", "TIGANUS": "ŢIGĂNUŞ", "TINICA": "TINICĂ",
                            "TOLOARGĂ": "TOLOROAGĂ", "TOMOIESCU": "TOMOESCU", "TOMOIOAGĂ": "TOMOIAGĂ",
                            "TOPLICEANU": "TOPOLICEANU", "TRASTAU": "TRASTĂU", "VACARU": "VĂCARU", "VEISA": "VEIŞA",
                            "VESTEMANU": "VEŞTEMEANU", "VLADESCU": "VLĂDESCU", "VRÎNCIANU": "VRÂNCIANU",
                            "VÎLCU": "VÂLCU", "ZAMFIRECU": "ZAMFIRESCU", "ŢÎRLEA": "ŢÂRLEA", "ŢÂBÂRNĂ": "ŢĂBÂRNĂ",
                            "ADRINOIU": "ANDRINOIU", "AMUSCALIŢEI": "AMUSCĂLIŢEI", "BADICA": "BĂDICA",
                            "BALAS": "BALAŞ", "BALOŞ": "BOLOŞ", "BARAI": "BARA", "BILHA": "BÂLHA", "BOCHIS": "BOCHIŞ",
                            "BORS": "BORŞ", "BOSCANU": 'BOSIANU', "BOSTIOG": "BOŞTIOG", "BOTOC": "BOŢOC",
                            "BRATULEA": "BRĂTULEA", "BIRSAN": "BÂRSAN", "BALDEA": "BÂLDEA", "BITU": "BÂTU",
                            "BABUŢĂU": "BĂBUŢĂU", "BĂDICA": "BĂDICĂ", "BAGEAG": "BĂGEAG", "CALIN": "CĂLIN",
                            "CECĂLACEAN": "CECĂLĂCEAN", "CERGHIZAN": "CERCHIZAN", "CERGA": "CERGĂ",
                            "GHIRILĂ": "CHIRILĂ", "CIMPEANA": "CIMPEANU", "CIMPOIERU": "CIMPOERU",
                            "CIOCHINA": 'CIOCHINĂ', "CITIRIGA": "CITIRIGĂ", "CIOBOTARIU": "CIUBOTARIU",
                            "COJOACA": "COJOACĂ", "COSNEANU": "COŞNEANU", "CRACIUNESCU": 'CRĂCIUNESCU',
                            "CRISU": "CRIŞU", "CALINESCU": "CĂLINESCU", "CĂRĂMIZANU": "CĂRĂMIZARU", "DUSA": "DUŞA",
                            "DUTOIU": 'DUŢOIU', "FELDIOREAN": "FELDIOREANU", "FISCHEV": "FISCHER", "GABURA": 'GABURĂ',
                            "GARL": "GAL", "GERENY": "GERENYI", "GOSEA": "GOŞEA", "HARLAMBIE": "HARALAMBIE",
                            "HÂRŞMAN": "HIRŞMAN", "ILIESCI": "ILIESCU", "MARIS": "MARIŞ", "MESAROS": 'MESAROŞ',
                            "MIHILĂ": "MIHĂILĂ", "MORŞOI": "MURŞOI", "MOTOARCA": "MOTOARCĂ", "MOSOIU": "MOŞOIU",
                            "MURESAN": 'MUREŞAN', "MUT": "MUŢ", "MĂCEŞANU": "MĂCEŞEANU", "NEGUŢ": "NEGRUŢ",
                            "NICOARA": "NICOARĂ", "NISIOI": "NISOI", "NITESCU": 'NIŢESCU', "NASTASIE": "NĂSTASIE",
                            "ODIHNĂ": "ODINĂ", "ONA": "ONEA", "OPARIUC": "OPĂRIUC", "PANCESCU": "PĂNCESCU",
                            "PANA": "PANĂ", "PANTURU": 'PANŢURU', "PAUN": 'PĂUN', "PASALEGA": 'PAŞALEGA',
                            "PASTIU": 'PAŞTIU', "PRAŢA": "PAŢA", "PETRAN": 'PETREAN', "PRUNA": 'PRUNĂ',
                            "PĂRCĂLĂBESCU": 'PÂRCĂLĂBESCU', "PAUNA": "PĂUNA", "RADUCA": "RADUICA", "ROMAS": "ROMAŞ",
                            "ROTARIU": 'ROTARU', "RADULESCU": 'RĂDULESCU', "SCALETCHI": "SCALEŢCHI",
                            "STANCESCU": "STĂNCESCU", "STANCIOIU": "STĂNCIOIU", "STEFAN": 'ŞTEFAN', "SUTIMA": "SUTIMAN",
                            "SINGEORZAN": "SÂNGEORZAN", "TAMAŞ": 'TĂMAŞ', "TANASE": 'TĂNASE', "TAPLIUC": "ŢAPLIUC",
                            "TRAISTARU": "TRĂISTARU", "TRINCĂ": "TRÂNCĂ", "TURLEA": 'ŢURLEA', "TANASĂ": 'TĂNASĂ',
                            "TARAŞ": "TĂRAŞ", "VESTEMEAN": "VEŞTEMEAN", "VESTEMEANU": "VEŞTEMEANU",
                            "VINTILA": "VINTILĂ", "VOINA": 'VOINEA', "VIJIAC": "VÂJIAC", "VADUVAN": "VĂDUVAN",
                            "VĂETIŞI": "VĂETIŞ", "VĂSII": "VĂSÂI", "ZAPODEANU": "ZĂPODEANU", "SELARU": "ŞELARU",
                            "SENTEŞ": "ŞENTEŞ", "SPAIUC": "ŞPAIUC", "TICOFSCHI": "ŢICOFSCHI", "MURSOI": "MURŞOI"}

judges_surname_replacers = {"ACIOBANITEI": "ACIOBĂNIŢEI", "AFRASINIE": "AFRĂSINIE", "AILENA": "AILENE",
                            "AIONITOAIE": "AIONIŢOAIE", "ANCUTA": "ANCUŢA", "ANUTI": "ANUŢI", "ARBANAS": "ARBĂNAŞ",
                            "ASTALAŞ": "ASTĂLAŞ", "AVASILCĂI": "AVASILICĂI", "AXÎNTI": "AXINTI",
                            "BADESCU": "BĂDESCU", "BADICEANU": "BĂDICEANU", "BADULESCU": "BĂDULESCU",
                            "BENEGIU": "BENEGUI", "BLEOANCĂ": "BLEOANCĂ", "BLANARIU": "BLĂNARIU", "BOBOS": "BOBOŞ",
                            "BOCHIS": "BOCHIŞ", "BOLOS": "BOLOŞ", "BONTAS": "BONTAŞ", "BRATIS": "BRATIŞ",
                            "BREZAE": "BREZAIE", "BRESUG": "BREŞUG", "BRÎNZICĂ": "BRĂNZICĂ", "BUTUCA": "BUTUCĂ",
                            "BUZA": "BUZĂ", "BÎRSESCU": "BÂRSESCU", "BÎRŞĂŞTEANU": "BÎRSĂŞTEANU", "BĂISAN": "BĂIŞAN",
                            "CAMPEAN": "CÂMPEAN", "CAPOTA": "CAPOTĂ", "CEAUSESCU": "CEAUŞESCU", "CETERAS": "CETERAŞ",
                            "CEUCA": "CEUCĂ", "CHIDOVĂŢ": "CHIDOVEŢ", "CHIRILA": "CHIRILĂ", "CIOARA": "CIOARĂ",
                            "CIRCIUMARU": "CÂRCIUMARU", "CIRSTESCU": "CÂRSTESCU", "CIRSTOCEA": "CÂRSTOCEA",
                            "COARNA": "COARNĂ", "CODINA": "CODINĂ", "COJOCARIU": "COJOCARU", "CORAS": "CORAŞ",
                            "CORUGA": "CORUGĂ", "COSTASI": "COSTAŞI", "CRISAN": "CRIŞAN", "DANAILA": "DĂNĂILĂ",
                            "DANILA": "DĂNILĂ", "DANILEŢ": "DĂNILEŢ", "DARABAN": "DĂRĂBAN", "DRAGOS": "DRAGOŞ",
                            "DUDAS": "DUDAŞ", "DUMINECA": "DUMINECĂ", "DURBACA": "DURBACĂ", "DUSA": "DUŞA",
                            "DUTA": "DUŢĂ", "DUTĂ": "DUŢĂ", "FAZAKAŞ": "FAZAKAS", "FALAMAS": "FĂLĂMAS",
                            "FĂNUTA": "FĂNUŢĂ", "FARCAS": "FARCAŞ", "FRAŢILESCU": "FRĂŢILESCU",
                            "FUNDATUREANU": "FUNDĂTUREANU", "GAINA": "GĂINĂ", "GAISTEANU": "GĂIŞTEANU",
                            "GALAŢANU": "GĂLĂŢANU", "GÂRLECI": "GÂRLICI", "GHERCA": "GHERCĂ", "GHILA": "GHILĂ",
                            "GRADINARIU": "GRĂDINARIU", "GRADINARU": "GRĂDINARU", "GRIGORASCU": "GRIGORAŞCU",
                            "GROAPA": "GROAPĂ", "GUTU": "GUŢU", "HANCAŞ": "HANCĂŞ", "HARTMAN": "HARTMANN",
                            "HOLBOCEANU": "HOLBOCIANU", "IONITA": "IONIŢĂ", "ISAILĂ": "ISĂILĂ",
                            "ISTRATESCU": "ISTRĂTESCU", "IUJĂ": "IUJA", "LACUSTEANU": "LĂCUSTEANU",
                            "LASCONI": "LĂSCONI", "LINTA": "LINŢA", "LITA": "LIŢĂ", "LIXANDROIU": "LIXĂNDROIU",
                            "LUCACEL": "LUCĂCEL", "LUCGHIAN": "LUCHIAN", "LUCHOAN": "LUCHIAN", "MADUTA": "MĂDUŢĂ",
                            "MANASTIREANU": "MĂNĂSTIREANU", "MARIS": "MARIŞ", "MAIEREANU": "MĂIEREANU",
                            "MĂSTACAN": "MĂSTĂCAN", "MÂNGAŢĂ": "MÂNGÂŢĂ", "MERISESCU": "MERIŞESCU",
                            "MEROBIAN": "MESROBIAN", "MESTER": "MEŞTER", "MIHAIANU": "MIHĂIANU", "MINCA": "MINCĂ",
                            "MOISA": "MOISĂ", "MONCIA": "MONCEA", "MOTAN": "MOŢAN", "MPSTPCAN": "MĂSTĂCAN",
                            "MUSAT": "MUŞAT", "MUŞINOU": "MUŞINOI", "NASTASE": "NĂSTASE", "NASTASIE": "NĂSTASIE",
                            "NĂSTĂSIE": "NĂSTASIE", "NEGOIŢA": "NEGOIŢĂ", "NEGRILA": "NEGRILĂ", "NEMES": "NEMEŞ",
                            "NEMTEANU": "NEMŢEANU", "NENITA": "NENIŢĂ", "NIŢUQÂ": "NIŢU", "NOSLACAN": "NOŞLĂCAN",
                            "OANNCEA": "OANCEA", "OBOROCEANU": "OBOROCIANU", "OPRIS": "OPRIŞ", "ORASEANU": "ORĂŞEANU",
                            "ORASTEANU": "ORĂŞTEANU", "OROSAN": "OROŞAN", "PADURARIU": "PĂDURARIU",
                            "PALINCAS": "PALINCAŞ", "PASARE": "PASĂRE", "PASCA": "PAŞCA", "PASTORICI": "PASTORCICI",
                            "PATRAS": "PĂTRAŞ", "PATRAŞ": "PĂTRAŞ", "PATRAUS": "PĂTRĂUŞ", "PÂRLETEANU": "PÂRLEŢEANU",
                            "PĂRVULESCU": "PÂRVULESCU", "PETRASCU": "PETRAŞCU", "PETRISOR": "PETRIŞOR",
                            "PINTILEI": "PINTILIE", "PIRJOL": "PÂRJOL", "PIRVU": "PÂRVU", "PIRVULESCU": "PÂRVULESCU",
                            "PISLARU": "PÂSLARU", "PLACINTA": "PLĂCINTĂ", "PLACINTĂ": "PLĂCINTĂ", "POIANA": "POIANĂ",
                            "POLITEANU": "POLIŢEANU", "POMANA": "POMANĂ", "PREOEASA": "PREOTEASA",
                            "PREPELIŢA": "PREPELIŢĂ", "PRICINA": "PRICINĂ", "PUSCASIU": "PUŞCASIU",
                            "RAMASCANU": "RAMAŞCANU", "REGHINA": "REGHINĂ", "RETEZATU": "RETEZANU",
                            "RISNOVEANU": "RÂSNOVEANU", "ROMILA": "ROMILĂ", "ROS": "ROŞ", "ROSIORU": "ROŞIORU",
                            "ROSU": "ROŞU", "RUSAN": "RUŞAN", "SALAJAN": "SĂLĂJAN", "SALAPA": "ŞALAPA",
                            "SANDULESCU": "SĂNDULESCU", "SARB": "SÂRB", "SEBESAN": "SEBEŞAN", "SECARA": "SECARĂ",
                            "SECRETEANU": "SECREŢEANU", "SEGARCEANU": "SEGĂRCEANU", "SERBAN": "ŞERBAN",
                            "SERBANESCU": "ŞERBĂNESCU", "SIPOTEANU": "ŞIPOTEANU", "SIRBU": "SÂRBU",
                            "SMÂNTÂNA": "SMÂNTÂNĂ", "SPÂNACHE": "SPÂNOCHE", "SPRINCEANA": "SPRÂNCEANA",
                            "STANESCU": "STĂNESCU", "STANISOR": "STANIŞOR", "STĂNILA": "STĂNILĂ",
                            "SZIKSAY": "SZIKSZAY", "TANDARESCU": "ŢĂNDĂRESCU", "TANTĂU": "TANŢĂU",
                            "TĂMĂZLACARU": "TĂMĂZLĂCARU", "TÂLVAR": "TÂLVĂR", "TEAHA": "TEANA", "TIMISAN": "TIMIŞAN",
                            "TIŢA": "TIŢĂ", "TRAISTARU": "TRĂISTARU", "TRANCA": "TRANCĂ", "TRUTESCU": "TRUŢESCU",
                            "TUCA": "TUCĂ", "TULICA": "TULICĂ", "VACARUS": "VĂCĂRUŞ", "VADUVA": "VĂDUVA",
                            "VALEANU": "VĂLEANU", "VALVOI": "VÂLVOI", "VÂRGĂ": "VARGA", "VARTOPEANU": "VÂRTOPEANU",
                            "VATAVU": "VĂTAVU", "VATRA": "VATRĂ", "VÂNŞU": "VÂNŢU", "VEGHES": "VEGHEŞ",
                            "VERDES": "VERDEŞ", "VIJLOI": "VÂJLOI", "VILCU": "VÂLCU", "VILCELEANU": "VÂLCELEANU",
                            "VISAN": "VIŞAN", "ZBARCEA": "ZBÂRCEA", "ZGLIMBRA": "ZGLIMBEA", "AGAFITEI": "AGAFIŢEI",
                            "AILENE": "AILENEI", "AIONESE": "AIONESEI", "ALECXANDRU": "ALEXANDRU", "APETREI": "APETRI",
                            "ATUDOSIEI": "ATUDOSEI", "AXINTI": "AXÂNTI", "BADILĂ": "BĂDILĂ", "BADOI": "BĂDOI",
                            "BALAŞCA": "BALAŞCĂ", "BARAN": "BĂRAN", "BIRAU": "BIRĂU", "BLEOANCA": "BLEOANCĂ",
                            "BOROS": "BOROŞ", "BROASCA": "BROASCĂ", "BRUMA": "BRUMĂ", "BRĂNZICĂ": "BRÂNZICĂ",
                            "BURLIBASA": "BURLIBAŞA", "BANYAI": "BÁNYAI", "BIGIOI": "BÂGIOI", "BÂGOI": "BÂGIOI",
                            "BÂLBA": "BÂLBĂ", "BÂRSAŞTEANU": "BÂRSĂŞTEANU", "BÂRŞĂŞTEANU": "BÂRSĂŞTEANU",
                            "BĂDIŢA": "BĂDIŢĂ", "BALAN": "BĂLAN", "BARBULESCU": "BĂRBULESCU", "CALANCE": "CALANCEA",
                            "CALOTA": "CALOTĂ", "CAMENIŢA": "CAMENIŢĂ", "CATUNA": "CĂTUNA", "CHIRVASA": "CHIRVASĂ",
                            "CHIRVASE": "CHIRVASĂ", "CHIS": "CHIŞ", "CIORCAS": "CIORCAŞ", "CIOVIRNACHE": 'CIOVÂRNACHE',
                            "COVÂRNACHE": "CIOVÂRNACHE", "CIRLIG": "CÂRLIG", "CIRSTOIU": "CÂRSTOIU",
                            "COBISCAN": "COBÂSCAN", "COMÂSCAN": "COBÂSCAN", "COMSA": "COMŞA", "CORLĂŢENU": "CORLĂŢEANU",
                            "COTUTIU": "COTUŢIU", "CREMENITCHI": "CREMENIŢCHI", "CRETOIU": "CREŢOIU",
                            "CREŢANU": "CREŢEANU", "CRÂSMARU": "CRÂŞMARU", "CRPCIUN": "CRĂCIUN", "CARSTEA": "CÂRSTEA",
                            "CALIN": "CĂLIN", "CĂRSTESCU": "CÂRSTESCU", "DASCALU": "DASCĂLU", "DEACONU": "DIACONU",
                            "DOMNITEANU": "DOMNIŢEANU", "DOROBANTU": "DOROBANŢU", "DOTIU": "DOŢIU", "DRAGAN": 'DRĂGAN',
                            "DRAGHICI": "DRĂGHICI", "DUMITRASCU": 'DUMITRAŞCU', "DUSCCEAC": "DUSCEAC",
                            "DUTESCU": "DUŢESCU", "EROS": "ERÖS", "FARTATHY": 'FARMATHY', "FAT": "FĂT", "FIT": "FIŢ",
                            "FLORUT": "FLORUŢ", "FĂLĂMAS": "FĂLĂMAŞ", "GADICI": "GÂDICI", "GALESCU": "GĂLESCU",
                            "GARBACI": "GÂRBACI", "GASPAR": "GAŞPAR", "GAVRILA": "GAVRILĂ", "GIORGESCU": "GEORGESCU",
                            "GHEALDIR": "GHEALDÂR", "GRECUP": "GRECU", "GROZAVESCU": "GROZĂVESCU",
                            "VLADISLAU": 'VLADISLAV', "GURITĂMANOLE": "GURITĂ MANOLE", "GYORGY": "GYÖRGY",
                            "GĂLĂTAN": "GĂLĂŢAN", "GĂRCU": "GÂRCU", "HANCĂS": "HANCĂŞ", "HANCAS": "HANCĂŞ",
                            "HARALAMBE": "HARALAMBIE", "HATEGAN": "HAŢEGAN", "HEGYI": "HEGY", "HURDUCACI": "HURDUGACI",
                            "HELRGHELEGIU": "HERGHELEGIU", "HOALGA": "HOALGĂ", "HRITCU": "HRIŢCU", "HĂRĂBOR": "HĂRĂBOI",
                            "ILUT": "ILUŢ", "ILYES": "ILYÉS", "IORANESCU": "IORDANESCU", "IVANUŞCĂ": "IVĂNUŞCĂ",
                            "IVĂHIŞI": "IVĂNIŞI", "IVANIŞ": "IVĂNIŞ", "IVĂNUŞCA": 'IVĂNUŞCĂ', "JIRLĂEANU": "JÂRLĂEANU",
                            "KARDALUS": "KARDALUŞ", "KAZĂR": "LAZĂR", "KULCEAR": "KULCSAR", "LERESZTES": 'KERESZTES',
                            "LODOABA": "LODOABĂ", "LUSUŞAN": "LUDUŞAN", "MAGYORI": 'MAGYARI', "MAIREAN": "MAIEREAN",
                            "MANCAS": "MANCAŞ", "MANDROC": "MÂNDROC", "MANIGUŢIU": 'MĂNIGUŢIU', "MARGINA": "MARGINĂ",
                            "MEUCĂ": 'MEAUCĂ', "MIHALACGE": "MIHALACHE", "MIHAIESCU": 'MIHĂIESCU',
                            "MINDRUTIU": "MINDRUŢIU", "MITRANCA": 'MITRANCĂ', "MODILCĂ": 'MODÂLCĂ', "MOIS": "MOIŞ",
                            "MORMĂILĂ": "MORNĂILĂ", "MOROSANU": "MOROŞANU", "MOT": "MOŢ", "MOTIRLICHIE": "MOŢÂRLICHIE",
                            "MOTÂRLICHIE": "MOŢÂRLICHIE", "MOTĂŢEANU": "MOŢĂŢEANU", "MURESAN": "MUREŞAN",
                            "MAIEREAN": "MĂIEREAN", "NEACSU": "NEACŞU", "MAE": "NAE", "NISULESCU": "NIŞULESCU",
                            "NITOI": "NIŢOI", "NITULESCU": "NIŢULESCU", "NOVACESCU": "NOVĂCESCU", "OPRIŢA": "OPRIŢĂ",
                            "OSICECANU": "OSICEANU", "PANTELEEV": "PENTELEEV", "PANŢIRU": "PANŢÂRU",
                            "PARFENE": "PARFENIE", "PASTILA": 'PASTILĂ', "PAUN": 'PĂUN', "PESCĂRUS": "PESCĂRUŞ",
                            "PISMIS": "PISMIŞ", "POTANG": "POTÂNG", "PRICIN": "PRICINĂ", "PURCARIŢĂ": "PURCĂRIŢĂ",
                            "PUŞCA": "PUŞCĂ", "PUŞCASIU": "PUŞCAŞIU", "PUSCHIN": "PUŞCHIN", "PUTURA": "PUŢURA",
                            "PALTINEANU": "PĂLTINEANU", "PĂSCULEŢ": "PĂŞCULEŢ", "PUŞOU": "PUŞOIU", "RACEANU": "RĂCEANU",
                            "RADOCĂ": "RĂDOCĂ", "RAT": "RAŢ", "RUSTI": "RUŞTI", "RADULESCU": "RĂDULESCU",
                            "SABAU": "SABĂU", "SAICIUC": "SAUCIUC", "SCIUCHIN": 'ŞCIUCHIN', "SENDRESCU": "ŞENDRESCU",
                            "SFINTESCU": "SFINŢESCU", "SING": "SINGH", "SOFRANCA": "ŞOFRANCA", "SPOEALĂ": "SPOIEALĂ",
                            "SPRÂNCEANA": "SPRÂNCEANĂ", "SPATARU": "SPĂTARU", "STANILA": "STĂNILĂ",
                            "STANILĂ": "STĂNILĂ", "STEFAN": "ŞTEFAN", "STANCESCU": "STĂNCESCU",
                            "STANCULESCU": "STĂNCULESCU", "SUHANI": "ŞUHANI", "SZATMARI": "SZATMÁRI", "SZABO": "SZÁBO",
                            "SARBU": "SÂRBU", "SALAN": "SĂLAN", "TAGA": "ŢAGA", "TANASE": "TĂNASE", "TELBIS": 'TELBIŞ',
                            "TAPLIUC": "ŢAPLIUC", "LORENJA": "LORENA", "TATAR": "TĂTAR", "TAU": "ŢĂU",
                            "TIMOASCĂ": "TIMOAŞCĂ", "TINCA": 'TINCĂ', "TINEGHE": "ŢINEGHE", "TIRLEA": "ŢIRLEA",
                            "TOSA": "TOŞA", "TRUTA": "TRUŢĂ", "TRUŢA": "TRUŢĂ", "TUDURUŢA": "TUDURUŢĂ",
                            "TARLION": "TÂRLION", "TĂMĂSAN": 'TĂMĂŞAN', "TĂNĂSICA": "TĂNĂSICĂ", "TĂU": "ŢAU",
                            "TĂRNICERIU": "TĂRNICERU", "TARÂŢĂ": 'TĂRÂŢĂ', "VADANA": "VĂDANA", "VALS": "VALD",
                            "ALIXANDRI": "ALEXANDRI", "VINTEANU": "VITANU", "VIOIU": "VIŞOIU", "VOICILA": "VOICILĂ",
                            "VRINCEANU": "VRÂNCEANU", "VADEANU": "VĂDEANU", "VALAN": "VĂLAN", "VĂTZARU": "VĂRZARU",
                            "VARZARU": 'VĂRZARU', "VASONAN": "VĂSONAN", "ZETES": "ZETEŞ", "ZUGRAVEL": "ZUGRĂVEL",
                            "ÎMPARATU": 'ÎMPĂRATU', "ŞODINCA": "ŞODINCĂ", "SOLOVĂSTRU": "ŞOLOVĂSTRU",
                            "SORTAN": 'ŞORTAN', "ŞORÂNDARU": 'ŞORÂNDACU', "ŞTEFANESCU": "ŞTEFĂNESCU",
                            "STEFĂNIŢĂ": "ŞTEFĂNIŢĂ", "TAMBLAC": "ŢAMBLAC", "TARI": "ŢARI", "ŢIRLEA": 'ŢÂRLEA',
                            "ŢUIU": "TUIU", "ŢÂCŞA": "TÂCŞA", "TIPLEA": "ŢIPLEA", "ŢĂPURIN": "ŢAPURIN",
                            "TERMURE": "ŢERMURE", "CRETEANU": "CREŢEANU", "GIURCA": "GIURCĂ", "ILEASĂ": "ILIASĂ",
                            "IVĂNIŞI": "IVĂNIŞ", "LAZĂU": "LĂZĂU", "MIRĂUŢĂ": "MIRUŢĂ", "PATRA": "PATRĂ",
                            "RACLEA": "RÂCLEA", "ARMĂ": "ARAMĂ", "AVELOIE": "AVELOAIE", "BORDIANU": "BORDEIANU",
                            "COSMAN": "COŞMAN", "DOGARE": "DOGARU", "POPOESCU": "POPESCU"}
