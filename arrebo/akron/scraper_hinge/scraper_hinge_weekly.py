import os
import yaml
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from merge_files import merge
from datetime import *

with open('conf.yml', 'r') as y:
    configuration = yaml.safe_load(y)
    y.close()

options = Options()
options.add_experimental_option("prefs", {
    "download.default_directory": os.path.abspath("./files")})
driver = webdriver.Chrome(options=options)
driver.get(configuration["URL"])
driver.maximize_window()

# attendo che i campi html username, password e il botton login siano caricati
WebDriverWait(driver, 60).until(EC.presence_of_element_located(
    (By.XPATH, configuration["XPATH_USERNAME"])))
WebDriverWait(driver, 60).until(EC.presence_of_element_located(
    (By.XPATH, configuration["XPATH_PASSWORD"])))
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, configuration["XPATH_LOGIN_BUTTON"])))

# scrivo lo username e la password e premo login
username = driver.find_element(By.XPATH, configuration["XPATH_USERNAME"])
username.send_keys(configuration["USERNAME"])
password = driver.find_element(By.XPATH, configuration["XPATH_PASSWORD"])
password.send_keys(configuration["PASSWORD"])
login = driver.find_element(By.XPATH, configuration["XPATH_LOGIN_BUTTON"])
login.click()

# attendo che il bottone di visualizzazione della macchina AKRON sia disponibile e lo clicco
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, configuration["XPATH_AKRON_BUTTON"])))
akron = driver.find_element(By.XPATH, configuration["XPATH_AKRON_BUTTON"])
akron.click()

sleep(2)  # serve per attendere che i dati siano caricati

# attendo che il bottone di visualizzazione del campo STATUS sia disponibile e lo clicco
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, configuration["XPATH_STATUS_BUTTON"])))
status_view = driver.find_element(By.XPATH, configuration["XPATH_STATUS_BUTTON"])
status_view.click()

# attendo che la select di cambio data sia disponibile
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, "/html/body/div/div[5]/div[2]/div[1]/select/option[5]")))
driver.find_element(By.XPATH, "/html/body/div/div[5]/div[2]/div[1]/select/option[5]").click()

# dopo aver selezionato l'opzione di custom date, attendo che la tabella si carichi
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, configuration["XPATH_TABLE_TBODY"])))

# setto data di inizio e fine
date_from = driver.find_element(By.XPATH, configuration["XPATH_DATE_FROM"])
date_to = driver.find_element(By.XPATH, configuration["XPATH_DATE_TO"])
enabled = False
while not enabled:
    if date_from.is_enabled() and date_to.is_enabled():
        enabled = True
update = driver.find_element(By.XPATH, configuration["XPATH_UPDATE_BUTTON"])
date_from.clear()
date_to.clear()
date_from_value = datetime.now().date()  # prendo la data atuale
date_to_value = date_from_value  # la imposto come data massima di destinazione
date_from_value -= timedelta(
    days=7)  # ci sottraggo 7 giorni in modo che il range sia da 7 giorni fa ad oggi (una settimana)
date_from.send_keys(date_from_value.strftime("%d-%m-%Y") + " 00:00:00")
date_to.send_keys(date_to_value.strftime("%d-%m-%Y") + " 23:59:59")
update.click()

# anche qui attendo che si carichi la tabella
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, configuration["XPATH_TABLE_TBODY"])))

# attendo che il bottone di download csv sia disponibile e dopodichè per ogni opzione della select (escluse le prime 3 che non servono)
# le clicco tutte e scarico i vari file di esportazione .csv
WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, configuration["XPATH_DOWNLOAD_CSV_BUTTON"])))
download_csv = driver.find_element(By.XPATH, configuration["XPATH_DOWNLOAD_CSV_BUTTON"])
for i in range(4, 33):
    driver.find_element(By.XPATH,
                        configuration["PARTIAL_XPATH_OPTION"] + str(i) + ']').click()
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, configuration["XPATH_TABLE_TBODY"])))
    actionChains = ActionChains(driver)
    actionChains.move_to_element(download_csv).click().perform()

# attendo che tutti i file siano scaricati
wait = True
while wait:
    wait = False
    files = os.listdir("./files")
    if configuration["FILES_NUMBER"] and len(files) != configuration["FILES_NUMBER"]:
        wait = True
    for file in files:
        if file.endswith('.csv'):
            wait = False
        else:
            wait = True
            break
driver.close()
driver.quit()
# chiamo la funzione mer mergiare i file scaricati
merge()
