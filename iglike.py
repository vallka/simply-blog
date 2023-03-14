import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

class SelDriver():
  def __init__(self,dbg=False):
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    if dbg:
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    #Change chrome driver path accordingly
    chrome_driver = "chromedriver.exe"
    self.driver = webdriver.Chrome(chrome_driver, options=chrome_options)
    print (self.driver)
    self.driver.implicitly_wait(1)
    self.vars = {}

driver=SelDriver(True)

to_like =500
liked=0
for i in range(2001):
    
    ilikes = 100
    sleep = 1

    try:
        likes = driver.driver.find_elements(By.XPATH,"//*[contains(text(), 'likes')]")[0].text
        if likes:
            ilikes = int(likes.split()[0])
        elif driver.driver.find_elements(By.XPATH,"//*[contains(text(), '1 like')]") and driver.driver.find_elements(By.XPATH,"//*[contains(text(), '1 like')]")[0].text:
            ilikes = 1
        elif driver.driver.find_elements(By.XPATH,"//*[contains(text(), 'Be the first')]") and driver.driver.find_elements(By.XPATH,"//*[contains(text(), 'Be the first')]")[0].text:
            ilikes = 1

        if ilikes<30:
            liked = liked+1
            driver.driver.find_elements(By.CSS_SELECTOR,'._abl-')[3].click()
            sleep = random.randint(2,120)

        print(i,liked,'waiting:',sleep)
        time.sleep(sleep)
    except:

        None    

    if liked>=to_like:
        break    

    driver.driver.find_elements(By.CSS_SELECTOR,'._abl-')[1].click()
    time.sleep(1)

