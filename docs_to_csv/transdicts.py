"""
Translation dictionaries for various spelling/diacritic issues.
"""

court_names = {"ALSED": "ALEŞD", "TÎRGU": "TÂRGU", "TĂRGU": "TÂRGU", "STEHAIA": "STREHAIA", "PITESTI": "PITEŞTI",
               "HÎRLĂU": "HÂRLĂU", "CAMPULUNG": "CÂMPULUNG", "VÎNJU": "VÂNJU", "RM  VALCEA": "RÂMNICU VÂLCEA",
               "COMERCIAL": "COMERC./SPECIAL.", "SPECIALIZAT": "COMERC./SPECIAL.", "BALCESTI": "BĂLCEŞTI",
               "BÎRLAD": "BÂRLAD", "COSTESTI": "COSTEŞTI", "ARGES": "ARGEŞ", "DRAGASANI": "DRĂGĂŞANI",
               "SÎNNICOLAU": "SÂNNICOLAU", "ŞOMCUTA": "ŞOMCUŢA", "VALCEA": "VÂLCEA"}

parquet_names = {"BRASOV": "BRAŞOV", "BUCUREŞTI": "BUCUREŞTI", "CONSTANTA": "CONSTANŢA", "PITESTI": "PITEŞTI",
                 "PLOIESTI": "PLOIEŞTI", "CAMPULUNG": "CÂMPULUNG", "VÎNJU": "VÂNJU", "RM  VALCEA": "RÂMNICU VÂLCEA",
                 "COMERCIAL": "COMERC./SPECIAL.", "SPECIALIZAT": "COMERC./SPECIAL.", "TG MURES": "TÂRGU MUREŞ",
                 "LEHLIU GARA": "LEHLIU GARĂ", "ODORHEIUL": "ODORHEIU", "ROSIORI": "ROŞIORI", "TÎRGU": "TÂRGU",
                 "TARGU": "TÂRGU", "IALOMITA": "IALOMIŢA", "ÎALTA": "ÎNALTA", "SÎNNICOLAU": "SÂNNICOLAU",
                 "TG BUJOR": "TÂRGU BUJOR", "LAPUS": "LĂPUŞ", "SECTORULUI CINCI BUCUREŞTI": "SECTORULUI CINCI",
                 "SECTORULUI DOI BUCUREŞTI": "SECTORULUI DOI", "SECTORULUI PATRU BUCUREŞTI": "SECTORULUI PATRU",
                 "SECTORULUI TREI BUCUREŞTI": "SECTORULUI TREI", "SECTORULUI UNU BUCUREŞTI": "SECTORULUI UNU",
                 "SECTORULUI ŞASE BUCUREŞTI": "SECTORULUI ŞASE", "SFANTU": "SFÂNTU", "ŞOMCUTA": "ŞOMCUŢA",
                 "JUDECĂTORIAVIŞEU": "JUDECĂTORIA VIŞEU", "TRIBUNALULBRAŞOV": "TRIBUNALUL BRAŞOV",
                 "TIMISOARA": "TIMIŞOARA", "HĂRŞOVA": "HÂRŞOVA", "CALARASI": "CĂLĂRAŞI",
                 "CÎMPENI": "CÂMPENI", "FAGARAS": "FĂGĂRAŞ", "INTORSURA BUZAULUI": "ÎNTORSURA BUZĂULUI",
                 "JUGOJ": "LUGOJ", "ZARNESTI": "ZĂRNEŞTI", "TRIBUNLAUL": "TRIBUNALUL"}

court_sectors_buc = {"LUI 1": "LUI UNU", "LUI 2": "LUI DOI", "LUI 3": "LUI TREI", "LUI 4": "LUI PATRU",
                     "LUI 5": "LUI CINCI", "LUI 6": "LUI ŞASE",
                     'RAZA TRIBUNALUL BISTRI': 'RAZA TRIBUNALULUI BISTRI'}

parquet_sectors_buc = {"PARCHETUL DE PE LÂNGĂ  ": '', "TOR 1": "TORULUI UNU", "TOR 2": "TORULUI DOI",
                       "TOR 4": "TORULUI PATRU", "TOR 3": "TORULUI TREI", "TOR 5": "TORULUI CINCI",
                       "TOR 6": "TORULUI ŞASE"}

given_name_mistakes = {"AMCA": "ANCA", "AMDREEA": "ANDREEA", "ANGELAA": "ANGELA", "CODRŢA": "CODRUŢA",
                       "CRIASTIANA": "CRISTIANA", "CRSITINA": "CRISTINA", "DANDU": "SANDU",
                       "DÎNZIANA": "SÎNZIANA", "ELRNA": "ELENA", "GENONEVA": "GENOVEVA", "GEORGICA": "GEORGICĂ",
                       "GHEORGEH": "GHEORGHE", "CIRNELIU": "CORNELIU", "IUNUŢ": "IONUŢ", "IYABELA": "ISABELA",
                       "LUARA": "LAURA", "MANUEMA": "MANUELA", "MARINENA": "MARINELA", "MRCEA": "MIRCEA",
                       "NICUŢOR": "NICUŞOR", "NILOLETA": "NICOLETA", "ORSALYA": "ORSOLYA", "OTILEA": "OTILIA",
                       "OTILIEA": "OTILIA", "PRTRONELA": "PETRONELA", "ROXAN": "ROXANA", "ROYALIA": "ROZALIA",
                       "VIRGINEI": "VIRGINEL", "C TIN": "CONSTANTIN", "D TRU": "DUMITRU",
                       "MIHAELAIULIANA": "MIHAELA IULIANA", "GHEORGHW": "GHEORGHE", "VAENTIN": "VALENTIN",
                       "CĂTĂLI N": "CĂTĂLIN", "RONELA": "RONELLA", "ITILIA": "OTILIA", "ANC A": "ANCA",
                       "INSPECTOR CSM": '', "R?ZVAN": "RĂZVAN", "LUMINI?A": "LUMINIŢA", "CONSTAN?A": "CONSTANŢA"}

given_name_diacritics = {"ADELUTA": "ADELUŢA", "ANCUTA": "ANCUŢA", "ANISOARA": "ANIŞOARA", "ANUTA": "ANUŢA",
                         "AURAS": "AURAŞ", "BRANDUSA": "BRÂNDUŞA", "BRANDUŞA": "BRÂNDUŞA", "BRINDUSA": "BRÂNDUŞA",
                         "BRÎNDUŞA": "BRÂNDUŞA", "CALIN": "CĂLIN", "CATALIN": "CĂTĂLIN", "CLOPOTEL": "CLOPOŢEL",
                         "CONSTANTA": "CONSTANŢA", "COSTICA": "COSTICĂ", "CRACIUN": "CRĂCIUN",
                         "CRENGUTA": "CRENGUŢA", "DANTES": "DANTEŞ", "DANUT": "DĂNUŢ", "DANUŢ": "DĂNUŢ",
                         "DOINITA": "DOINIŢA", "DRAGOS": "DRAGOŞ", "DĂNUT": "DĂNUŢ", "FANEL": "FĂNEL",
                         "CAMPEANA": "CÂMPEANA", "CÎMPEANA": "CÂMPEANA", "FLORIŢA": "FLORIŢĂ",
                         "GHEORGITA": "GHEORGIŢĂ",
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
                         "TANTA": "TANŢA", "VALERICA": "VALERICĂ", "VLADUT": "VLĂDUŢ", "ZOITA": "ZOIŢA"}
