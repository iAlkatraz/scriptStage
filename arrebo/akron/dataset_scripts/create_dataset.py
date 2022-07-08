import datetime
import json
import os
from os import listdir
from os.path import isfile, join
import csv
import pandas as pd


# funzione per leggere ogni json del file event.txt e scrivere un file event_temp.txt in cui ci sono tutte le righe dei vari json
def create_event_temp():
    event_file = open("event.txt", "r")
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


# TODO: modificare in modo che faccia un confronto con il file alarm.txt e verifchi che se in emergenza e warning allora mettere come descrizione dispositivo di emergenza inserito
# funzione per leggere dal file event.txt e creare un file emergencies.txt che contiene solo EMERGENCY e END OF EMERGENCY
def get_only_emergencies():
    event_file = open("event.txt", "r")
    dizionario = dict()
    with open("emergencies.txt", "a") as emergencies_file:
        for line in event_file.readlines():
            json_obj = json.loads(line.replace("'", '"'))
            lista = json_obj["elementiStatistica"]
            for el in lista:
                if "EMERGENCY" in str(el):
                    if str(el) not in dizionario:
                        dizionario[str(el)] = 1
                        emergencies_file.write(str(el) + "\n")
        event_file.close()
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
            if json_obj[
                "B"].strip() == "(VC1E07)":  # nel file alarm, se c'è warning a 1 ed emergenza a 1, e nel corrispettivo file event, l'emergenza è (VC1E07), allora l'emergenza in realtà è dispositivo di emergenza inserito (funghi)
                if "Dispositivo di emergenza inserito (GE0E16)" in emergencies:
                    emergencies["Dispositivo di emergenza inserito (GE0E16)"].append(
                        (json_obj["Date"], get_end_emergency(json_obj["Date"])))
                else:
                    emergencies["Dispositivo di emergenza inserito (GE0E16)"] = list()
                    emergencies["Dispositivo di emergenza inserito (GE0E16)"].append(
                        (json_obj["Date"], get_end_emergency(json_obj["Date"])))
            else:
                if json_obj["B"].strip() in emergencies:
                    emergencies[json_obj["B"].strip()].append((json_obj["Date"], get_end_emergency(json_obj["Date"])))
                else:
                    emergencies[json_obj["B"].strip()] = list()
                    emergencies[json_obj["B"].strip()].append((json_obj["Date"], get_end_emergency(json_obj["Date"])))
    return emergencies


def create_dataset():
    files = [f for f in listdir("../scraper_hinge/merged") if
             isfile(join("../scraper_hinge/merged", f))]  # file da cui prendere i dati
    with open("../dataset_scripts/dataset_hinge.csv", 'a', newline='') as dataset:  # apro il file dataset
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
                    "../scraper_hinge/merged/" + file))  # mi creo una lista di tutti i file da cui leggere in modo da averli gia aperti pronti
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
    dataset = pd.read_csv("dataset_hinge.csv")
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
    dataset.to_csv("dataset_hinge.csv", index=False)


try:
    os.remove("emergencies.txt")
except:
    print("emergencies.txt does not exist")
try:
    os.remove("event_temp.txt")
except:
    print("event_temp.txt does not exist")
try:
    os.remove("dataset_hinge.csv")
except:
    print("dataset_hinge.csv does not exist")
create_event_temp()
get_only_emergencies()
create_dataset()
