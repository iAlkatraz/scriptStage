import csv
import sqlite3
import pandas as pd
import json
from tkinter import Tk
from tkinter.filedialog import askopenfilename

Tk().withdraw()
filename = askopenfilename()

directory, db_name = '/'.join(filename.split("/")[0:-1]) + "/", filename.split("/")[len(filename.split("/")) - 1]
file_name = directory + "dataset_" + '_'.join(db_name.split("_")[0:-1]) + ".csv"
db_name = directory + db_name

con = sqlite3.connect(db_name)
cur = con.cursor()

data = cur.execute("SELECT TIMESTAMP, datas from machine_datas")
first = True

with open(file_name, 'w', newline='') as out_file:
    csv_writer = csv.writer(out_file)
    for res in data:
        json_object = json.loads(res[1].replace("'", "\""))
        if first:
            header = json_object.keys()
            csv_writer.writerow(header)
            first = False
        row = list()
        for value in json_object.values():
            row.append(value)
        csv_writer.writerow(row)
out_file.close()
dataset = pd.read_csv(file_name)
data = cur.execute("SELECT TIMESTAMP, datas from machine_datas")
times = [time[0] for time in data]
dataset.insert(loc=0, column="TIME_STAMP", value=times)
dataset["TOOL"].fillna("NONE", inplace=True)
dataset.to_csv(file_name, index=False)
