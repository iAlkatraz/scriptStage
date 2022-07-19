# serve per appendere i file event.txt e alarm.txt quando vengono presi dal Pc del cliente
import os

event_file_from = open("../customers/arrebo/files/event.txt", 'r')
event_file_to = open("../customers/arrebo/event.txt", 'a', newline='')
event_file_to.writelines(event_file_from.readlines())
event_file_to.close()
event_file_from.close()
os.remove("../customers/arrebo/files/event.txt")
alarm_file_from = open("../customers/arrebo/files/alarm.txt", 'r')
alarm_file_to = open("../customers/arrebo/alarm.txt", 'a', newline='')
alarm_file_to.writelines(alarm_file_from.readlines())
alarm_file_to.close()
alarm_file_from.close()
os.remove("../customers/arrebo/files/alarm.txt")
