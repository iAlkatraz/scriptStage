import time
from os import listdir
from os.path import isfile
from os.path import join
from os import remove

from dateutil.parser import parse


# metodo per l'ottenimento del nome del file
# dato che la hinge esporta i dati su file .csv chiamati ad esempio
# STATUS_2022-10-10_17-23-00.csv, ovvero NOME_DATA_ORA, a noi serve il nome "pulito", cioè solo STATUS.csv
# alcuni file hanno nomi come TEMP_PHON_1_DATA_ORA. Quel "1" fa parte del nome pulito: il metodo gestisce anche quello
def get_correct_name(file):
    splits = file.split(".")[0].split("_")
    name = ""
    first = True  # flag di prima iterazione
    for el in splits:
        if len(el) == 1:
            name += '_' + el
        else:
            try:
                parse(el)  # verifichiamo se è una data, così da scartarla
            except:
                try:
                    time.strptime(el, '%H-%M-%S')  # verifichiamo se è un'orario, così da scartarla
                except:
                    if first:  # se è la prima iterazione, allora non dobbiamo considerare "_" come divisore
                        name += el
                        first = False
                    else:
                        name += "_" + el
    name += ".csv"
    return name


files = [f for f in listdir("./files") if isfile(join("./files", f))]  # file da cui prendere i dati
for f in files:
    file_from = open("./files/" + f, 'r')
    lines = file_from.readlines()
    file_to_name = get_correct_name(f)
    file_to = open("./merged/" + file_to_name, 'a')  # file a cui appendere i dati
    first = True
    for line in lines:
        if first:
            first = False
        else:
            file_to.write(line)
    file_from.close()
    file_to.close()
    remove(join("./files", f))
