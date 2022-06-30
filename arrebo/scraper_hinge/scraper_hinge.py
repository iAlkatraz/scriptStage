from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

driver = webdriver.Chrome()
driver.get("http://192.168.20.5:8089/iur/access.php?e=ARB")
driver.maximize_window()

WebDriverWait(driver, 60).until(EC.presence_of_element_located(
    (By.XPATH, '/html/body/div/div[2]/div/div[2]/div[2]/form/div[2]/div[3]/div[2]/input')))
WebDriverWait(driver, 60).until(EC.presence_of_element_located(
    (By.XPATH, '/html/body/div/div[2]/div/div[2]/div[2]/form/div[2]/div[4]/div[2]/input')))
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[2]/div[2]/form/div[2]/div[5]/div')))

username = driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/div[2]/form/div[2]/div[3]/div[2]/input')
username.send_keys("arb")

password = driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/div[2]/form/div[2]/div[4]/div[2]/input')
password.send_keys("ow3hx1bq")

login = driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/div[2]/form/div[2]/div[5]/div')
login.click()

WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div/div/table/tbody/tr[3]/td[1]')))
akron = driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[1]/div/div/table/tbody/tr[3]/td[1]')
akron.click()

sleep(2)

WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[2]/div/div/table/tbody/tr[3]/td[1]/img')))
status_view = driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/div/div/table/tbody/tr[3]/td[1]/img')
status_view.click()

WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[5]/div[2]/div[1]/img')))
download_csv = driver.find_element(By.XPATH, '/html/body/div/div[5]/div[2]/div[1]/img')
for i in range(4, 30):
    driver.find_element(By.XPATH,
                        '/html/body/div/div[5]/div[2]/div[2]/div[1]/div[1]/select/option[' + str(i) + ']').click()
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div/div[5]/div[2]/div[2]/div[2]/table/tbody')))
    actionChains = ActionChains(driver)
    actionChains.move_to_element(download_csv).click().perform()
driver.close()
