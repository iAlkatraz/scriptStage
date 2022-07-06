import json

import pandas as pd


def contains_emergency(items):
    for key, value in items:
        if type(value) == str and "EMERGENCY" in value.split(" ")[0]:
            return True
    return False


def get_emergency():
    file = open("event.txt", "r")
    prev = None  # questa variabile serve per vitare di prendere in considerazioni più volte lo stesso dizionario
    emergenze = dict()
    # in quanto nei dati a volte duplicati dei dati; evitiamo quindi ridonanza
    for line in file.readlines():
        json_obj = json.loads(line.replace("'", '"'))
        lista = json_obj[
            "elementiStatistica"]  # qui prendo tutti gli elementi della lista; ogni elemento è un dizionario
        for i in range(len(lista)):
            if prev is None:  # se è a None, vuol dire che è la prima iterazione, quindi semplicemente non facciamo nulla
                prev = dict(lista[i])
                if contains_emergency(lista[i].items()):
                    for key, value in lista[i].items():
                        if key == "B":
                            if value in emergenze:
                                emergenze[value] += 1
                            else:
                                emergenze[value] = 1
                            print(value)
            else:  # altrimenti controlliamo di anon aver già avuto sto dizionario nell'iterazione precedente (tanto sono ordinati già per ora i dati)
                if not prev == lista[i]:
                    if contains_emergency(lista[i].items()):
                        for key, value in lista[i].items():
                            if key == "B":
                                if value in emergenze:
                                    emergenze[value] += 1
                                else:
                                    emergenze[value] = 1
                    prev = dict(lista[i])
                else:
                    prev = dict(lista[i])
    print("--- EMERGENZE CHE ABBIAMO ---")
    for key, value in emergenze.items():
        emergency = ""
        for el in key.split(
                " "):  # sta roba serve perche alcune stringe sono ripostate come " ciaooo   ", quidi per pulirle e ottenere solo "ciao" si fa questo
            if not el == " " and not el == "":
                if emergency == "":
                    emergency += el
                else:
                    emergency += " " + el
        print(emergency + " -> " + str(value))


get_emergency()
