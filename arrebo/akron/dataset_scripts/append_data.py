import csv
from os import listdir
from os.path import isfile, join

import pandas as pd

files = [f for f in listdir("../scraper_hinge/merged") if
         isfile(join("../scraper_hinge/merged", f))]  # file da cui prendere i dati
with open("../dataset_scripts/dataset_hinge.csv", 'a', newline='') as dataset:
    writer = csv.writer(dataset)
    files_open = []
    for file in files:
        files_open.append(pd.read_csv(
            "../scraper_hinge/merged/" + file))  # mi creo una lista di tutti i file da cui leggere in modo da averli gia aperti pronti
    for i in range(len(files_open[0])):
        row = list()
        first = True
        for file in files_open:
            if first:  # solo la prima volta devo mettere il timestamp (tanto è uguale per tutti)
                row.append(file["board time"][i])
                row.append(file["value"][i])
                first = False
            else:
                row.append(file["value"][i])
        writer.writerow(row)
    dataset.close()
    # TODO: aggiungere eliminazione dei file da merged
