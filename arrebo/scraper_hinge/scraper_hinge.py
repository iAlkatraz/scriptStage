from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

driver = webdriver.Chrome()
driver.get("http://192.168.20.5:8089/iur/access.php?e=ARB")
driver.maximize_window()

# attendo che i campi html username, password e il botton login siano caricati
WebDriverWait(driver, 60).until(EC.presence_of_element_located(
    (By.XPATH, '/html/body/div/div[2]/div/div[2]/div[2]/form/div[2]/div[3]/div[2]/input')))
WebDriverWait(driver, 60).until(EC.presence_of_element_located(
    (By.XPATH, '/html/body/div/div[2]/div/div[2]/div[2]/form/div[2]/div[4]/div[2]/input')))
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[2]/div[2]/form/div[2]/div[5]/div')))

#scrivo lo username e la password e premo login
username = driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/div[2]/form/div[2]/div[3]/div[2]/input')
username.send_keys("arb")
password = driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/div[2]/form/div[2]/div[4]/div[2]/input')
password.send_keys("ow3hx1bq")
login = driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/div[2]/form/div[2]/div[5]/div')
login.click()

# attendo che il bottone di visualizzazione della macchina AKRON sia disponibile e lo clicco
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div/div/table/tbody/tr[3]/td[1]')))
akron = driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[1]/div/div/table/tbody/tr[3]/td[1]')
akron.click()

sleep(2)# serve per attendere che i dati siano caricati

# attendo che il bottone di visualizzazione del campo STATUS sia disponibile e lo clicco
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[2]/div/div/table/tbody/tr[3]/td[1]/img')))
status_view = driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/div/div/table/tbody/tr[3]/td[1]/img')
status_view.click()

# attendo che la select sia disponibile e dopodichè per ogni opzione (escluse le prime 3 che non servono)
# le clicco tutte e scarico i vari file di esportazione .csv
WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[5]/div[2]/div[1]/img')))
download_csv = driver.find_element(By.XPATH, '/html/body/div/div[5]/div[2]/div[1]/img')
for i in range(4, 33):
    driver.find_element(By.XPATH,
                        '/html/body/div/div[5]/div[2]/div[2]/div[1]/div[1]/select/option[' + str(i) + ']').click()
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div/div[5]/div[2]/div[2]/div[2]/table/tbody')))
    actionChains = ActionChains(driver)
    actionChains.move_to_element(download_csv).click().perform()
    #TODO: mettere controllo di attesa di terminazione di tutti i download pendenti
    #TODO: aggiungere spostamento file dalla cartella download alla cartella /files del modulo "merge_files" e lanciare la sua esecuzione
    #TODO: verificare se si può impostare una cartella di download differente da quella di default