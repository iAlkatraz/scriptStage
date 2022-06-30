import time
from os import listdir
from os.path import isfile
from os.path import join

from dateutil.parser import parse


def get_correct_name(file):
    splits = file.split(".")[0].split("_")
    name = ""
    first = True
    for el in splits:
        if len(el) == 1:
            name += '_' + el
        else:
            try:
                parse(el)
            except:
                try:
                    time.strptime(el, '%H-%M-%S')
                except:
                    if first:
                        name += el
                        first = False
                    else:
                        name += "_" + el
    name += ".csv"
    return name


files = [f for f in listdir("./files") if isfile(join("./files", f))]
for f in files:
    file_from = open("./files/" + f, 'r')
    lines = file_from.readlines()
    file_to_name = get_correct_name(f)
    file_to = open("./merged/" + file_to_name, 'a')
    first = True
    for line in lines:
        if first:
            first = False
        else:
            file_to.write(line)
