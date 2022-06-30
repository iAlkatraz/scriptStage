import requests
from time import sleep
import json
import yaml
from datetime import *

with open('conf.yml', 'r') as y:
    configuration = yaml.safe_load(y)
    y.close()

#PROBLEMA: se si mette una finestra temporale di 5 minuti, non si ottengono dati
# ESEMPIO: se attualemente sono le 17:00:00, lo script cercherà dati nella finestra temporale quale
# 16:55:00 to 17:00:00. Ho riscontrato ieri però che la macchina non restituisce nulla perchè forse non ha ancora salvato nulla
# quindi bisogna definire una finestra temporale sensata... ho pensato a 10 minuti: in questo modo vengono sicuramente presi
# sempre i dati. In riferimento alla finestra temporale dell'esempio precedente, avremo quindi 16:50:00 to 17:00:00, e verranno sicuramente
# presi i dati dalle 16:55:00 alle 17:00:00. Quando saranno le 17:05:00, la finestra sarà 16:55:00 to 17:05:00, assicurando di prendere
# i dati dalle 16:55:00 alle 17:00:00

while True:
    # Inizializziamo a None
    event = None
    alarm = None
    try:
        start = datetime.now()
        stop = start
        start -= timedelta(minutes=10)

        print(start.strftime("%d/%m/%Y %H:%M:%S"))
        print(stop.strftime("%d/%m/%Y %H:%M:%S"))

        # richiesta di valori
        event_request = requests.post(url=configuration['event_address'], json={
            "Start": start.strftime("%d/%m/%Y %H:%M:%S"),
            "Stop": stop.strftime("%d/%m/%Y %H:%M:%S"),
            "Descr": 1
        })
        alarm_request = requests.get(configuration['alarm_address'])

        print("EVENT ---- " + event_request.text)
        print("ALARM ---- " + alarm_request.text)

        event = open("event" + ".txt", "a")  # apertura file
        print("Apertura file report.txt riuscita")
        alarm = open("alarm" + ".txt", "a")
        print("Apertura file alarm.txt riuscita")

        event_json = json.loads(event_request.text)  # creazione dei file json
        print("Creazione del json event_json riuscita")
        alarm_json = json.loads(alarm_request.text)
        print("Creazione del json alarm_json riuscita")

        event.write(str(event_json) + "\n")  # scrittura dei json su file
        print("Scrittura su file event.txt riuscita")
        alarm.write(str(alarm_json) + "\n")
        print("Scrittura su file alarm.txt riuscita")

    except Exception as e:
        print("ERRORE VERIFICATOSI")
        log = open("log" + ".txt", "a")
        print("Apertura del file log.txt riuscita")
        log.write(str(datetime.now()) + " - ERRORE -> " + str(e) + "\n")
        print("Scrittura del file log.txt riuscita")
        log.close()
        print("Chiusura del file log.txt riuscita")

    # se il crash avviene nell'apertura dei file in una delle sue variabili 'alarm' o 'report'
    # allora essi, essendo stati inizializzati a None, rimarranno a None: il controllo successivo
    # serve appunto per verificare questo: se sono a None, allora non li chiudiamo, evitando così un eventuale
    # ennesimo crash. Altrimenti li chiudiamo in quanto il crash potrebbe essersi verificato altrove.
    finally:
        if not (event is None):
            event.close()
            print("Chiusura del file event.txt riuscita")
        if not (alarm is None):
            alarm.close()
            print("Chiusura del file alarm.txt riuscita")

    sleep(configuration['interval'])
