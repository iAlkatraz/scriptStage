import datetime
import json
import os
from os import listdir
from os.path import isfile, join
import csv
import pandas as pd
import yaml

CONF_PATH = "../customers/conf_files"


# funzione per leggere ogni json del file event.txt e scrivere un file event_temp.txt in cui ci sono tutte le righe dei vari json
def create_event_temp(configuration):
    event_file = open(configuration["CUSTOMER_PATH"] + "/event.txt", "r")
    dizionario = dict()
    with open("event_temp.txt", "a") as event_temp_file:
        for line in event_file.readlines():
            json_obj = json.loads(line.replace("'", '"'))
            lista = json_obj["elementiStatistica"]
            for el in lista:
                if str(el) not in dizionario:
                    dizionario[str(el)] = 1
                    event_temp_file.write(str(el) + "\n")
        event_file.close()
        event_temp_file.close()


# funzione per leggere dal file event.txt e creare un file emergencies.txt che contiene solo EMERGENCY e END OF EMERGENCY
def get_only_emergencies(configuration):
    event_file = open(configuration["CUSTOMER_PATH"] + "/event.txt", "r")
    alarm_file = open(configuration["CUSTOMER_PATH"] + "/alarm.txt", "r")
    dizionario = dict()
    with open("emergencies.txt", "a") as emergencies_file:
        event_lines = event_file.readlines()
        alarm_lines = alarm_file.readlines()
        for i in range(len(event_lines)):
            event_json = json.loads(event_lines[i].replace("'", '"'))
            alarm_json = json.loads(alarm_lines[i].replace("'", '"'))
            lista = event_json["elementiStatistica"]
            for el in lista:
                if "EMERGENCY" in str(el):
                    if alarm_json["stato_allarme"] == 1 and alarm_json["stato_warning"] == 1 and el[
                        "B"].strip() == "(VC1E07)":
                        el["B"] = "Dispositivo di emergenza inserito (GE0E16)"
                    if alarm_json["stato_allarme"] == 0 and alarm_json["stato_warning"] == 1 and el[
                        "B"].strip() == "(VC1E07)" and "GE0E16" in alarm_json["testo_aux"]:
                        el["B"] = "Dispositivo di emergenza inserito (GE0E16)"
                    if str(el) not in dizionario:
                        dizionario[str(el)] = 1
                        emergencies_file.write(str(el) + "\n")
        event_file.close()
        alarm_file.close()
        emergencies_file.close()


# funzione per ottenere la END OF EMERGENCY dato un EMERGENCY
def get_end_emergency(start):
    start = datetime.datetime.strptime(start, "%d/%m/%Y %H:%M:%S")
    file = open("emergencies.txt", 'r')
    for line in file.readlines():
        json_obj = json.loads(line.replace("\n", "").replace("'", '"'))
        if json_obj["Descr"].strip() == "END OF EMERGENCY":
            end = datetime.datetime.strptime(json_obj["Date"], "%d/%m/%Y %H:%M:%S")
            if start.date() == end.date():
                if start.time() < end.time():
                    return end.strftime("%d/%m/%Y %H:%M:%S")


# funzione per creare un dizionario key -> value
# in cui le key sono le DESCRIZIONI DELLE EMERGENZE
# value è una lista di coppie (start, end) in cui
# start è la data inizio dell'emergenza (EMERGENCY)
# end è la data fine di emergenza (END OF EMERGENCY)
def get_emergencies():
    emergencies = dict()
    file = open("emergencies.txt", "r")
    for line in file.readlines():
        json_obj = json.loads(line.replace("\n", "").replace("'", '"'))
        if json_obj["Descr"].strip() == "EMERGENCY":
            if json_obj["B"].strip() in emergencies:
                emergencies[json_obj["B"].strip()].append((json_obj["Date"], get_end_emergency(json_obj["Date"])))
            else:
                emergencies[json_obj["B"].strip()] = list()
                emergencies[json_obj["B"].strip()].append((json_obj["Date"], get_end_emergency(json_obj["Date"])))
    return emergencies


def create_dataset(configuration):
    files = [f for f in listdir(configuration["MERGED_PATH"]) if
             isfile(join(configuration["MERGED_PATH"], f))]  # file da cui prendere i dati
    with open(configuration["CUSTOMER_PATH"] + "/dataset_akron.csv", 'a',
              newline='') as dataset:  # apro il file dataset
        header = ["TIME_STAMP"]
        writer = csv.writer(dataset)
        files_open = []
        for file in files:
            if file.split(".")[0] not in ["STATUS", "TEMP_AFS_PHON_1", "TEMP_ARIA_AFS", "TEMP_BOX_AFS",
                                          "TEMP_FUSORE_PHON_1", "TEMP_FUSORE_PHON_2", "TEMP_PANNELLO",
                                          "TEMP_PREFUSORE_EVA", "TEMP_PREFUSORE_GPOD", "TEMP_PREFUSORE_TM20",
                                          "TEMP_TUBO_CONVOGLIATORE", "TEMP_TUBO_GPOD", "TEMP_UGELLO_AFS"]:
                header.append(file.split(".")[0])  # creo l'header
                files_open.append(pd.read_csv(
                    configuration[
                        "MERGED_PATH"] + '/' + file))  # mi creo una lista di tutti i file da cui leggere in modo da averli gia aperti pronti
        writer.writerow(header)
        for i in range(len(files_open[0])):
            row = list()
            for file in files_open:
                if len(row) == 0:  # solo la prima volta devo mettere il timestamp (tanto è uguale per tutti)
                    row.append(file["board time"][i])
                    row.append(file["value"][i])
                else:
                    row.append(file["value"][i])
            writer.writerow(row)
    dataset.close()
    emergencies = get_emergencies()
    dataset = pd.read_csv(configuration["CUSTOMER_PATH"] + "/dataset_akron.csv")
    dataset.insert(6, "ST_MACH_EMERG_DESC", '')
    for index, row in dataset.iterrows():
        if row["ST_MACH_EMERG"] == 1:
            timestamp_data = datetime.datetime.strptime(row["TIME_STAMP"].split(".")[0], "%Y-%m-%d %H:%M:%S")
            trovato = False
            for (emergency, lista_tuple) in emergencies.items():
                for (start, end) in lista_tuple:
                    emergency_start = datetime.datetime.strptime(start, "%d/%m/%Y %H:%M:%S")
                    if end is not None:
                        emergency_end = datetime.datetime.strptime(end, "%d/%m/%Y %H:%M:%S")
                    else:
                        emergency_end = datetime.datetime.strptime(start, "%d/%m/%Y %H:%M:%S")
                        emergency_end = emergency_end.replace(hour=23, minute=59, second=59)
                    if emergency_start.date() == timestamp_data.date():
                        if emergency_start.time() <= timestamp_data.time() <= emergency_end.time():
                            trovato = True
                            if dataset.at[index, "ST_MACH_EMERG_DESC"] == '':
                                dataset.at[index, "ST_MACH_EMERG_DESC"] = emergency
                            else:
                                dataset.at[index, "ST_MACH_EMERG_DESC"] = dataset.at[
                                                                              index, "ST_MACH_EMERG_DESC"] + ", " + emergency
            if not trovato:
                dataset.at[index, "ST_MACH_EMERG_DESC"] = "Dispositivo di emergenza inserito (GE0E16)"
        else:
            dataset.at[index, "ST_MACH_EMERG_DESC"] = "NO EMERGENCY"
    dataset.drop("ST_MACH_EMERG", axis=1, inplace=True)
    dataset.to_csv(configuration["CUSTOMER_PATH"] + "/dataset_akron.csv", index=False)
    os.remove("emergencies.txt")
    os.remove("event_temp.txt")


files = [f for f in os.listdir(CONF_PATH) if isfile(join(CONF_PATH, f))]
for i in range(len(files)):
    print(str(i) + " - " + files[i])
conf_file = int(input("Inserisci scelta: "))
while conf_file not in range(len(files)):
    conf_file = input("Scelta errata. Reinserire: ")
with open(CONF_PATH + '/' + files[conf_file], 'r') as y:
    configuration = yaml.safe_load(y)
    y.close()
try:
    os.remove("emergencies.txt")
except:
    print("emergencies.txt does not exist")
try:
    os.remove("event_temp.txt")
except:
    print("event_temp.txt does not exist")
try:
    os.remove(configuration["CUSTOMER_PATH"] + "/dataset_akron.csv")
except:
    print("dataset_akron.csv does not exist")
create_event_temp(configuration)
get_only_emergencies(configuration)
create_dataset(configuration)
